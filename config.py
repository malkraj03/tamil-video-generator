"""
Central configuration for the Tamil Video Generator pipeline.
All settings, paths, and environment variable handling.
"""

import os
from pathlib import Path

# ── Directories ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
AUDIO_DIR = PROJECT_ROOT / "audio_output"
VIDEO_DIR = PROJECT_ROOT / "videos"
IMAGE_DIR = PROJECT_ROOT / "images"
THUMBNAIL_DIR = PROJECT_ROOT / "thumbnails"
TEMP_DIR = PROJECT_ROOT / "temp"

for _d in [AUDIO_DIR, VIDEO_DIR, IMAGE_DIR, THUMBNAIL_DIR, TEMP_DIR]:
    _d.mkdir(exist_ok=True)

# ── API Keys (environment variables, NEVER hardcoded) ────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# ── Gemini ───────────────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# ── Video ────────────────────────────────────────────────────
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_TARGET_DURATION_MINS = 12  # target narration length
VIDEO_MIN_DURATION_SECS = 540   # QC gate: at least 9 minutes

# ── TTS ──────────────────────────────────────────────────────
TTS_VOICE = os.getenv("TTS_VOICE", "ta-IN-PallaviNeural")
TTS_DEFAULT_RATE = "+0%"
TTS_HOOK_RATE = "+5%"

# ── Thumbnail ────────────────────────────────────────────────
THUMB_WIDTH = 1280
THUMB_HEIGHT = 720

# ── Content categories (rotated daily) ───────────────────────
CONTENT_CATEGORIES = [
    "Tamil History",
    "Indian History",
    "World History",
    "Science Facts",
    "Technology & AI",
    "Space & Astronomy",
    "Psychology",
    "Engineering Marvels",
    "Trending Topics",
    "Unknown & Surprising Facts",
    "Mysteries & Unsolved Cases",
]

# ── Topic tracking ───────────────────────────────────────────
USED_TOPICS_FILE = PROJECT_ROOT / "used_topics.json"

# ── Quality-control thresholds ───────────────────────────────
QC_MIN_FILE_SIZE_MB = 15
QC_MAX_FILE_SIZE_MB = 2000

# ── Font search paths (cross-platform) ──────────────────────
FONT_PATHS = [
    # Linux (GitHub Actions) - Tamil
    "/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
    # Linux - fallback
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    # macOS
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    # Windows
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
