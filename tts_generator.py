"""
Text-to-Speech Generator for Tamil
Uses edge-tts (Microsoft Edge TTS) - free, high quality Tamil voices, works headless
"""

import os
import asyncio
import logging
from typing import Optional
from pathlib import Path
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Available Tamil voices (all free via edge-tts)
TAMIL_VOICES = {
    "male_in": "ta-IN-ValluvarNeural",      # Indian Tamil Male
    "female_in": "ta-IN-PallaviNeural",      # Indian Tamil Female
    "male_lk": "ta-LK-KumarNeural",         # Sri Lankan Tamil Male
    "female_lk": "ta-LK-SaranyaNeural",     # Sri Lankan Tamil Female
    "male_my": "ta-MY-SuryaNeural",         # Malaysian Tamil Male
    "female_my": "ta-MY-KaniNeural",        # Malaysian Tamil Female
    "male_sg": "ta-SG-VenbaNeural",         # Singaporean Tamil Male
    "female_sg": "ta-SG-AnbuNeural",        # Singaporean Tamil Female
}


class TamilTTSGenerator:
    """Generate Tamil speech from text using edge-tts"""

    def __init__(self, output_dir: str = "audio_output", voice: str = "male_in"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.voice = TAMIL_VOICES.get(voice, voice)
        logger.info(f"TTS initialized with voice: {self.voice}")

    async def _generate_speech_async(self, text: str, output_path: str,
                                      rate: str = "+0%", volume: str = "+0%"):
        """Generate speech asynchronously using edge-tts"""
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=rate, volume=volume)
        await communicate.save(output_path)

    def generate_speech(self, text: str, filename: str,
                        rate: str = "+0%", volume: str = "+0%") -> str:
        """
        Generate speech from Tamil text

        Args:
            text: Tamil text to convert to speech
            filename: Output filename (without extension)
            rate: Speech rate (e.g., "+10%", "-10%")
            volume: Volume (e.g., "+10%", "-10%")

        Returns:
            Path to generated audio file (mp3)
        """
        try:
            output_path = str(self.output_dir / f"{filename}.mp3")

            # Run async edge-tts
            asyncio.run(self._generate_speech_async(text, output_path, rate, volume))

            logger.info(f"Generated speech: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise

    def generate_script_audio(self, script: str, filename: str,
                               rate: str = "+0%") -> str:
        """
        Generate audio from complete script.
        Breaks script into paragraphs for better quality.

        Args:
            script: Complete Tamil script
            filename: Output filename
            rate: Speech rate

        Returns:
            Path to generated audio file (mp3)
        """
        try:
            # Split script into paragraphs/sentences
            paragraphs = [p.strip() for p in script.split('\n') if p.strip()]

            audio_files = []

            for idx, paragraph in enumerate(paragraphs):
                if not paragraph or len(paragraph) < 3:
                    continue

                part_file = f"{filename}_part_{idx}"
                try:
                    audio_path = self.generate_speech(paragraph, part_file, rate=rate)
                    audio_files.append(audio_path)
                except Exception as e:
                    logger.warning(f"Error generating part {idx}: {e}")
                    continue

            if not audio_files:
                raise RuntimeError("No audio segments were generated")

            # Combine all audio files
            combined_audio = self._combine_audio_files(audio_files)

            # Save combined audio
            output_path = str(self.output_dir / f"{filename}_combined.mp3")
            combined_audio.export(output_path, format="mp3", bitrate="192k")

            # Clean up temporary files
            for audio_file in audio_files:
                try:
                    os.remove(audio_file)
                except OSError:
                    pass

            logger.info(f"Generated complete script audio: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating script audio: {e}")
            raise

    def _combine_audio_files(self, audio_files: list) -> AudioSegment:
        """Combine multiple audio files with pauses between them"""
        combined = AudioSegment.empty()
        gap = AudioSegment.silent(duration=700)  # 700ms gap between paragraphs

        for audio_file in audio_files:
            try:
                audio = AudioSegment.from_mp3(audio_file)
                combined += audio + gap
            except Exception as e:
                logger.warning(f"Error loading audio file {audio_file}: {e}")

        return combined

    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of an audio file in seconds"""
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    tts = TamilTTSGenerator()

    # Test Tamil text
    test_text = "வணக்கம் நண்பர்களே! இந்த வீடியோவில் நாம் தமிழ் வரலாறு பற்றி பேசப் போகிறோம்."

    audio_path = tts.generate_speech(test_text, "test_audio")
    print(f"Generated audio: {audio_path}")

    duration = tts.get_audio_duration(audio_path)
    print(f"Duration: {duration:.1f} seconds")
