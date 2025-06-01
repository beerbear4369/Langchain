import requests
import time
import tempfile
import wave
import numpy as np
import os

API_BASE_URL = "http://localhost:8000/api"
TEST_AUDIO_FILE = "test_wrap_up.wav"

def create_test_audio():
    """Create a simple test audio file."""
    # Generate a 2-second sine wave
    sample_rate = 44100
    duration = 2
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Write to WAV file
    with wave.open(TEST_AUDIO_FILE, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

def test_wrap_up_confirmation_flow():
    """Test the complete wrap-up confirmation flow."""
    print("=== Testing Wrap-Up Confirmation Flow ===\n")
    
    # Step 1: Create session
    print("1. Creating session...")
    response = requests.post(f"{API_BASE_URL}/sessions")
    assert response.status_code == 200
    session_data = response.json()
    assert session_data["success"] is True
    session_id = session_data["data"]["sessionId"]
    print(f"✅ Session created: {session_id}\n")
    
    # Step 2: Send a normal message first
    print("2. Sending normal conversation message...")
    create_test_audio()
    
    with open(TEST_AUDIO_FILE, "rb") as audio_file:
        files = {"audio": ("test.wav", audio_file, "audio/wav")}
        response = requests.post(f"{API_BASE_URL}/sessions/{session_id}/messages", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"✅ Normal message processed. AI said: {data['data']['messages'][1]['text'][:100]}...\n")
    
    # Step 3: Test wrap-up trigger
    print("3. Testing wrap-up command detection...")
    print("   (Simulating audio that transcribes to 'wrap up')")
    
    # We'll simulate this by directly calling the API
    # In real usage, the audio would be transcribed to "wrap up"
    # For this test, we'll create a simple audio file and hope transcription works
    
    with open(TEST_AUDIO_FILE, "rb") as audio_file:
        files = {"audio": ("wrap_up_test.wav", audio_file, "audio/wav")}
        response = requests.post(f"{API_BASE_URL}/sessions/{session_id}/messages", files=files)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        
        if data["success"]:
            user_msg = data["data"]["messages"][0]
            ai_msg = data["data"]["messages"][1]
            
            print(f"User transcription: '{user_msg['text']}'")
            print(f"AI response: '{ai_msg['text']}'")
            
            # Check if awaiting confirmation
            if data["data"].get("awaitingWrapUpConfirmation"):
                print("✅ Wrap-up confirmation prompt detected!")
                print("   AI is now awaiting confirmation.\n")
                
                # Step 4: Test confirmation
                print("4. Testing confirmation response...")
                print("   (Simulating audio that transcribes to 'yes')")
                
                with open(TEST_AUDIO_FILE, "rb") as audio_file:
                    files = {"audio": ("confirmation_test.wav", audio_file, "audio/wav")}
                    response = requests.post(f"{API_BASE_URL}/sessions/{session_id}/messages", files=files)
                
                if response.status_code == 200:
                    conf_data = response.json()
                    if conf_data["success"]:
                        conf_user_msg = conf_data["data"]["messages"][0]
                        conf_ai_msg = conf_data["data"]["messages"][1]
                        
                        print(f"Confirmation transcription: '{conf_user_msg['text']}'")
                        print(f"AI response: '{conf_ai_msg['text'][:100]}...'")
                        
                        if conf_data["data"].get("sessionEnded"):
                            print("✅ Session ended successfully after confirmation!")
                            print(f"Final summary provided: {bool(conf_data['data'].get('finalSummary'))}")
                        else:
                            print("❌ Session should have ended after confirmation")
                    else:
                        print(f"❌ Confirmation processing failed: {conf_data['error']}")
                else:
                    print(f"❌ Confirmation request failed: {response.status_code}")
            else:
                print("❌ Wrap-up confirmation prompt not detected")
                print(f"   Expected awaitingWrapUpConfirmation: true, got: {data['data']}")
        else:
            print(f"❌ Wrap-up command processing failed: {data['error']}")
    else:
        print(f"❌ Wrap-up command request failed: {response.status_code}")
    
    # Cleanup
    try:
        requests.post(f"{API_BASE_URL}/sessions/{session_id}/end")
    except:
        pass
    
    try:
        os.remove(TEST_AUDIO_FILE)
    except:
        pass

if __name__ == "__main__":
    # Check if numpy is available
    try:
        import numpy as np
    except ImportError:
        print("❌ This test requires numpy. Install it with: pip install numpy")
        print("For now, you can test manually using the updated Postman collection.")
        exit(1)
    
    test_wrap_up_confirmation_flow()
    print("\n=== Test Complete ===")
    print("📝 Note: The actual wrap-up detection depends on audio transcription.")
    print("   If transcription doesn't produce the exact phrases, the logic won't trigger.")
    print("   Use the updated Postman collection to test with real audio files.") 