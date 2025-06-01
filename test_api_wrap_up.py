#!/usr/bin/env python3
"""
Test script to verify automatic session wrap-up detection in the API.
This script tests the enhanced API functionality to match standalone version behavior.
"""

import requests
import json
import time
import os
from io import BytesIO

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "test_audio.wav"  # Small test audio file

def create_test_audio():
    """Create a simple test audio file for testing purposes."""
    # For testing, we'll just create a small dummy file
    # In real testing, you'd want to use actual audio files
    test_content = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
    with open(TEST_AUDIO_FILE, "wb") as f:
        f.write(test_content)

def test_session_creation():
    """Test session creation."""
    print("Testing session creation...")
    response = requests.post(f"{API_BASE_URL}/api/sessions")
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            return data["data"]["sessionId"]
    return None

def test_message_sending(session_id, message_count=20):
    """Test sending multiple messages to trigger wrap-up detection."""
    print(f"\nTesting message sending for session {session_id}...")
    
    # Create test audio file
    create_test_audio()
    
    try:
        for i in range(message_count):
            print(f"\nSending message {i+1}/{message_count}...")
            
            with open(TEST_AUDIO_FILE, "rb") as audio_file:
                files = {"audio": ("test.wav", audio_file, "audio/wav")}
                response = requests.post(
                    f"{API_BASE_URL}/api/sessions/{session_id}/messages",
                    files=files
                )
            
            print(f"Message {i+1} response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data['success']}")
                
                if data["success"] and "data" in data:
                    # Check if session was automatically ended
                    if "sessionEnded" in data["data"]:
                        print(f"🎉 Session automatically ended at message {i+1}!")
                        print(f"Session ended: {data['data']['sessionEnded']}")
                        
                        if "finalSummary" in data["data"]:
                            print("Final summary provided:")
                            print(data["data"]["finalSummary"][:200] + "...")
                        
                        return True  # Session ended automatically
                    
                    # Print AI response for monitoring
                    messages = data["data"].get("messages", [])
                    for msg in messages:
                        if msg["sender"] == "ai":
                            print(f"AI Response: {msg['text'][:100]}...")
            else:
                print(f"Error: {response.text}")
                break
            
            # Small delay between messages
            time.sleep(1)
        
        print(f"Completed {message_count} messages without automatic wrap-up")
        return False
    
    finally:
        # Clean up test audio file
        if os.path.exists(TEST_AUDIO_FILE):
            os.remove(TEST_AUDIO_FILE)

def test_manual_session_end(session_id):
    """Test manual session ending."""
    print(f"\nTesting manual session end for {session_id}...")
    
    response = requests.post(f"{API_BASE_URL}/api/sessions/{session_id}/end")
    print(f"End session response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        if data["success"]:
            summary_data = data["data"]
            print(f"Session ID: {summary_data['sessionId']}")
            print(f"Duration: {summary_data['duration']} seconds")
            print(f"Message count: {summary_data['messageCount']}")
            print(f"Summary: {summary_data['summary'][:200]}...")
    else:
        print(f"Error: {response.text}")

def main():
    """Main test function."""
    print("=== Testing API Automatic Wrap-Up Detection ===")
    
    # Test 1: Create session
    session_id = test_session_creation()
    if not session_id:
        print("❌ Failed to create session")
        return
    
    print(f"✅ Session created: {session_id}")
    
    # Test 2: Send messages to trigger wrap-up detection
    auto_ended = test_message_sending(session_id, message_count=25)
    
    # Test 3: Manual session end (only if not auto-ended)
    if not auto_ended:
        test_manual_session_end(session_id)
    else:
        print("✅ Automatic wrap-up detection working correctly!")

if __name__ == "__main__":
    main() 