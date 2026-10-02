"""
Visual Engine - sources relevant stock images for each scene.

Priority order:
  1. Pexels API  (free, 200 req/hr, high quality)
  2. Solid-color gradient fallback  (always works)

Images are cached in images/ to avoid re-downloading.
"""

import hashlib
import logging
import random
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from PIL import Image, ImageDraw

from config import PEXELS_API_KEY, IMAGE_DIR, VIDEO_WIDTH, VIDEO_HEIGHT

logger = logging.getLogger(__name__)

_PEXELS_SEARCH = "https://api.pexels.com/v1/search"


# ── gradient fallback ────────────────────────────────────────

_GRADIENT_PALETTES = [
    ((10, 10, 50), (30, 20, 80)),
    ((5, 30, 25), (15, 60, 50)),
    ((40, 10, 15), (80, 20, 35)),
    ((10, 25, 55), (30, 55, 110)),
    ((30, 10, 45), (60, 25, 85)),
    ((45, 30, 5), (90, 65, 15)),
]


def _make_gradient(
    w: int, h: int,
    c1: Tuple[int, int, int],
    c2: Tuple[int, int, int],
) -> Image.Image:
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(c1[0] + (c2[0] - c1[0]) * y / h)
        g = int(c1[1] + (c2[1] - c1[1]) * y / h)
        b = int(c1[2] + (c2[2] - c1[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


# ── Pexels fetcher ───────────────────────────────────────────

def _fetch_pexels(query: str, per_page: int = 5) -> Optional[Image.Image]:
    """Search Pexels and return the best-matching landscape photo."""
    if not PEXELS_API_KEY:
        return None
    try:
        resp = requests.get(
            _PEXELS_SEARCH,
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            timeout=15,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
        if not photos:
            return None
        photo = random.choice(photos[:3])
        img_url = photo["src"].get("large2x") or photo["src"].get("large")
        img_resp = requests.get(img_url, timeout=30)
        img_resp.raise_for_status()
        img = Image.open(BytesIO(img_resp.content)).convert("RGB")
        return img
    except Exception as e:
        logger.warning(f"Pexels fetch failed for '{query}': {e}")
        return None


# ── public API ───────────────────────────────────────────────

def fetch_scene_images(
    queries: List[str],
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT,
) -> List[Path]:
    """
    For each search query, return a local image path (cached).

    Falls back to a gradient background when stock search fails.
    """
    paths: List[Path] = []
    palette_idx = 0

    for i, query in enumerate(queries):
        q_hash = hashlib.md5(query.encode()).hexdigest()[:10]
        cache_path = IMAGE_DIR / f"scene_{i:03d}_{q_hash}.jpg"

        if cache_path.exists():
            paths.append(cache_path)
            logger.debug(f"Scene {i}: cached {cache_path.name}")
            continue

        # Try Pexels
        img = _fetch_pexels(query)

        if img is None:
            # Gradient fallback
            c1, c2 = _GRADIENT_PALETTES[palette_idx % len(_GRADIENT_PALETTES)]
            palette_idx += 1
            img = _make_gradient(width, height, c1, c2)
            logger.info(f"Scene {i}: gradient fallback")
        else:
            logger.info(f"Scene {i}: Pexels image for '{query}'")

        # Resize / crop to exact resolution
        img = _fit_cover(img, width, height)
        img.save(cache_path, "JPEG", quality=90)
        paths.append(cache_path)

    return paths


def _fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    """Resize and center-crop to exactly tw x th (cover mode)."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - tw) // 2
    top = (new_h - th) // 2
    return img.crop((left, top, left + tw, top + th))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_queries = ["ancient Indian temple architecture", "Tamil Nadu landscape"]
    result = fetch_scene_images(test_queries)
    for p in result:
        print(p)
