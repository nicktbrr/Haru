import os
import time
import base64
import logging
from typing import Optional
import tempfile
from pathlib import Path

import google.generativeai as genai
from google.generativeai import GenerativeModel

from lumaai import LumaAI
from dotenv import load_dotenv
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


class GeminiMusicAnalyzer:
    """A class to handle music analysis using Google's Gemini AI."""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the music analyzer.

        Args:
            model_name (str): The name of the Gemini model to use
        """
        self.model = GenerativeModel(model_name)
        self.supported_audio_formats = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}

    def convert_audio_to_base64(self, audio_path: str) -> str:
        """
        Convert an audio file to base64 encoding.

        Args:
            audio_path (str): Path to the audio file

        Returns:
            str: Base64 encoded audio data

        Raises:
            ValueError: If the file extension is not supported
            FileNotFoundError: If the audio file doesn't exist
            Exception: For other audio processing errors
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        file_ext = audio_path.suffix.lower()
        if file_ext not in self.supported_audio_formats:
            raise ValueError(
                f"Unsupported audio format: {file_ext}. Supported formats: {self.supported_audio_formats}"
            )

        try:
            audio = AudioSegment.from_file(str(audio_path))
            logger.info(f"Successfully loaded audio file: {audio_path}")
        except Exception as e:
            logger.error(f"Error loading audio file: {e}")
            raise

        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as temp_file:
            temp_wav_path = temp_file.name

        try:
            audio.export(temp_wav_path, format="wav")
            logger.info("Successfully converted audio to WAV format")

            with open(temp_wav_path, "rb") as audio_file:
                encoded_audio = base64.b64encode(audio_file.read()).decode(
                    "utf-8"
                )
                logger.info("Successfully encoded audio to base64")

            return encoded_audio
        finally:
            # Clean up temporary file
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
                logger.debug("Cleaned up temporary WAV file")

    def describe_music(
        self,
        audio_path: str,
        prompt_template: Optional[str] = None,
        max_retries: int = 3,
    ) -> str:
        """
        Analyze music using Gemini AI.

        Args:
            audio_path (str): Path to the audio file
            prompt_template (Optional[str]): Custom prompt template for analysis
            max_retries (int): Maximum number of retries for API calls

        Returns:
            str: Generated description of the music

        Raises:
            Exception: If the API call fails after max retries
        """
        default_prompt = """
        You are a famous music reviewer listening to an audio file containing music. Please write the following. 
        1. A description of the music broken into 6 distinct sections in a story format. 
        2. Within those 6 sections the mood of the music. 
        3. Keep a consistent description of any characters or common locations. 
        4. Vivid scenery depictions that match the music. 
        Limit any response to 4000 Characters or less. 
        """

        prompt = prompt_template or default_prompt

        try:
            encoded_audio = self.convert_audio_to_base64(audio_path)

            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": encoded_audio,
                            }
                        },
                    ],
                }
            ]

            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(contents)
                    if response.text:
                        logger.info("Successfully generated music description")
                        return response.text
                    else:
                        logger.warning(
                            f"Empty response from Gemini (attempt {attempt + 1}/{max_retries})"
                        )
                except Exception as e:
                    logger.error(
                        f"Error in API call (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(1)  # Wait before retrying

        except Exception as e:
            logger.error(f"Failed to analyze music: {e}")
            raise


class LumaAIConnector:
    """Class to generate a Video from LumaAI."""

    def __init__(self):
        """Initialize the Video Generator using LumaAI."""
        self.luma = LumaAI()

    def generate_video(self, prompt: str):
        """Uses LumaAI to generate videos based on a prompt.

        Args:
            prompt (str): Description of what kind of video to generate.

        Raises:
            RuntimeError: Raises an error if a video can not be generated.

        Returns:
            URL: URL to the video file.
        """
        generation = self.luma.generations.create(
            prompt=prompt,
        )
        completed = False
        while not completed:
            generation = self.luma.generations.get(id=generation.id)
            if generation.state == "completed":
                completed = True
            elif generation.state == "failed":
                raise RuntimeError(
                    f"Generation failed: {generation.failure_reason}"
                )
            print("Dreaming")
            time.sleep(3)

        return generation.assets.video


def generate_video(prompt: str):
    """Uses LumaAI to generate videos based on a prompt.

    Args:
        prompt (str): Description of what kind of video to generate.

    Raises:
        RuntimeError: Raises an error if a video can not be generated.

    Returns:
        URL: URL to the video file.
    """
    luma = LumaAI()
    generation = luma.generations.create(
        prompt=prompt,
    )
    completed = False
    while not completed:
        generation = luma.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(
                f"Generation failed: {generation.failure_reason}"
            )
        print("Dreaming")
        time.sleep(3)

    return generation.assets.video


if __name__ == "__main__":
    try:
        analyzer = GeminiMusicAnalyzer()
        # importing music files
        music_file_path = "TEMP_MUSIC_PATH"
        description = analyzer.describe_music(music_file_path)
        LumaAI = LumaAIConnector()
        video_url = (LumaAI.generate_video(prompt=description),)
        # print(description)
    except Exception as e:
        logger.error(f"Error in main: {e}")
