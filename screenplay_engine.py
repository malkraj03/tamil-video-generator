"""
Screenplay Engine - breaks a Gemini-generated Tamil script into
timed scenes suitable for video composition.

Each scene contains:
  section   – section name (Hook, Introduction, etc.)
  narration – Tamil text for TTS
  sentences – list of individual sentences (for subtitle timing)
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Section markers written by the Gemini script engine
_SECTION_RE = re.compile(r"\[SECTION:\s*(.+?)\]", re.IGNORECASE)


def _split_tamil_sentences(text: str) -> List[str]:
    """Split Tamil text into sentences on ., !, ? and newlines."""
    # Split on sentence-ending punctuation or double newlines
    parts = re.split(r"(?<=[.!?।])\s+|\n{2,}", text)
    sentences = []
    for p in parts:
        p = p.strip()
        if p and len(p) > 2:
            sentences.append(p)
    return sentences


def build_screenplay(script: str) -> List[Dict]:
    """
    Parse a [SECTION:]-tagged Tamil script into a list of scenes.

    Returns list of dicts:
      {
        "section": str,          # e.g. "Hook", "Main Content Part 1"
        "narration": str,        # full text for this section
        "sentences": [str, ...], # individual sentences for subtitles
      }
    """
    # Find all section markers and their positions
    markers = [(m.start(), m.end(), m.group(1).strip())
               for m in _SECTION_RE.finditer(script)]

    if not markers:
        logger.warning("No [SECTION:] markers found; treating entire script as one scene")
        sentences = _split_tamil_sentences(script)
        return [{
            "section": "Full Script",
            "narration": script,
            "sentences": sentences if sentences else [script],
        }]

    scenes: List[Dict] = []
    for i, (start, end, name) in enumerate(markers):
        # Text runs from end of this marker to start of the next (or end of script)
        next_start = markers[i + 1][0] if i + 1 < len(markers) else len(script)
        text = script[end:next_start].strip()

        if not text:
            continue

        sentences = _split_tamil_sentences(text)
        if not sentences:
            continue

        scenes.append({
            "section": name,
            "narration": text,
            "sentences": sentences,
        })

    if not scenes:
        sentences = _split_tamil_sentences(script)
        scenes.append({
            "section": "Full Script",
            "narration": script,
            "sentences": sentences if sentences else [script],
        })

    logger.info(
        f"Screenplay: {len(scenes)} scenes, "
        f"{sum(len(s['sentences']) for s in scenes)} sentences total"
    )
    return scenes


if __name__ == "__main__":
    sample = """[SECTION: Hook]
இது ஒரு சோதனை hook வாக்கியம். இரண்டாவது வாக்கியம்.

[SECTION: Introduction]
Introduction பகுதி இங்கே. இது நீளமான பகுதி.

[SECTION: Conclusion]
முடிவுரை. நன்றி!
"""
    for sc in build_screenplay(sample):
        print(f"[{sc['section']}] {len(sc['sentences'])} sentences")
