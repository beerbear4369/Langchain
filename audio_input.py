import wave  # For working with WAV audio files
import os  # For file operations
import tempfile  # For creating temporary files
import threading  # For handling keyboard input while recording
import platform  # For detecting the operating system
import time  # For delays and timing
from openai import OpenAI  # OpenAI API client
from config import OPENAI_API_KEY, SAMPLE_RATE, CHANNELS, CHUNK_SIZE, RECORD_SECONDS

# Conditional import for desktop audio recording
try:
    import pyaudio  # For recording audio from microphone
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: pyaudio not available - record_audio function disabled")

# Create an OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)

def record_audio(duration=RECORD_SECONDS, min_duration=0.5):
    """
    Records audio from the user's microphone until a key is pressed or max duration is reached.
    
    This function:
    1. Initializes the audio recording system
    2. Records audio until the user presses any key or max duration is reached
    3. Saves the recording to a temporary WAV file
    4. Returns the path to that file
    
    Args:
        duration (int): Maximum recording time in seconds (default from config)
        min_duration (float): Minimum recording duration in seconds to ensure valid audio
        
    Returns:
        str: Path to the recorded audio file
    """
    if not PYAUDIO_AVAILABLE:
        raise ImportError("pyaudio is not available - cannot record audio")
        
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
        
        # Track recording duration to ensure minimum length
        recording_start = time.time()
        
        # Record buffer period (capture audio before the user is fully ready)
        # This ensures we don't miss the beginning of speech
        buffer_chunks = int(SAMPLE_RATE / CHUNK_SIZE * 0.2)  # 200ms buffer
        for i in range(buffer_chunks):
            data = stream.read(CHUNK_SIZE)  # Read one chunk of audio
            frames.append(data)  # Add to our list
        
        print("Ready! Speak now...")
        
        # Record until key is pressed or max duration is reached
        for i in range(max_chunks):
            # Read current chunk before checking stop flag
            # This ensures we capture audio right up to the stopping point
            data = stream.read(CHUNK_SIZE)  # Read one chunk of audio
            frames.append(data)  # Add to our list
            
            # Calculate recording duration
            recording_duration = time.time() - recording_start
            
            # Visual indicator of recording progress - update more frequently
            if i % 5 == 0:  # Update every 5 chunks for more responsive feedback
                remaining = duration - recording_duration
                print(f"\rRecording... {remaining:.1f}s remaining (or press any key to stop)", end="")
            
            # Check if we should stop AFTER capturing the current chunk
            if stop_recording.is_set() and recording_duration >= min_duration:
                # Only stop if we've recorded at least the minimum duration
                # Add a small tail buffer to catch the end of speech
                tail_chunks = int(SAMPLE_RATE / CHUNK_SIZE * 0.2)  # 200ms buffer
                for _ in range(tail_chunks):
                    data = stream.read(CHUNK_SIZE)
                    frames.append(data)
                break
        
        # Force minimum recording duration if stopped too early
        if recording_duration < min_duration:
            print(f"\rEnsuring minimum recording duration ({min_duration}s)...", end="")
            additional_chunks = int(SAMPLE_RATE / CHUNK_SIZE * (min_duration - recording_duration))
            for _ in range(additional_chunks):
                data = stream.read(CHUNK_SIZE)
                frames.append(data)
        
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
    Transcribes audio to text using OpenAI's GPT-4o-mini-transcribe API with fallback.
    
    This function:
    1. Opens the audio file
    2. Tries to send it to OpenAI's transcription API
    3. Falls back to whisper-1 model if the primary model fails
    4. Deletes the temporary file
    5. Returns the transcribed text
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text, or None if transcription failed
    """
    import time
    from httpx import TimeoutException
    
    # Ensure the file exists before attempting transcription
    if not os.path.exists(audio_file_path):
        print("Error: Audio file does not exist")
        return None
        
    # Check if the file is empty or too small
    file_size = os.path.getsize(audio_file_path)
    if file_size == 0:
        print("Error: Audio file is empty")
        return None
    
    # Check if file is too small (less than approximately 0.1s of audio)
    # A very rough estimate based on typical WAV file sizes
    min_valid_size = 4000  # ~0.1s of 16-bit 44.1kHz audio
    if file_size < min_valid_size:
        print(f"Error: Audio file too small ({file_size} bytes), needs at least {min_valid_size} bytes")
        return None
    
    try:
        print("Starting transcription...")
        start_time = time.time()
        
        # Step 1: Open the audio file in binary mode
        with open(audio_file_path, "rb") as audio_file:
            try:
                # Step 2: Send the file to OpenAI's Whisper API for transcription
                # with a timeout to prevent hanging
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",  # Using the stable and reliable Whisper model
                    file=audio_file,  # The audio file object
                    timeout=30  # Add a timeout to prevent hanging indefinitely
                )
            except (TimeoutException, Exception) as e:
                print(f"Whisper transcription failed: {e}")
                # No fallback needed since whisper-1 is the most reliable model
                raise
        
        # Report time taken for transcription
        elapsed_time = time.time() - start_time
        print(f"Transcription completed in {elapsed_time:.2f} seconds")
        
        # Step 3: Clean up by deleting the temporary file
        try:
            os.unlink(audio_file_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file: {e}")
        
        # Step 4: Return the transcribed text
        return transcription.text
    except Exception as e:
        # Handle any errors that might occur during transcription
        print(f"Error during transcription: {e}")
        
        # Clean up the temporary file even if transcription failed
        try:
            os.unlink(audio_file_path)
        except Exception as file_e:
            print(f"Warning: Could not delete temporary file: {file_e}")
        
        # Return None to indicate transcription failed
        return None

def test_audio_transcription():
    """
    Test function to verify the audio recording and transcription functionality.
    """
    print("=== Testing Audio Transcription with gpt-4o-mini-transcribe ===")
    print("This test will record a short audio clip and transcribe it.")
    print("Please speak clearly for a few seconds after recording starts.\n")
    
    # Record a short audio clip (5 seconds by default or use config value)
    print("Starting audio recording...")
    audio_file = record_audio()
    
    if audio_file:
        print(f"Audio recorded successfully to temporary file: {audio_file}")
        print("Transcribing audio...")
        
        # Transcribe the recorded audio
        transcription = transcribe_audio(audio_file)
        
        if transcription:
            print("\nTranscription successful!")
            print("=" * 50)
            print("Transcribed text:")
            print(transcription)
            print("=" * 50)
            return True
        else:
            print("Transcription failed.")
            return False
    else:
        print("Audio recording failed.")
        return False

# Run the test function if this script is executed directly
if __name__ == "__main__":
    test_audio_transcription() 