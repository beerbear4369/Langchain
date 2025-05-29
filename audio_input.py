import os  # For file operations
import time  # For delays and timing
import logging
from openai import OpenAI  # OpenAI API client
from httpx import TimeoutException # For specific exception handling
from config import OPENAI_API_KEY, MODEL_NAME # Import necessary configs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create an OpenAI client with your API key
# This should be done once, ideally.
# If OPENAI_API_KEY is None (e.g., not set in environment or config.json),
# OpenAI client will raise openai.AuthenticationError
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    client = None # Ensure client is None if initialization fails

def transcribe_audio(audio_file_path: str) -> str | None:
    """
    Transcribes audio to text using OpenAI's API.
    This function is designed for API usage and expects a file path.
    It does not handle microphone input or delete the file afterwards.

    Args:
        audio_file_path (str): Path to the audio file to transcribe.

    Returns:
        str: The transcribed text, or None if transcription failed.
    """
    if client is None:
        logging.error("OpenAI client is not initialized. Cannot transcribe audio.")
        return None

    if not os.path.exists(audio_file_path):
        logging.error(f"Audio file does not exist: {audio_file_path}")
        return None
        
    file_size = os.path.getsize(audio_file_path)
    if file_size == 0:
        logging.error(f"Audio file is empty: {audio_file_path}")
        return None
    
    # A very rough estimate for minimum valid size (e.g. ~0.1s of 16-bit 44.1kHz audio)
    # This helps catch corrupted or truncated files early.
    min_valid_size = 1000 # Adjusted from 4000, as very short valid audio might be smaller.
    if file_size < min_valid_size:
        logging.warning(f"Audio file is very small ({file_size} bytes): {audio_file_path}. May result in poor transcription.")
        # Not returning None here, as OpenAI might still process it.

    try:
        logging.info(f"Starting transcription for {audio_file_path}...")
        start_time = time.time()
        
        with open(audio_file_path, "rb") as audio_file:
            # Determine which model to use for transcription.
            # Using a general model like whisper-1 is common.
            # gpt-4o-mini-transcribe was mentioned, but whisper-1 is a standard.
            # Let's stick to whisper-1 for robustness unless a specific finetuned model is required.
            transcription_model = "whisper-1"
            # If MODEL_NAME from config is a specific transcription fine-tune, it could be used here,
            # but typically MODEL_NAME is for chat/completion models.
            # Example: if "transcribe" in MODEL_NAME: transcription_model = MODEL_NAME

            try:
                transcript_response = client.audio.transcriptions.create(
                    model=transcription_model,
                    file=audio_file,
                    # timeout=30 # httpx client used by OpenAI lib handles timeouts based on client config
                )
            except TimeoutException as e:
                logging.error(f"OpenAI API timeout during transcription for {audio_file_path}: {e}")
                return None
            except Exception as e: # Catch other OpenAI or network errors
                logging.error(f"OpenAI API error during transcription for {audio_file_path} with {transcription_model}: {e}")
                # Fallback to whisper-1 if a different model was attempted and failed,
                # though currently, we only use whisper-1.
                # if transcription_model != "whisper-1":
                #     logging.info(f"Falling back to whisper-1 for {audio_file_path}...")
                #     audio_file.seek(0) # Reset file pointer
                #     transcript_response = client.audio.transcriptions.create(
                #         model="whisper-1",
                #         file=audio_file,
                #     )
                # else:
                raise # Re-raise if whisper-1 itself failed or no other model to fallback to

        elapsed_time = time.time() - start_time
        logging.info(f"Transcription for {audio_file_path} completed in {elapsed_time:.2f} seconds.")
        
        return transcript_response.text

    except Exception as e:
        logging.error(f"Error during transcription process for {audio_file_path}: {e}")
        return None

# Removed record_audio, check_for_keypress, and test_audio_transcription as they are CLI-specific.
# The main functionality for the API is transcribe_audio taking a file path.