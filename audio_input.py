import wave  # For working with WAV audio files
import pyaudio  # For recording audio from microphone
import os  # For file operations
import tempfile  # For creating temporary files
import threading  # For handling keyboard input while recording
import platform  # For detecting the operating system
from openai import OpenAI  # OpenAI API client
from config import OPENAI_API_KEY, SAMPLE_RATE, CHANNELS, CHUNK_SIZE, RECORD_SECONDS

# Create an OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)

def record_audio(duration=RECORD_SECONDS):
    """
    Records audio from the user's microphone until a key is pressed or max duration is reached.
    
    This function:
    1. Initializes the audio recording system
    2. Records audio until the user presses any key or max duration is reached
    3. Saves the recording to a temporary WAV file
    4. Returns the path to that file
    
    Args:
        duration (int): Maximum recording time in seconds (default from config)
        
    Returns:
        str: Path to the recorded audio file
    """
    print("Recording... Press any key to stop recording")
    
    # Flag to indicate if recording should stop
    stop_recording = threading.Event()
    
    # Function to check for key press in a separate thread
    def check_for_keypress():
        # Use the appropriate method based on the operating system
        if platform.system() == 'Windows':
            # Windows-specific implementation
            import msvcrt
            while not stop_recording.is_set():
                # Check if a key has been pressed
                if msvcrt.kbhit():
                    # Read the key to clear the buffer
                    msvcrt.getch()
                    print("\nStopping recording...")
                    stop_recording.set()
                    break
                # Small sleep to prevent high CPU usage
                import time
                time.sleep(0.1)
        else:
            # Unix-like systems (Linux, macOS) implementation
            import sys
            import select
            while not stop_recording.is_set():
                # Check if there's data available to read from stdin
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    # Read the input to clear the buffer
                    sys.stdin.readline()
                    print("\nStopping recording...")
                    stop_recording.set()
                    break
    
    # Start the keypress detection thread
    keypress_thread = threading.Thread(target=check_for_keypress)
    keypress_thread.daemon = True
    keypress_thread.start()
    
    try:
        # Step 1: Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Step 2: Open an audio stream to record from the microphone
        stream = p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        # Step 3: Record audio in chunks and store in a list
        frames = []  # This will hold all the audio data
        
        # Calculate maximum number of chunks based on duration
        max_chunks = int(SAMPLE_RATE / CHUNK_SIZE * duration)
        
        # Record until key is pressed or max duration is reached
        for i in range(max_chunks):
            if stop_recording.is_set():
                break
                
            data = stream.read(CHUNK_SIZE)  # Read one chunk of audio
            frames.append(data)  # Add to our list
            
            # Visual indicator of recording progress
            if i % 10 == 0:  # Update every 10 chunks
                remaining = duration - (i * CHUNK_SIZE / SAMPLE_RATE)
                print(f"\rRecording... {remaining:.1f}s remaining (or press any key to stop)", end="")
        
        print("\nRecording finished.")
        
        # Step 4: Clean up the audio stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Step 5: Create a temporary file to store the audio
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.close()
        
        # Step 6: Save the recorded audio to a WAV file
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_file.name
    
    finally:
        # Make sure we set the stop flag to terminate the thread
        stop_recording.set()
        # Wait for the thread to finish
        keypress_thread.join(timeout=0.5)

def transcribe_audio(audio_file_path):
    """
    Transcribes audio to text using OpenAI's Whisper API.
    
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