"""
Cloud Text-to-Speech - Google Cloud TTS integration
Better quality Tamil speech synthesis using Google Cloud
"""

import logging
from typing import Optional
from pathlib import Path
from google.cloud import texttospeech
from google.oauth2 import service_account
import os

logger = logging.getLogger(__name__)


class CloudTTSGenerator:
    """Generate high-quality Tamil speech using Google Cloud TTS"""
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None,
                 output_dir: str = "audio_output"):
        """
        Initialize Cloud TTS Generator
        
        Args:
            project_id: GCP project ID
            credentials_path: Path to service account JSON
            output_dir: Directory to save audio files
        """
        self.project_id = project_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize TTS client
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        else:
            self.client = texttospeech.TextToSpeechClient()
        
        logger.info("Cloud TTS initialized")
    
    def generate_speech(self, text: str, filename: str, 
                       voice_name: str = "ta-IN-Standard-A",
                       speaking_rate: float = 1.0) -> Optional[str]:
        """
        Generate speech from Tamil text using Google Cloud TTS
        
        Args:
            text: Tamil text to convert
            filename: Output filename (without extension)
            voice_name: Voice to use (ta-IN-Standard-A, ta-IN-Standard-B, etc.)
            speaking_rate: Speaking rate (0.25 to 4.0)
            
        Returns:
            Path to generated audio file
        """
        try:
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code="ta-IN",
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=0.0,
                volume_gain_db=0.0
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save the response to a file
            output_path = self.output_dir / f"{filename}.mp3"
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            
            logger.info(f"Generated speech: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def generate_script_audio(self, script: str, filename: str,
                             voice_name: str = "ta-IN-Standard-A",
                             speaking_rate: float = 1.0) -> Optional[str]:
        """
        Generate audio from complete script
        Processes sentence by sentence for better quality
        
        Args:
            script: Complete Tamil script
            filename: Output filename
            voice_name: Voice to use
            speaking_rate: Speaking rate
            
        Returns:
            Path to generated audio file
        """
        try:
            # Split script into sentences
            sentences = script.split('\n')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                logger.error("No sentences to process")
                return None
            
            # Generate audio for complete script
            output_path = self.generate_speech(
                script,
                filename,
                voice_name=voice_name,
                speaking_rate=speaking_rate
            )
            
            logger.info(f"Generated complete script audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating script audio: {e}")
            return None
    
    def list_voices(self) -> list:
        """List available Tamil voices"""
        try:
            response = self.client.list_voices(language_code="ta-IN")
            
            voices = []
            for voice in response.voices:
                voices.append({
                    'name': voice.name,
                    'ssml_gender': voice.ssml_gender,
                    'natural_sample_rate_hertz': voice.natural_sample_rate_hertz
                })
            
            logger.info(f"Available Tamil voices: {len(voices)}")
            return voices
            
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    tts = CloudTTSGenerator(project_id="your-project-id")
    
    # List available voices
    voices = tts.list_voices()
    for voice in voices:
        print(f"Voice: {voice['name']}")
    
    # Generate speech
    # audio_path = tts.generate_speech("வணக்கம் நண்பர்களே!", "greeting")
    # print(f"Audio: {audio_path}")
