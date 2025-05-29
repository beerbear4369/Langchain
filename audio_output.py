import os
import logging
from openai import OpenAI
from config import OPENAI_API_KEY, DEFAULT_VOICE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def text_to_speech_file(text: str, output_file_path: str, voice: str = DEFAULT_VOICE) -> str | None:
    """
    Convert text to speech using OpenAI's TTS API and saves it to a specified file path.

    Args:
        text (str): The text to convert to speech.
        output_file_path (str): The full path where the audio file should be saved.
        voice (str): The voice to use (e.g., "alloy", "echo", "fable").

    Returns:
        str: The path to the saved audio file if successful, None otherwise.
    """
    if client is None:
        logging.error("OpenAI client is not initialized. Cannot perform text-to-speech.")
        return None

    if not text:
        logging.warning("Text-to-speech called with empty text.")
        return None
    
    if not output_file_path:
        logging.error("Output file path is not provided for text-to-speech.")
        return None

    try:
        logging.info(f"Generating speech for text: '{text[:50]}...' and saving to {output_file_path}")
        
        response = client.audio.speech.create(
            model="tts-1",  # Standard TTS model
            voice=voice,
            input=text
        )
        
        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir: # If output_file_path includes a directory
            os.makedirs(output_dir, exist_ok=True)
            
        response.stream_to_file(output_file_path)
        logging.info(f"Speech audio successfully saved to {output_file_path}")
        
        return output_file_path
        
    except Exception as e:
        logging.error(f"Error in text-to-speech conversion for output path {output_file_path}: {e}")
        return None

# Removed play_audio function as it's CLI-specific and uses sounddevice/soundfile.
# The API will provide audio files via URL, to be played by the client.