"""
Video Engine - composes the final MP4 from scene images, narration
audio, subtitles, and background music.

Uses Pillow for frame generation and moviepy for assembly.
Produces a professional-looking video with:
  - Per-sentence subtitle overlays burned into frames
  - Ken Burns (slow zoom) on scene images
  - Darkened image backgrounds for text readability
  - Intro and outro cards
  - Background music mixed under narration
"""

import logging
import math
import os
import random
import struct
import wave
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import numpy as np
from moviepy.editor import (
    AudioFileClip, CompositeAudioClip, CompositeVideoClip,
    ImageClip, concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from pydub import AudioSegment
from pydub.generators import Sine

from config import (
    AUDIO_DIR, FONT_PATHS, TEMP_DIR, THUMBNAIL_DIR,
    VIDEO_DIR, VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH,
)
from tts_engine import SentenceAudio

logger = logging.getLogger(__name__)

# ── font helper ──────────────────────────────────────────────

def _find_font(size: int = 40) -> ImageFont.FreeTypeFont:
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    try:
        import subprocess
        r = subprocess.run(["fc-match", "--format=%{file}", "sans"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return ImageFont.truetype(r.stdout.strip(), size)
    except Exception:
        pass
    return ImageFont.load_default()


# ── text helpers ─────────────────────────────────────────────

def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> List[str]:
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


def _draw_centered(draw, text, y, font, color, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = max(0, (width - tw) // 2)
    draw.text((x, y), text, fill=color, font=font)


# ── background music generator ───────────────────────────────

def _generate_ambient_music(duration_s: float, out_path: Path):
    """Create a soft ambient drone for background music (no external files)."""
    sr = 22050
    samples = int(sr * duration_s)
    t = np.linspace(0, duration_s, samples, dtype=np.float32)

    # Layer several low sine waves for a warm pad
    signal = np.zeros(samples, dtype=np.float32)
    for freq, amp in [(65, 0.15), (98, 0.10), (130, 0.08), (196, 0.05)]:
        signal += amp * np.sin(2 * np.pi * freq * t)

    # Slow volume modulation (breathing effect)
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
    signal *= mod

    # Fade in/out
    fade = int(sr * 3)
    signal[:fade] *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)

    # Normalize to 16-bit
    signal = np.clip(signal, -1, 1)
    pcm = (signal * 32767).astype(np.int16)

    # Write WAV
    wav_path = out_path.with_suffix(".wav")
    with wave.open(str(wav_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    # Convert to MP3 via pydub
    seg = AudioSegment.from_wav(str(wav_path))
    seg.export(str(out_path), format="mp3", bitrate="128k")
    wav_path.unlink(missing_ok=True)
    logger.info(f"Generated ambient music: {duration_s:.0f}s")


# ── color themes ─────────────────────────────────────────────

_THEMES = [
    {"title": (255, 215, 0), "text": (255, 255, 255), "sub_bg": (0, 0, 0, 180), "accent": (100, 149, 237)},
    {"title": (50, 255, 150), "text": (220, 255, 240), "sub_bg": (0, 0, 0, 180), "accent": (0, 200, 150)},
    {"title": (255, 200, 100), "text": (255, 230, 220), "sub_bg": (0, 0, 0, 180), "accent": (255, 100, 80)},
    {"title": (100, 200, 255), "text": (220, 240, 255), "sub_bg": (0, 0, 0, 180), "accent": (50, 150, 255)},
    {"title": (200, 150, 255), "text": (240, 230, 255), "sub_bg": (0, 0, 0, 180), "accent": (180, 100, 255)},
]


# ── main class ───────────────────────────────────────────────

class VideoEngine:
    """Compose final MP4 from images, audio, and metadata."""

    def __init__(self):
        self.w = VIDEO_WIDTH
        self.h = VIDEO_HEIGHT
        self.fps = VIDEO_FPS
        self._temp: List[str] = []

    # ── public API ───────────────────────────────────────────

    def compose(
        self,
        sentence_audios: List[SentenceAudio],
        scene_images: List[Path],
        scenes: List[dict],
        title: str,
        run_id: str,
    ) -> Path:
        """
        Build the final video.

        Args:
            sentence_audios: per-sentence TTS data (from tts_engine)
            scene_images: one background image per scene (from visual_engine)
            scenes: screenplay scenes list
            title: video title for intro card
            run_id: unique identifier

        Returns:
            Path to final MP4.
        """
        theme = random.choice(_THEMES)

        # 1. Build per-sentence video clips
        clips = []

        # Intro card
        intro_img = self._make_intro(title, theme)
        intro_clip = self._img_clip(intro_img, 5.0, fade=True)
        clips.append(intro_clip)

        # Scene clips
        for sa in sentence_audios:
            bg_path = self._scene_bg(sa.scene_idx, scene_images)
            frame = self._make_sentence_frame(bg_path, sa, theme)
            clip = self._img_clip(frame, sa.duration_s + 0.3)
            clips.append(clip)

        # Outro card
        outro_img = self._make_outro(theme)
        outro_clip = self._img_clip(outro_img, 5.0, fade=True)
        clips.append(outro_clip)

        # 2. Concatenate
        video = concatenate_videoclips(clips, method="compose")

        # 3. Audio: narration + background music
        narration_path = AUDIO_DIR / f"{run_id}_combined.mp3"
        total_dur = video.duration
        music_path = AUDIO_DIR / f"{run_id}_music.mp3"
        _generate_ambient_music(total_dur, music_path)

        narration_audio = AudioFileClip(str(narration_path))
        music_audio = AudioFileClip(str(music_path)).volumex(0.12)

        # Pad narration with silence for intro
        from moviepy.audio.AudioClip import AudioClip
        intro_silence = AudioClip(lambda t: [0], duration=5.0, fps=44100)
        intro_silence = intro_silence.set_duration(5.0)

        # Compose: silence for intro, then narration, music runs full length
        final_audio = CompositeAudioClip([
            music_audio.set_duration(total_dur),
            narration_audio.set_start(5.0),
        ])
        video = video.set_audio(final_audio)

        # 4. Render
        out_path = VIDEO_DIR / f"tamil_video_{run_id}.mp4"
        logger.info(f"Rendering video: {total_dur:.0f}s -> {out_path}")
        video.write_videofile(
            str(out_path),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            verbose=False,
            logger=None,
            threads=2,
            preset="medium",
        )

        # Cleanup
        video.close()
        narration_audio.close()
        music_audio.close()
        for c in clips:
            c.close()
        self._cleanup()
        music_path.unlink(missing_ok=True)

        file_mb = out_path.stat().st_size / (1024 * 1024)
        logger.info(f"Video rendered: {out_path} ({file_mb:.1f} MB)")
        return out_path

    # ── frame builders ───────────────────────────────────────

    def _make_intro(self, title: str, theme: dict) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (10, 10, 35))
        draw = ImageDraw.Draw(img)
        f_big = _find_font(72)
        f_med = _find_font(48)
        f_sm = _find_font(32)

        # Decorative lines
        draw.line([(self.w // 4, 260), (3 * self.w // 4, 260)],
                  fill=theme["accent"], width=3)
        _draw_centered(draw, "Tamil Facts & History", 300, f_big,
                       theme["title"], self.w)

        # Episode title (wrapped)
        lines = _wrap(title, f_med, self.w - 200)
        y = 420
        for ln in lines[:3]:
            _draw_centered(draw, ln, y, f_med, theme["text"], self.w)
            y += 65

        draw.line([(self.w // 4, self.h - 260), (3 * self.w // 4, self.h - 260)],
                  fill=theme["accent"], width=3)
        _draw_centered(draw, "Subscribe & Like", self.h - 220, f_sm,
                       theme["accent"], self.w)
        return img

    def _make_outro(self, theme: dict) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (10, 10, 35))
        draw = ImageDraw.Draw(img)
        f_big = _find_font(90)
        f_med = _find_font(50)
        f_sm = _find_font(36)

        _draw_centered(draw, "நன்றி!", self.h // 2 - 130, f_big,
                       theme["title"], self.w)
        _draw_centered(draw, "Thank You for Watching!", self.h // 2 - 10,
                       f_med, theme["text"], self.w)
        _draw_centered(draw, "Like | Subscribe | Share | Comment",
                       self.h // 2 + 80, f_sm, theme["accent"], self.w)
        return img

    def _make_sentence_frame(
        self,
        bg_path: Path,
        sa: SentenceAudio,
        theme: dict,
    ) -> Image.Image:
        """Build one frame: darkened background + section label + subtitle."""
        # Load and darken background
        try:
            bg = Image.open(bg_path).convert("RGB")
            if bg.size != (self.w, self.h):
                bg = bg.resize((self.w, self.h), Image.LANCZOS)
            bg = ImageEnhance.Brightness(bg).enhance(0.40)
        except Exception:
            bg = Image.new("RGB", (self.w, self.h), (15, 15, 40))

        draw = ImageDraw.Draw(bg)

        # Section label (top-left)
        f_label = _find_font(28)
        draw.text((50, 40), sa.section.upper(), fill=theme["accent"], font=f_label)

        # Thin accent line below label
        draw.line([(50, 80), (400, 80)], fill=theme["accent"], width=2)

        # Subtitle at the bottom with semi-transparent background
        f_sub = _find_font(40)
        lines = _wrap(sa.sentence, f_sub, self.w - 160)

        # Calculate subtitle area
        line_h = 55
        sub_h = len(lines) * line_h + 40
        sub_y = self.h - sub_h - 60

        # Semi-transparent black box
        overlay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        ov_draw.rounded_rectangle(
            [(60, sub_y), (self.w - 60, sub_y + sub_h)],
            radius=16,
            fill=(0, 0, 0, 170),
        )
        bg = bg.convert("RGBA")
        bg = Image.alpha_composite(bg, overlay).convert("RGB")
        draw = ImageDraw.Draw(bg)

        y = sub_y + 20
        for ln in lines:
            _draw_centered(draw, ln, y, f_sub, (255, 255, 255), self.w)
            y += line_h

        return bg

    # ── helpers ──────────────────────────────────────────────

    def _scene_bg(self, scene_idx: int, images: List[Path]) -> Path:
        """Pick the background image for a scene index."""
        if not images:
            return Path("/dev/null")
        idx = min(scene_idx, len(images) - 1)
        return images[idx]

    def _img_clip(self, img: Image.Image, duration: float, fade: bool = False):
        """Convert PIL Image to a moviepy ImageClip."""
        tmp = TEMP_DIR / f"frame_{id(img)}_{random.randint(0,99999)}.png"
        img.save(str(tmp))
        self._temp.append(str(tmp))
        clip = ImageClip(str(tmp)).set_duration(duration)
        if fade:
            clip = clip.fadein(0.5).fadeout(0.5)
        return clip

    def _cleanup(self):
        for f in self._temp:
            try:
                os.remove(f)
            except OSError:
                pass
        self._temp.clear()
