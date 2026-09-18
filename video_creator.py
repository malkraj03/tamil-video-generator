"""
Video Creator - Creates videos with mixed styles
Uses Pillow for all image generation (no external APIs needed)
Works on Linux (GitHub Actions), macOS, and Windows
"""

import os
import logging
import math
import random
import hashlib
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime

from moviepy.editor import (
    ImageClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip, AudioFileClip,
)
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import requests
from io import BytesIO
import urllib.parse
import numpy as np

logger = logging.getLogger(__name__)

# Font search paths for cross-platform support
FONT_SEARCH_PATHS = [
    # Linux (Ubuntu / GitHub Actions) - Tamil fonts
    "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf",
    # Linux - General fonts
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    # macOS
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/SFNSText.ttf",
    # Windows
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    # Bundled font (if user places one in project)
    "fonts/NotoSansTamil-Regular.ttf",
]

# Beautiful color themes for video backgrounds
COLOR_THEMES = [
    {"bg_start": (10, 10, 40), "bg_end": (40, 20, 80), "title": (255, 215, 0), "text": (255, 255, 255), "accent": (100, 149, 237)},
    {"bg_start": (5, 30, 20), "bg_end": (15, 60, 45), "title": (50, 255, 150), "text": (220, 255, 240), "accent": (0, 200, 150)},
    {"bg_start": (40, 10, 10), "bg_end": (80, 20, 30), "title": (255, 200, 100), "text": (255, 230, 220), "accent": (255, 100, 80)},
    {"bg_start": (10, 20, 50), "bg_end": (30, 50, 100), "title": (100, 200, 255), "text": (220, 240, 255), "accent": (50, 150, 255)},
    {"bg_start": (30, 10, 40), "bg_end": (60, 20, 80), "title": (200, 150, 255), "text": (240, 230, 255), "accent": (180, 100, 255)},
    {"bg_start": (40, 30, 5), "bg_end": (80, 60, 15), "title": (255, 200, 50), "text": (255, 240, 200), "accent": (220, 180, 50)},
]


# Free AI image prompts for cartoon-style backgrounds per category
CARTOON_PROMPTS = {
    "history": "colorful cartoon illustration of ancient Tamil Chola and Pandya kingdoms, animated story scene, vibrant colors, high quality",
    "mythology": "colorful cartoon illustration of South Indian temple festival and divine legends, animated mythology scene, bright colors",
    "science": "cartoon illustration of ancient Tamil scholars studying astronomy and mathematics, bright creative scene",
    "culture": "vibrant cartoon illustration of Tamil classical dance and music festival, colorful cultural scene",
    "lifestyle": "cartoon illustration of healthy South Indian yoga and wellness lifestyle, warm colors",
    "nature": "cartoon illustration of Tamil Nadu hills, forests and waterfalls, vibrant nature scene",
    "inventions": "cartoon illustration of ancient Tamil language and inventions, creative colorful scene",
    "famous_people": "cartoon illustration of inspiring Tamil leaders and celebrities, colorful portrait style scene",
    "festivals": "cartoon illustration of Tamil Pongal and festival celebration, bright festive colors",
    "food": "cartoon illustration of delicious South Indian Tamil food dishes, colorful food art",
}


def find_font(size: int = 40) -> ImageFont.FreeTypeFont:
    """Find an available font on this system"""
    for font_path in FONT_SEARCH_PATHS:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Try fc-match on Linux
    try:
        import subprocess
        result = subprocess.run(["fc-match", "--format=%{file}", "sans"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return ImageFont.truetype(result.stdout.strip(), size)
    except Exception:
        pass

    logger.warning("No TrueType font found, using default bitmap font")
    return ImageFont.load_default()


class VideoCreator:
    """Create videos with mixed styles using only Pillow (no external APIs)"""

    def __init__(self, output_dir: str = "videos",
                 resolution: Tuple[int, int] = (1920, 1080), fps: int = 30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.image_dir = Path("images")
        self.image_dir.mkdir(exist_ok=True)
        self.resolution = resolution
        self.fps = fps
        self.width, self.height = resolution
        self.temp_files = []  # track temp files for cleanup
        self._category_images = {}

    def create_video(self, content: Dict, audio_path: str, title: str) -> str:
        """
        Create complete video from content and audio

        Args:
            content: Content dictionary from content_generator
            audio_path: Path to audio file
            title: Video title

        Returns:
            Path to created video
        """
        try:
            logger.info(f"Creating video: {title}")

            # Get audio duration
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            logger.info(f"Audio duration: {audio_duration:.1f}s")

            # Create video clips
            video_clips = self._create_mixed_style_video(content, audio_duration)

            # Concatenate clips
            final_video = concatenate_videoclips(video_clips, method="compose")

            # Add audio
            final_video = final_video.set_audio(audio)

            # Generate output filename (safe characters only)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"tamil_video_{timestamp}.mp4"

            logger.info(f"Writing video to: {output_path}")
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                threads=2,
                preset='medium',
            )

            # Cleanup
            audio.close()
            final_video.close()
            for clip in video_clips:
                clip.close()
            self._cleanup_temp_files()

            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating video: {e}")
            self._cleanup_temp_files()
            raise

    def _create_mixed_style_video(self, content: Dict, duration: float) -> List:
        """Create video with mixed styles"""
        clips = []
        theme = random.choice(COLOR_THEMES)

        # Intro clip (5% of duration, min 3s, max 8s)
        intro_duration = max(3, min(8, duration * 0.05))
        intro_clip = self._create_intro_clip(content.get('title', ''), theme, intro_duration)
        clips.append(intro_clip)

        # Content clips
        content_items = content.get('content', [])
        if not content_items:
            # Fallback: single clip for remaining duration
            remaining = duration - intro_duration - 3
            clips.append(ColorClip(size=self.resolution, color=theme['bg_start']).set_duration(remaining))
        else:
            remaining_duration = duration - intro_duration - max(3, min(5, duration * 0.05))
            clip_duration = remaining_duration / len(content_items)

            for idx, item in enumerate(content_items):
                style = idx % 3  # rotate through styles
                item_theme = COLOR_THEMES[(COLOR_THEMES.index(theme) + idx) % len(COLOR_THEMES)]

                # Storytelling scene position for this segment
                total_items = len(content_items)
                if idx == 0:
                    item['_story_scene'] = 'opening scene of a'
                elif idx == total_items - 1:
                    item['_story_scene'] = 'final scene of a'
                else:
                    item['_story_scene'] = f'middle scene {idx} of a'

                if style == 0:
                    clip = self._create_title_content_clip(item, item_theme, clip_duration)
                elif style == 1:
                    clip = self._create_full_text_clip(item, item_theme, clip_duration)
                else:
                    clip = self._create_gradient_text_clip(item, item_theme, clip_duration)

                clips.append(clip)

        # Outro clip
        outro_duration = max(3, min(5, duration * 0.05))
        outro_clip = self._create_outro_clip(theme, outro_duration)
        clips.append(outro_clip)

        return clips

    def _create_intro_clip(self, title: str, theme: dict, duration: float):
        """Create intro clip with channel title"""
        image = self._create_gradient_background(theme['bg_start'], theme['bg_end'])
        draw = ImageDraw.Draw(image)

        font_large = find_font(80)
        font_small = find_font(50)

        # Draw decorative line
        line_y = 250
        draw.line([(self.width // 4, line_y), (3 * self.width // 4, line_y)],
                  fill=theme['accent'], width=3)

        # Draw main title
        main_title = "Tamil History & Fun Facts"
        self._draw_centered_text(draw, main_title, self.height // 2 - 80,
                                 font_large, theme['title'])

        # Draw Tamil subtitle
        tamil_title = title if title else "தமிழ் வரலாறு மற்றும் சுவையான உண்மைகள்"
        # Truncate if too long
        if len(tamil_title) > 50:
            tamil_title = tamil_title[:47] + "..."
        self._draw_centered_text(draw, tamil_title, self.height // 2 + 30,
                                 font_small, theme['text'])

        # Draw decorative line bottom
        line_y = self.height - 250
        draw.line([(self.width // 4, line_y), (3 * self.width // 4, line_y)],
                  fill=theme['accent'], width=3)

        return self._image_to_clip(image, duration, fade=True)

    def _create_title_content_clip(self, item: Dict, theme: dict, duration: float):
        """Create clip with title at top and content below"""
        image = self._get_background_image(theme, item)
        draw = ImageDraw.Draw(image)

        font_title = find_font(65)
        font_body = find_font(42)

        # Draw title with underline
        title = item.get('title', '')
        title_y = 120
        self._draw_centered_text(draw, title, title_y, font_title, theme['title'])

        # Draw underline
        draw.line([(200, title_y + 90), (self.width - 200, title_y + 90)],
                  fill=theme['accent'], width=2)

        # Draw content text wrapped
        content = item.get('content', '')
        wrapped = self._wrap_text_smart(content, font_body, self.width - 300)
        y = title_y + 140
        for line in wrapped:
            self._draw_centered_text(draw, line, y, font_body, theme['text'])
            y += 65

        # Draw category badge
        category = item.get('category', '')
        if category:
            badge_font = find_font(28)
            badge_text = f"  {category.upper()}  "
            bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
            badge_w = bbox[2] - bbox[0] + 20
            badge_h = bbox[3] - bbox[1] + 16
            badge_x = self.width - badge_w - 60
            badge_y = self.height - badge_h - 60
            draw.rounded_rectangle(
                [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
                radius=10, fill=theme['accent']
            )
            draw.text((badge_x + 10, badge_y + 8), badge_text,
                      fill=(255, 255, 255), font=badge_font)

        return self._image_to_clip(image, duration, fade=True)

    def _create_full_text_clip(self, item: Dict, theme: dict, duration: float):
        """Create clip with content text centered on dark background"""
        image = self._get_background_image(theme, item, darker=True)
        draw = ImageDraw.Draw(image)

        font_title = find_font(55)
        font_body = find_font(40)

        # Draw number/icon area
        number = str(random.randint(1, 99))
        num_font = find_font(120)
        self._draw_centered_text(draw, number, 80, num_font, (*theme['accent'], 60))

        # Draw title
        title = item.get('title', '')
        self._draw_centered_text(draw, title, 280, font_title, theme['title'])

        # Draw horizontal rule
        draw.line([(300, 360), (self.width - 300, 360)],
                  fill=theme['accent'], width=2)

        # Draw content
        content = item.get('content', '')
        wrapped = self._wrap_text_smart(content, font_body, self.width - 400)
        y = 400
        for line in wrapped:
            self._draw_centered_text(draw, line, y, font_body, theme['text'])
            y += 60

        return self._image_to_clip(image, duration, fade=True)

    def _create_gradient_text_clip(self, item: Dict, theme: dict, duration: float):
        """Create clip with radial gradient or cartoon image and text"""
        image = self._get_background_image(theme, item, radial=True)
        draw = ImageDraw.Draw(image)

        font_title = find_font(70)
        font_body = find_font(38)

        # Draw decorative corners
        corner_size = 80
        for corners in [
            [(40, 40), (40 + corner_size, 40)],
            [(40, 40), (40, 40 + corner_size)],
            [(self.width - 40 - corner_size, 40), (self.width - 40, 40)],
            [(self.width - 40, 40), (self.width - 40, 40 + corner_size)],
            [(40, self.height - 40), (40 + corner_size, self.height - 40)],
            [(40, self.height - 40 - corner_size), (40, self.height - 40)],
            [(self.width - 40, self.height - 40 - corner_size), (self.width - 40, self.height - 40)],
            [(self.width - 40 - corner_size, self.height - 40), (self.width - 40, self.height - 40)],
        ]:
            draw.line(corners, fill=theme['accent'], width=2)

        # Draw title
        title = item.get('title', '')
        self._draw_centered_text(draw, title, 200, font_title, theme['title'])

        # Draw content
        content = item.get('content', '')
        wrapped = self._wrap_text_smart(content, font_body, self.width - 350)
        y = 380
        for line in wrapped:
            self._draw_centered_text(draw, line, y, font_body, theme['text'])
            y += 55

        return self._image_to_clip(image, duration, fade=True)

    def _create_outro_clip(self, theme: dict, duration: float):
        """Create outro clip"""
        image = self._create_gradient_background(theme['bg_start'], theme['bg_end'])
        draw = ImageDraw.Draw(image)

        font_large = find_font(90)
        font_medium = find_font(50)
        font_small = find_font(35)

        # Thank you text
        self._draw_centered_text(draw, "நன்றி!", self.height // 2 - 120,
                                 font_large, theme['title'])
        self._draw_centered_text(draw, "Thank You!", self.height // 2,
                                 font_medium, theme['text'])

        # Subscribe text
        self._draw_centered_text(draw, "Like | Subscribe | Share",
                                 self.height // 2 + 100, font_small, theme['accent'])

        return self._image_to_clip(image, duration, fade=True)

    def _get_story_image(self, item: Dict) -> Image.Image | None:
        """Fetch or load a cartoon-style story image for a content segment"""
        category = item.get('_category', '')
        base_prompt = CARTOON_PROMPTS.get(category)
        if not base_prompt:
            return None
        scene = item.get('_story_scene', '')
        title = item.get('title', '')
        prompt = f"{scene} {base_prompt}".strip() if scene else base_prompt
        item_hash = hashlib.md5(f"{category}_{title}".encode('utf-8')).hexdigest()[:12]
        cache_path = self.image_dir / f"{category}_{item_hash}.png"
        try:
            if cache_path.exists():
                img = Image.open(cache_path).convert('RGB')
                return img.copy()
            encoded = urllib.parse.quote(prompt)
            seed = int(item_hash[:8], 16) % 100000
            url = f"https://image.pollinations.ai/prompt/{encoded}?width={self.width}&height={self.height}&nologo=true&seed={seed}"
            logger.info(f"Generating story image for '{category}' ({scene})...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert('RGB')
            if img.size != self.resolution:
                img = img.resize(self.resolution, Image.Resampling.LANCZOS)
            img.save(cache_path)
            return img.copy()
        except Exception as e:
            logger.warning(f"Could not load story image for '{category}': {e}")
            return None

    def _get_background_image(self, theme: dict, item: Dict,
                               darker: bool = False, radial: bool = False) -> Image.Image:
        """Return a cartoon story image background or a gradient fallback"""
        img = self._get_story_image(item)
        if img:
            brightness = 0.35 if darker else 0.45
            return ImageEnhance.Brightness(img).enhance(brightness)
        if radial:
            return self._create_radial_gradient(theme['bg_start'], theme['bg_end'])
        if darker:
            bg_start = tuple(max(0, c - 15) for c in theme['bg_start'])
            bg_end = tuple(max(0, c - 15) for c in theme['bg_end'])
            return self._create_gradient_background(bg_start, bg_end)
        return self._create_gradient_background(theme['bg_start'], theme['bg_end'])

    # ---- Helper methods ----

    def _create_gradient_background(self, color_start: tuple, color_end: tuple) -> Image.Image:
        """Create a vertical gradient background"""
        image = Image.new('RGB', self.resolution)
        draw = ImageDraw.Draw(image)

        for y in range(self.height):
            ratio = y / self.height
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return image

    def _create_radial_gradient(self, color_start: tuple, color_end: tuple) -> Image.Image:
        """Create a radial gradient background"""
        image = Image.new('RGB', self.resolution)
        cx, cy = self.width // 2, self.height // 2
        max_dist = math.sqrt(cx**2 + cy**2)

        pixels = image.load()
        for y in range(self.height):
            for x in range(self.width):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
                dist = min(dist, 1.0)
                r = int(color_start[0] + (color_end[0] - color_start[0]) * dist)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * dist)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * dist)
                pixels[x, y] = (r, g, b)

        return image

    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str, y: int,
                            font: ImageFont.FreeTypeFont, color: tuple):
        """Draw text centered horizontally"""
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            # Ensure text fits
            if text_width > self.width - 100:
                x = 50
            draw.text((x, y), text, fill=color, font=font)
        except Exception as e:
            logger.warning(f"Error drawing text '{text[:30]}...': {e}")

    def _wrap_text_smart(self, text: str, font: ImageFont.FreeTypeFont,
                         max_width: int) -> List[str]:
        """Wrap text to fit within max_width pixels"""
        words = text.split()
        lines = []
        current_line = []
        dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))

        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
            except Exception:
                line_width = len(test_line) * 20

            if line_width > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _image_to_clip(self, image: Image.Image, duration: float, fade: bool = False):
        """Convert PIL Image to moviepy clip"""
        temp_path = self.output_dir / f"temp_{datetime.now().timestamp()}.png"
        image.save(str(temp_path))
        self.temp_files.append(str(temp_path))

        clip = ImageClip(str(temp_path)).set_duration(duration)
        if fade:
            clip = clip.fadein(0.4).fadeout(0.4)

        return clip

    def _cleanup_temp_files(self):
        """Remove temporary image files"""
        for f in self.temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except OSError:
                pass
        self.temp_files = []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from content_generator import TamilContentGenerator

    content_gen = TamilContentGenerator()
    content = content_gen.get_random_content()

    print(f"Content: {content['title']}")
    print(f"Duration: {content['total_duration']} seconds")
    print(f"Items: {len(content['content'])}")
