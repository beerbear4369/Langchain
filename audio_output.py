import tempfile
import os
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
from config import OPENAI_API_KEY, DEFAULT_VOICE

client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech(text, voice=DEFAULT_VOICE):
    """
    Convert text to speech using OpenAI's TTS (Text-to-Speech) API.
    
    This function:
    1. Takes a text input and voice selection
    2. Sends it to OpenAI's TTS API
    3. Saves the audio to a temporary file
    4. Plays the audio
    5. Deletes the temporary file
    
    Args:
        text (str): The text to convert to speech
        voice (str): The voice to use (e.g., "alloy", "echo", "fable")
        
    Returns:
        None: The function plays audio but doesn't return a value
    """
    if not text:
        return
    
    try:
        # Step 2: Create a temporary file to store the audio
        # This file will be deleted after playback
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.close()
        
        # Step 3: Generate speech from text using OpenAI's TTS API
        # - model="tts-1": The text-to-speech model to use
        # - voice: Which voice to use (from config or parameter)
        # - input: The text to convert to speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Step 4: Save the audio to the temporary file
        response.stream_to_file(temp_file.name)
        
        # Step 5: Play the audio file
        play_audio(temp_file.name)
        
        # Step 6: Clean up by deleting the temporary file
        os.unlink(temp_file.name)
        
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")

def text_to_speech_api(text, output_path, voice=DEFAULT_VOICE):
    """
    Convert text to speech using OpenAI's TTS API and save to a specific file path.
    This version is designed for API use where we need to save files for serving.
    
    Args:
        text (str): The text to convert to speech
        output_path (str): Path where to save the audio file
        voice (str): The voice to use (e.g., "alloy", "echo", "fable")
        
    Returns:
        bool: True if successful, False if failed
    """
    if not text:
        return False
    
    try:
        # Generate speech from text using OpenAI's TTS API
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Save the audio to the specified file path
        response.stream_to_file(output_path)
        
        return True
        
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return False

def play_audio(file_path):
    """
    Play audio from a file using sounddevice.
    
    This function:
    1. Reads an audio file
    2. Plays it through the default audio output device
    3. Waits for playback to finish
    
    Args:
        file_path (str): Path to the audio file to play
        
    Returns:
        None
    """
    try:
        # Step 1: Load the audio file
        # This returns the audio data and sample rate
        data, fs = sf.read(file_path)
        
        # Step 2: Play the audio through the default output device
        sd.play(data, fs)
        
        # Step 3: Wait until audio playback is complete
        # This ensures the function doesn't return until the audio finishes
        sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}") 