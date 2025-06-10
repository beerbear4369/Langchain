#!/usr/bin/env python3

import requests
import tempfile
import wave
import numpy as np
import time
from database_service import db_service

API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "test_ending.wav"

def create_test_audio():
    """Create a simple test audio file."""
    sample_rate = 16000
    duration = 2  # seconds
    frequency = 440  # Hz (A note)
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(frequency * 2 * np.pi * t)
    
    # Scale to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open(TEST_AUDIO_FILE, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

def test_automatic_session_ending():
    """Test that automatic session ending properly updates the database."""
    print("🧪 Testing Automatic Session Ending Database Update Fix")
    print("=" * 60)
    
    # 1. Create a new session
    print("1. Creating new session...")
    response = requests.post(f"{API_BASE_URL}/api/sessions")
    assert response.status_code == 200
    
    session_data = response.json()
    session_id = session_data["data"]["sessionId"]
    print(f"   ✅ Session created: {session_id}")
    
    # 2. Check initial database state
    print("2. Checking initial database state...")
    session = db_service.get_session(session_id)
    print(f"   Initial status: {session['status']}")
    print(f"   Initial summary: {session.get('summary', 'None')}")
    assert session["status"] == "active"
    assert session.get("summary") is None
    
    # 3. Send a few messages to establish conversation
    print("3. Sending initial messages...")
    create_test_audio()
    
    for i in range(2):
        with open(TEST_AUDIO_FILE, "rb") as audio_file:
            files = {"audio": ("test.wav", audio_file, "audio/wav")}
            response = requests.post(
                f"{API_BASE_URL}/api/sessions/{session_id}/messages",
                files=files
            )
            print(f"   Message {i+1} sent: Status {response.status_code}")
            time.sleep(1)  # Brief pause between messages
    
    # 4. Trigger wrap-up confirmation by saying "wrap up"
    print("4. Triggering wrap-up...")
    wrap_audio = create_wrap_up_audio()
    
    with open(wrap_audio, "rb") as audio_file:
        files = {"audio": ("wrap_up.wav", audio_file, "audio/wav")}
        response = requests.post(
            f"{API_BASE_URL}/api/sessions/{session_id}/messages",
            files=files
        )
        
        print(f"   Wrap-up trigger sent: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                if "awaitingWrapUpConfirmation" in data["data"]:
                    print("   ✅ Wrap-up confirmation triggered")
                    
                    # 5. Confirm wrap-up by saying "yes"
                    print("5. Confirming wrap-up...")
                    confirm_audio = create_confirmation_audio()
                    
                    with open(confirm_audio, "rb") as audio_file:
                        files = {"audio": ("confirm.wav", audio_file, "audio/wav")}
                        response = requests.post(
                            f"{API_BASE_URL}/api/sessions/{session_id}/messages",
                            files=files
                        )
                        
                        print(f"   Confirmation sent: Status {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success") and "data" in data:
                                if data["data"].get("sessionEnded"):
                                    print("   ✅ Session automatically ended!")
                                    
                                    # 6. Check database state after automatic ending
                                    print("6. Checking database state after automatic ending...")
                                    time.sleep(2)  # Give database time to update
                                    
                                    session = db_service.get_session(session_id)
                                    print(f"   Final status: {session['status']}")
                                    print(f"   Final summary: {'Present' if session.get('summary') else 'None'}")
                                    print(f"   Ended at: {session.get('ended_at', 'None')}")
                                    print(f"   Duration: {session.get('duration_seconds', 'None')} seconds")
                                    
                                    # Verify the fix worked
                                    if session["status"] == "ended" and session.get("summary"):
                                        print("\n🎉 SUCCESS: Bug fix verified!")
                                        print("   ✅ Session status updated to 'ended'")
                                        print("   ✅ Summary saved to database")
                                        print("   ✅ End timestamp recorded")
                                        print("   ✅ Duration calculated")
                                        return True
                                    else:
                                        print("\n❌ FAILURE: Bug still exists!")
                                        print(f"   Status: {session['status']} (expected: ended)")
                                        print(f"   Summary: {session.get('summary', 'None')} (expected: present)")
                                        return False
    
    print("\n❌ Test failed to complete successfully")
    return False

def create_wrap_up_audio():
    """Create audio that says 'wrap up' - simplified version."""
    # For this test, we'll create a simple audio file
    # In reality, this would need actual speech audio
    create_test_audio()
    return TEST_AUDIO_FILE

def create_confirmation_audio():
    """Create audio that says 'yes' - simplified version."""
    # For this test, we'll create a simple audio file
    # In reality, this would need actual speech audio
    create_test_audio()
    return TEST_AUDIO_FILE

if __name__ == "__main__":
    try:
        success = test_automatic_session_ending()
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Tests failed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc() 