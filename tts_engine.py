"""
TTS Engine - Generate Tamil speech from screenplay scenes using edge-tts.

Produces one audio file per sentence so that timing data is available
for subtitle synchronisation and per-sentence image display.

Returns a list of SentenceAudio dicts:
  {
    "sentence": str,
    "audio_path": Path,
    "duration_s": float,
    "scene_idx": int,
    "section": str,
  }
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import edge_tts
from pydub import AudioSegment

from config import AUDIO_DIR, TTS_VOICE, TTS_DEFAULT_RATE, TTS_HOOK_RATE

logger = logging.getLogger(__name__)

# Section names that should be narrated slightly faster
_FAST_SECTIONS = {"Hook"}

# Pause between sentences (ms)
_SENTENCE_GAP_MS = 500
# Pause between scenes (ms)
_SCENE_GAP_MS = 900


@dataclass
class SentenceAudio:
    sentence: str
    audio_path: Path
    duration_s: float
    scene_idx: int
    section: str


class TTSEngine:
    """Generate Tamil narration audio from screenplay scenes."""

    def __init__(self, voice: str = TTS_VOICE, output_dir: Path = AUDIO_DIR):
        self.voice = voice
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    # ── async core ───────────────────────────────────────────

    async def _synthesize(self, text: str, path: str, rate: str):
        comm = edge_tts.Communicate(text, self.voice, rate=rate)
        await comm.save(path)

    def _tts(self, text: str, path: str, rate: str = TTS_DEFAULT_RATE):
        asyncio.run(self._synthesize(text, path, rate))

    # ── public API ───────────────────────────────────────────

    def generate_scene_audio(
        self, scenes: List[Dict], run_id: str
    ) -> List[SentenceAudio]:
        """
        Generate per-sentence audio for every scene.

        Args:
            scenes: list of screenplay scenes (from screenplay_engine).
            run_id: unique run identifier for file naming.

        Returns:
            list of SentenceAudio objects with timing data.
        """
        results: List[SentenceAudio] = []
        total_sentences = sum(len(sc.get("sentences", [])) for sc in scenes)
        done = 0

        for sc_idx, scene in enumerate(scenes):
            section = scene.get("section", "")
            rate = TTS_HOOK_RATE if section in _FAST_SECTIONS else TTS_DEFAULT_RATE

            for sent_idx, sentence in enumerate(scene.get("sentences", [])):
                if not sentence or len(sentence.strip()) < 3:
                    continue

                fname = f"{run_id}_s{sc_idx:02d}_{sent_idx:03d}.mp3"
                fpath = self.output_dir / fname

                try:
                    self._tts(sentence, str(fpath), rate=rate)
                    dur = self._duration(fpath)
                    results.append(SentenceAudio(
                        sentence=sentence,
                        audio_path=fpath,
                        duration_s=dur,
                        scene_idx=sc_idx,
                        section=section,
                    ))
                    done += 1
                    if done % 10 == 0:
                        logger.info(f"TTS progress: {done}/{total_sentences}")
                except Exception as e:
                    logger.warning(f"TTS failed for sentence {done}: {e}")
                    continue

        logger.info(f"TTS complete: {len(results)}/{total_sentences} sentences")
        return results

    def combine_audio(
        self, sentence_audios: List[SentenceAudio], run_id: str
    ) -> Path:
        """
        Combine per-sentence audio into a single narration track.

        Inserts short pauses between sentences and longer pauses
        between scenes.

        Returns path to combined MP3.
        """
        combined = AudioSegment.empty()
        sentence_gap = AudioSegment.silent(duration=_SENTENCE_GAP_MS)
        scene_gap = AudioSegment.silent(duration=_SCENE_GAP_MS)
        prev_scene = -1

        for sa in sentence_audios:
            try:
                seg = AudioSegment.from_file(str(sa.audio_path))
            except Exception as e:
                logger.warning(f"Could not load {sa.audio_path}: {e}")
                continue

            if sa.scene_idx != prev_scene and prev_scene >= 0:
                combined += scene_gap
            elif len(combined) > 0:
                combined += sentence_gap

            combined += seg
            prev_scene = sa.scene_idx

        out_path = self.output_dir / f"{run_id}_combined.mp3"
        combined.export(str(out_path), format="mp3", bitrate="192k")
        logger.info(f"Combined audio: {len(combined)/1000:.1f}s -> {out_path}")
        return out_path

    # ── helpers ──────────────────────────────────────────────

    @staticmethod
    def _duration(path: Path) -> float:
        try:
            return len(AudioSegment.from_file(str(path))) / 1000.0
        except Exception:
            return 0.0

    def cleanup(self, run_id: str):
        """Remove temporary per-sentence audio files for a run."""
        for f in self.output_dir.glob(f"{run_id}_s*.mp3"):
            try:
                f.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = TTSEngine()
    test_scenes = [{
        "section": "Hook",
        "narration": "வணக்கம்! இது ஒரு சோதனை.",
        "sentences": ["வணக்கம்!", "இது ஒரு சோதனை."],
    }]
    audios = engine.generate_scene_audio(test_scenes, "test")
    for a in audios:
        print(f"{a.section}: {a.duration_s:.1f}s - {a.sentence[:40]}")
