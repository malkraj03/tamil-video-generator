"""
Thumbnail Engine - generates a professional YouTube thumbnail (1280x720).

Design:
  - Uses the best scene image as background
  - Darkened / colour-graded for contrast
  - Large, bold text overlay (2-4 words)
  - Accent colour border / glow
"""

import logging
import os
import random
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from config import FONT_PATHS, THUMB_HEIGHT, THUMB_WIDTH, THUMBNAIL_DIR

logger = logging.getLogger(__name__)


def _font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap(text: str, font, max_w: int) -> List[str]:
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        tw = dummy.textbbox((0, 0), test, font=font)[2]
        if tw > max_w and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


_ACCENT_COLORS = [
    (255, 215, 0),   # gold
    (0, 200, 255),   # cyan
    (255, 80, 80),   # red
    (100, 255, 100), # green
    (255, 150, 50),  # orange
]


def generate_thumbnail(
    text: str,
    scene_images: List[Path],
    run_id: str,
) -> Path:
    """
    Create a 1280x720 YouTube thumbnail.

    Args:
        text: 2-5 words to display prominently.
        scene_images: available scene images (picks the best one).
        run_id: unique identifier.

    Returns:
        Path to saved thumbnail JPEG.
    """
    w, h = THUMB_WIDTH, THUMB_HEIGHT
    accent = random.choice(_ACCENT_COLORS)

    # Pick a background image (prefer middle scenes for visual interest)
    bg = None
    if scene_images:
        mid = len(scene_images) // 2
        candidates = scene_images[max(0, mid - 1):mid + 2]
        for bp in candidates:
            try:
                bg = Image.open(bp).convert("RGB")
                break
            except Exception:
                continue

    if bg is None:
        bg = Image.new("RGB", (w, h), (20, 20, 60))

    # Resize to cover
    bg = _fit_cover(bg, w, h)

    # Darken and boost contrast
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    bg = ImageEnhance.Contrast(bg).enhance(1.3)

    # Optional: slight blur for depth
    bg = bg.filter(ImageFilter.GaussianBlur(radius=2))

    draw = ImageDraw.Draw(bg)

    # Accent border
    bw = 8
    draw.rectangle([(bw, bw), (w - bw, h - bw)], outline=accent, width=bw)

    # Main text
    font_size = 96
    f = _font(font_size)
    lines = _wrap(text, f, w - 120)
    if len(lines) > 3:
        font_size = 72
        f = _font(font_size)
        lines = _wrap(text, f, w - 120)

    line_h = font_size + 12
    total_h = len(lines) * line_h
    y_start = (h - total_h) // 2

    # Draw text shadow
    for i, ln in enumerate(lines):
        y = y_start + i * line_h
        bbox = draw.textbbox((0, 0), ln, font=f)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        # Shadow
        draw.text((x + 3, y + 3), ln, fill=(0, 0, 0), font=f)
        # Main text
        draw.text((x, y), ln, fill=(255, 255, 255), font=f)

    # Small accent label at bottom
    f_sm = _font(28)
    draw.text((40, h - 60), "Tamil Facts & History", fill=accent, font=f_sm)

    out_path = THUMBNAIL_DIR / f"thumb_{run_id}.jpg"
    bg.save(str(out_path), "JPEG", quality=95)
    logger.info(f"Thumbnail saved: {out_path}")
    return out_path


def _fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))
