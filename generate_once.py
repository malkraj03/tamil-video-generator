"""
Generate Once - full pipeline: topic -> research -> script -> screenplay ->
TTS -> visuals -> video -> thumbnail -> QC -> YouTube upload.

Designed for CI/CD (GitHub Actions). Runs once, produces one video.

Usage:
    python generate_once.py
    python generate_once.py --skip-upload     # skip YouTube
    python generate_once.py --resolution 1280x720 --fps 24
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pipeline")


def run_pipeline(skip_upload: bool = False, resolution: str = "1920x1080",
                 fps: int = 30) -> dict:
    """Execute the complete video-generation pipeline."""

    result = {
        "success": False, "video_path": None, "video_id": None,
        "title": None, "error": None,
    }
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # ── override resolution/fps if requested ─────────────
        import config
        w, h = map(int, resolution.split("x"))
        config.VIDEO_WIDTH = w
        config.VIDEO_HEIGHT = h
        config.VIDEO_FPS = fps

        # ── STEP 1: Topic ────────────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 1: Generating topic via Gemini...")
        logger.info("=" * 60)

        from gemini_engine import GeminiEngine
        gemini = GeminiEngine()
        topic_data = gemini.generate_topic()
        logger.info(f"Topic: {topic_data['topic']}")
        logger.info(f"Category: {topic_data['category']}")
        logger.info(f"Angle: {topic_data.get('angle', '')}")

        # ── STEP 2: Script ───────────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 2: Generating Tamil script...")
        logger.info("=" * 60)

        script = gemini.generate_script(topic_data)
        logger.info(f"Script length: {len(script)} chars, ~{len(script.split())} words")

        # ── STEP 3: Screenplay ───────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 3: Building screenplay...")
        logger.info("=" * 60)

        from screenplay_engine import build_screenplay
        scenes = build_screenplay(script)
        for sc in scenes:
            logger.info(f"  [{sc['section']}] {len(sc['sentences'])} sentences")

        # ── STEP 4: Image search queries ─────────────────────
        logger.info("=" * 60)
        logger.info("STEP 4: Generating image search queries...")
        logger.info("=" * 60)

        queries = gemini.generate_scene_queries(scenes)
        # Ensure we have at least one query per scene
        while len(queries) < len(scenes):
            queries.append(topic_data.get("image_queries", ["Tamil Nadu"])[0])

        # ── STEP 5: Fetch images ─────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 5: Fetching stock images...")
        logger.info("=" * 60)

        from visual_engine import fetch_scene_images
        scene_images = fetch_scene_images(queries, width=w, height=h)
        logger.info(f"Fetched {len(scene_images)} images")

        # ── STEP 6: TTS ──────────────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 6: Generating Tamil narration audio...")
        logger.info("=" * 60)

        from tts_engine import TTSEngine
        tts = TTSEngine()
        sentence_audios = tts.generate_scene_audio(scenes, run_id)
        combined_audio = tts.combine_audio(sentence_audios, run_id)
        total_audio_dur = sum(sa.duration_s for sa in sentence_audios)
        logger.info(f"Total narration: {total_audio_dur:.1f}s ({total_audio_dur/60:.1f} min)")

        # ── STEP 7: Video composition ────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 7: Composing video...")
        logger.info("=" * 60)

        from video_engine import VideoEngine
        video_eng = VideoEngine()
        video_path = video_eng.compose(
            sentence_audios=sentence_audios,
            scene_images=scene_images,
            scenes=scenes,
            title=topic_data["topic"],
            run_id=run_id,
        )
        result["video_path"] = str(video_path)

        # ── STEP 8: Metadata ────────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 8: Generating YouTube metadata...")
        logger.info("=" * 60)

        metadata = gemini.generate_metadata(topic_data, script)
        title = metadata.get("title", topic_data["topic"])
        description = metadata.get("description", "")
        tags = metadata.get("tags", [])
        result["title"] = title
        logger.info(f"Title: {title}")

        # ── STEP 9: Thumbnail ────────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 9: Generating thumbnail...")
        logger.info("=" * 60)

        from thumbnail_engine import generate_thumbnail
        thumb_text = metadata.get("thumbnail_text", metadata.get("tamil_title", title))
        thumb_path = generate_thumbnail(thumb_text, scene_images, run_id)

        # ── STEP 10: Quality Control ─────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 10: Running quality checks...")
        logger.info("=" * 60)

        from quality_control import run_qc
        passed, issues = run_qc(
            video_path=video_path,
            audio_path=combined_audio,
            thumbnail_path=thumb_path,
            title=title,
            description=description,
        )

        if not passed:
            logger.error("QC FAILED — video will NOT be published")
            for issue in issues:
                logger.error(f"  - {issue}")
            result["error"] = f"QC failed: {'; '.join(issues)}"
            # Still mark success=True so the video is saved as artifact
            result["success"] = True
            result["qc_passed"] = False
            return result

        logger.info("QC PASSED")

        # ── STEP 11: YouTube Upload ──────────────────────────
        if not skip_upload:
            logger.info("=" * 60)
            logger.info("STEP 11: Uploading to YouTube...")
            logger.info("=" * 60)

            has_creds = all([
                os.getenv("YOUTUBE_CLIENT_ID"),
                os.getenv("YOUTUBE_CLIENT_SECRET"),
                os.getenv("YOUTUBE_REFRESH_TOKEN"),
            ]) or os.path.exists("credentials.json")

            if has_creds:
                from youtube_uploader import YouTubeUploader
                uploader = YouTubeUploader()
                if uploader.youtube:
                    video_id = uploader.upload_video(
                        video_path=str(video_path),
                        title=title,
                        description=description,
                        tags=tags,
                        category_id="27",
                        privacy_status="public",
                    )
                    if video_id:
                        result["video_id"] = video_id
                        logger.info(f"Uploaded! https://www.youtube.com/watch?v={video_id}")

                        # Set thumbnail
                        uploader.set_thumbnail(video_id, str(thumb_path))
                    else:
                        logger.warning("YouTube upload returned no video ID")
                        result["error"] = "Upload failed"
                else:
                    result["error"] = "YouTube auth failed"
            else:
                logger.info("No YouTube credentials found, skipping upload")
                result["error"] = "No credentials"
        else:
            logger.info("STEP 11: Skipped (--skip-upload)")

        # ── STEP 12: Cleanup ─────────────────────────────────
        logger.info("=" * 60)
        logger.info("STEP 12: Cleanup...")
        logger.info("=" * 60)
        tts.cleanup(run_id)
        logger.info("Temporary audio files removed")

        result["success"] = True
        result["qc_passed"] = True
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Tamil video and optionally upload to YouTube"
    )
    parser.add_argument("--skip-upload", action="store_true")
    parser.add_argument("--resolution", default="1920x1080")
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    # Create output directories
    for d in ["audio_output", "videos", "images", "thumbnails", "temp"]:
        Path(d).mkdir(exist_ok=True)

    result = run_pipeline(
        skip_upload=args.skip_upload,
        resolution=args.resolution,
        fps=args.fps,
    )

    print("\n" + "=" * 60)
    print("RESULT SUMMARY")
    print("=" * 60)
    print(f"Success:    {result['success']}")
    print(f"Title:      {result.get('title', 'N/A')}")
    print(f"Video:      {result.get('video_path', 'N/A')}")
    print(f"YouTube ID: {result.get('video_id', 'N/A')}")
    print(f"QC Passed:  {result.get('qc_passed', 'N/A')}")
    if result.get("error"):
        print(f"Error:      {result['error']}")
    print("=" * 60)

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
