"""
Generate Once - Single video generation and upload script.
Designed for CI/CD (GitHub Actions) - runs once, generates one video, uploads to YouTube.

Usage:
    python generate_once.py
    python generate_once.py --duration 300 --resolution 1280x720
    python generate_once.py --skip-upload  # Generate video without YouTube upload
"""

import os
import sys
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_video(duration: int = 300, resolution: str = "1280x720",
                   fps: int = 24, skip_upload: bool = False,
                   voice: str = "male_in") -> dict:
    """
    Complete pipeline: generate content -> TTS audio -> create video -> upload to YouTube

    Args:
        duration: Target video duration in seconds (default: 300 = 5 minutes)
        resolution: Video resolution (default: 1280x720 for faster processing)
        fps: Frames per second (default: 24)
        skip_upload: If True, skip YouTube upload
        voice: TTS voice key (default: male_in)

    Returns:
        Result dictionary with success status and details
    """
    result = {
        'success': False,
        'video_path': None,
        'video_id': None,
        'title': None,
        'error': None,
    }

    try:
        # Parse resolution
        width, height = map(int, resolution.split('x'))

        # Step 1: Generate content
        logger.info("=" * 60)
        logger.info("STEP 1: Generating content...")
        logger.info("=" * 60)

        from content_generator import TamilContentGenerator
        content_gen = TamilContentGenerator()
        content = content_gen.get_random_content(duration_target=duration)

        logger.info(f"Title: {content['title']}")
        logger.info(f"Category: {content['category']}")
        logger.info(f"Content items: {len(content['content'])}")
        logger.info(f"Estimated duration: {content['estimated_video_duration']}s")
        result['title'] = content['title']

        # Step 2: Generate Tamil audio
        logger.info("=" * 60)
        logger.info("STEP 2: Generating Tamil speech audio...")
        logger.info("=" * 60)

        from tts_generator import TamilTTSGenerator
        tts = TamilTTSGenerator(output_dir="audio_output", voice=voice)

        audio_filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        audio_path = tts.generate_script_audio(content['script'], audio_filename)

        audio_duration = tts.get_audio_duration(audio_path)
        logger.info(f"Audio generated: {audio_path}")
        logger.info(f"Audio duration: {audio_duration:.1f}s")

        # Step 3: Create video
        logger.info("=" * 60)
        logger.info("STEP 3: Creating video...")
        logger.info("=" * 60)

        from video_creator import VideoCreator
        video_creator = VideoCreator(
            output_dir="videos",
            resolution=(width, height),
            fps=fps
        )

        video_path = video_creator.create_video(
            content=content,
            audio_path=audio_path,
            title=content['title']
        )

        logger.info(f"Video created: {video_path}")
        result['video_path'] = video_path

        # Check video file size
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"Video size: {video_size_mb:.1f} MB")

        # Step 4: Upload to YouTube
        if not skip_upload:
            logger.info("=" * 60)
            logger.info("STEP 4: Uploading to YouTube...")
            logger.info("=" * 60)

            # Check if YouTube credentials are available
            has_creds = all([
                os.getenv('YOUTUBE_CLIENT_ID'),
                os.getenv('YOUTUBE_CLIENT_SECRET'),
                os.getenv('YOUTUBE_REFRESH_TOKEN'),
            ]) or os.path.exists('credentials.json')

            if has_creds:
                from youtube_uploader import YouTubeUploader
                uploader = YouTubeUploader()

                if uploader.youtube:
                    video_id = uploader.upload_video(
                        video_path=video_path,
                        title=content['title'],
                        description=content['description'],
                        tags=content['tags'],
                        category_id='27',  # Education
                        privacy_status='public'
                    )

                    if video_id:
                        result['video_id'] = video_id
                        logger.info(f"Video uploaded! ID: {video_id}")
                        logger.info(f"URL: https://www.youtube.com/watch?v={video_id}")
                    else:
                        logger.warning("Video upload failed")
                        result['error'] = "Upload failed"
                else:
                    logger.warning("YouTube service not available")
                    result['error'] = "YouTube auth failed"
            else:
                logger.info("YouTube credentials not found, skipping upload")
                logger.info("Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
                result['error'] = "No YouTube credentials"
        else:
            logger.info("STEP 4: Skipping YouTube upload (--skip-upload flag)")

        # Step 5: Cleanup audio files
        logger.info("=" * 60)
        logger.info("STEP 5: Cleanup...")
        logger.info("=" * 60)

        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Removed audio: {audio_path}")
        except OSError:
            pass

        result['success'] = True
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        result['error'] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Generate a Tamil video and optionally upload to YouTube'
    )
    parser.add_argument('--duration', type=int, default=300,
                        help='Target video duration in seconds (default: 300)')
    parser.add_argument('--resolution', default='1280x720',
                        help='Video resolution (default: 1280x720)')
    parser.add_argument('--fps', type=int, default=24,
                        help='Frames per second (default: 24)')
    parser.add_argument('--skip-upload', action='store_true',
                        help='Skip YouTube upload')
    parser.add_argument('--voice', default='male_in',
                        choices=['male_in', 'female_in', 'male_lk', 'female_lk',
                                 'male_my', 'female_my', 'male_sg', 'female_sg'],
                        help='TTS voice (default: male_in = Indian Tamil Male)')

    args = parser.parse_args()

    # Create output directories
    Path("audio_output").mkdir(exist_ok=True)
    Path("videos").mkdir(exist_ok=True)

    result = generate_video(
        duration=args.duration,
        resolution=args.resolution,
        fps=args.fps,
        skip_upload=args.skip_upload,
        voice=args.voice,
    )

    # Print result summary
    print("\n" + "=" * 60)
    print("RESULT SUMMARY")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"Video: {result.get('video_path', 'N/A')}")
    print(f"YouTube ID: {result.get('video_id', 'N/A')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    print("=" * 60)

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
