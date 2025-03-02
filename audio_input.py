import wave  # For working with WAV audio files
import pyaudio  # For recording audio from microphone
import os  # For file operations
import tempfile  # For creating temporary files
from openai import OpenAI  # OpenAI API client
from config import OPENAI_API_KEY, SAMPLE_RATE, CHANNELS, CHUNK_SIZE, RECORD_SECONDS

# Create an OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)

def record_audio(duration=RECORD_SECONDS):
    """
    Records audio from the user's microphone.
    
    This function:
    1. Initializes the audio recording system
    2. Records audio for the specified duration
    3. Saves the recording to a temporary WAV file
    4. Returns the path to that file
    
    Args:
        duration (int): How long to record in seconds (default from config)
        
    Returns:
        str: Path to the recorded audio file
    """
    print("Recording...")
    
    # Step 1: Initialize PyAudio - this is the library that handles microphone input
    p = pyaudio.PyAudio()
    
    # Step 2: Open an audio stream to record from the microphone
    # - format=paInt16: Record 16-bit audio (CD quality)
    # - channels: Mono (1) or stereo (2)
    # - rate: Sample rate in Hz (44100 = CD quality)
    # - input=True: We want to record, not play audio
    # - frames_per_buffer: How many samples to process at once
    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    # Step 3: Record audio in chunks and store in a list
    frames = []  # This will hold all the audio data
    
    # Calculate how many chunks we need to record based on duration
    for i in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
        data = stream.read(CHUNK_SIZE)  # Read one chunk of audio
        frames.append(data)  # Add to our list
    
    print("Recording finished.")
    
    # Step 4: Clean up the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Step 5: Create a temporary WAV file to store the recording
    # This file will be deleted after transcription
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    
    # Step 6: Write the audio data to the WAV file
    wf = wave.open(temp_file.name, 'wb')  # Open file for writing binary data
    wf.setnchannels(CHANNELS)  # Set number of channels
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))  # Set sample width
    wf.setframerate(SAMPLE_RATE)  # Set sample rate
    wf.writeframes(b''.join(frames))  # Write all audio frames at once
    wf.close()  # Close the file
    
    # Return the path to the temporary audio file
    return temp_file.name

def transcribe_audio(audio_file_path):
    """
    Transcribes an audio file to text using OpenAI's Whisper API.
    
    This function:
    1. Opens the audio file
    2. Sends it to OpenAI's Whisper API for transcription
    3. Deletes the temporary file
    4. Returns the transcribed text
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text, or None if transcription failed
    """
    try:
        # Step 1: Open the audio file in binary mode
        with open(audio_file_path, "rb") as audio_file:
            # Step 2: Send the file to OpenAI's Whisper API for transcription
            transcription = client.audio.transcriptions.create(
                model="whisper-1",  # The Whisper model to use
                file=audio_file  # The audio file object
            )
        
        # Step 3: Clean up by deleting the temporary file
        # This prevents filling up disk space with recordings
        os.unlink(audio_file_path)
        
        # Step 4: Return the transcribed text
        return transcription.text
    except Exception as e:
        # Handle any errors that might occur during transcription
        print(f"Error during transcription: {e}")
        
        # Clean up the temporary file even if transcription failed
        os.unlink(audio_file_path)
        
        # Return None to indicate transcription failed
        return None 