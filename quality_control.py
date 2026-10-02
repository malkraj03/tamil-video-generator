"""
Quality Control - automated checks before publishing a video.

Returns a pass/fail verdict with reasons.  If QC fails the pipeline
must NOT publish the video.
"""

import logging
from pathlib import Path
from typing import List, Tuple

from pydub import AudioSegment

from config import QC_MAX_FILE_SIZE_MB, QC_MIN_FILE_SIZE_MB, VIDEO_MIN_DURATION_SECS

logger = logging.getLogger(__name__)


def run_qc(
    video_path: Path,
    audio_path: Path,
    thumbnail_path: Path,
    title: str,
    description: str,
) -> Tuple[bool, List[str]]:
    """
    Run quality-control checks on the finished video.

    Returns:
        (passed: bool, issues: list[str])
    """
    issues: List[str] = []

    # 1. Video file exists and has reasonable size
    if not video_path.exists():
        issues.append("Video file does not exist")
    else:
        size_mb = video_path.stat().st_size / (1024 * 1024)
        if size_mb < QC_MIN_FILE_SIZE_MB:
            issues.append(f"Video too small ({size_mb:.1f} MB < {QC_MIN_FILE_SIZE_MB} MB)")
        if size_mb > QC_MAX_FILE_SIZE_MB:
            issues.append(f"Video too large ({size_mb:.1f} MB > {QC_MAX_FILE_SIZE_MB} MB)")

    # 2. Audio duration check (proxy for video duration)
    if not audio_path.exists():
        issues.append("Combined audio file does not exist")
    else:
        try:
            dur = len(AudioSegment.from_file(str(audio_path))) / 1000.0
            if dur < VIDEO_MIN_DURATION_SECS:
                issues.append(
                    f"Audio too short ({dur:.0f}s < {VIDEO_MIN_DURATION_SECS}s)"
                )
        except Exception as e:
            issues.append(f"Cannot read audio: {e}")

    # 3. Thumbnail exists
    if not thumbnail_path.exists():
        issues.append("Thumbnail file does not exist")

    # 4. Title and description are non-empty
    if not title or len(title.strip()) < 10:
        issues.append("Title is missing or too short")
    if not description or len(description.strip()) < 30:
        issues.append("Description is missing or too short")

    passed = len(issues) == 0
    if passed:
        logger.info("QC PASSED")
    else:
        for issue in issues:
            logger.warning(f"QC FAIL: {issue}")
    return passed, issues
