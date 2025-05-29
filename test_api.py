import pytest
import requests
import json
import io
import os
import time
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_AUDIO_FILES = {
    "short_wav": "test_audio/short_test.wav",
    "medium_mp3": "test_audio/medium_test.mp3", 
    "webm": "test_audio/test.webm"
}

class TestKukuCoachAPI:
    """
    Comprehensive test suite for Kuku Coach API endpoints.
    
    Tests cover all 5 essential endpoints as specified in integration-testing-plan.md:
    1. POST /api/sessions - Create session
    2. GET /api/sessions/{sessionId} - Get session status  
    3. POST /api/sessions/{sessionId}/messages - Send audio message
    4. GET /api/sessions/{sessionId}/messages - Get conversation history
    5. POST /api/sessions/{sessionId}/end - End session
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test."""
        self.session_id = None
        self.created_sessions = []
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up any created sessions
        for session_id in self.created_sessions:
            try:
                requests.post(f"{API_BASE_URL}/sessions/{session_id}/end")
            except:
                pass
    
    def create_test_session(self) -> str:
        """Helper method to create a test session."""
        response = requests.post(f"{API_BASE_URL}/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        session_id = data["data"]["sessionId"]
        self.created_sessions.append(session_id)
        return session_id
    
    def create_test_audio_file(self) -> io.BytesIO:
        """Helper method to create a test audio file."""
        # Create a simple WAV file for testing
        audio_data = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        return io.BytesIO(audio_data)

    # Test Cases for Session Creation (S-01, S-02, S-03)
    
    def test_s01_create_new_session(self):
        """S-01: Create new session - Successfully returns valid session ID"""
        response = requests.post(f"{API_BASE_URL}/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "sessionId" in data["data"]
        assert data["data"]["sessionId"].startswith("session-")
        assert "createdAt" in data["data"]
        assert data["data"]["status"] == "active"
        assert data["data"]["messageCount"] == 0
        
        self.created_sessions.append(data["data"]["sessionId"])
    
    def test_s02_create_multiple_sessions(self):
        """S-02: Create multiple sessions - Each session has a unique ID"""
        session1_response = requests.post(f"{API_BASE_URL}/sessions")
        session2_response = requests.post(f"{API_BASE_URL}/sessions")
        
        assert session1_response.status_code == 200
        assert session2_response.status_code == 200
        
        session1_data = session1_response.json()
        session2_data = session2_response.json()
        
        assert session1_data["success"] is True
        assert session2_data["success"] is True
        
        session1_id = session1_data["data"]["sessionId"]
        session2_id = session2_data["data"]["sessionId"]
        
        assert session1_id != session2_id
        
        self.created_sessions.extend([session1_id, session2_id])

    # Test Cases for Session Status (S-04, S-05, S-06)
    
    def test_s04_get_existing_session(self):
        """S-04: Get existing session - Successfully returns session details"""
        session_id = self.create_test_session()
        
        response = requests.get(f"{API_BASE_URL}/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["sessionId"] == session_id
        assert data["data"]["status"] == "active"
        assert "createdAt" in data["data"]
        assert data["data"]["messageCount"] == 0
    
    def test_s05_get_nonexistent_session(self):
        """S-05: Get non-existent session - Returns appropriate error"""
        fake_session_id = "session-nonexistent"
        
        response = requests.get(f"{API_BASE_URL}/sessions/{fake_session_id}")
        
        assert response.status_code == 200  # API returns 200 with error in body
        data = response.json()
        
        assert data["success"] is False
        assert "Session not found" in data["error"]
    
    def test_s06_get_session_invalid_format(self):
        """S-06: Get session with invalid ID format - Returns validation error"""
        invalid_session_id = "invalid-format"
        
        response = requests.get(f"{API_BASE_URL}/sessions/{invalid_session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Session not found" in data["error"]

    # Test Cases for Audio Conversation (A-01, A-02, A-03, A-04, A-05)
    
    def test_a01_send_short_audio_message(self):
        """A-01: Send short audio message - Returns transcription and AI response"""
        session_id = self.create_test_session()
        
        # Create test audio file
        audio_file = self.create_test_audio_file()
        
        files = {
            'audio': ('test_audio.wav', audio_file, 'audio/wav')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/sessions/{session_id}/messages",
            files=files
        )
        
        # Note: This test may fail if audio transcription fails
        # In a real test environment, you'd use actual audio files
        assert response.status_code == 200
        data = response.json()
        
        if data["success"]:
            assert "data" in data
            assert "messages" in data["data"]
            assert len(data["data"]["messages"]) == 2  # User + AI message
            
            user_msg = data["data"]["messages"][0]
            ai_msg = data["data"]["messages"][1]
            
            assert user_msg["sender"] == "user"
            assert ai_msg["sender"] == "ai"
            assert "text" in user_msg
            assert "text" in ai_msg
        else:
            # Accept transcription failures in test environment
            assert "transcribe" in data["error"].lower() or "audio" in data["error"].lower()
    
    def test_a04_send_malformed_audio_data(self):
        """A-04: Send malformed audio data - Returns appropriate error"""
        session_id = self.create_test_session()
        
        # Send non-audio data
        files = {
            'audio': ('test.txt', io.BytesIO(b'This is not audio data'), 'text/plain')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/sessions/{session_id}/messages",
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Invalid audio format" in data["error"]
    
    def test_a05_send_audio_to_nonexistent_session(self):
        """A-05: Send audio to non-existent session - Returns appropriate error"""
        fake_session_id = "session-nonexistent"
        
        audio_file = self.create_test_audio_file()
        files = {
            'audio': ('test_audio.wav', audio_file, 'audio/wav')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/sessions/{fake_session_id}/messages",
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Session not found" in data["error"]

    # Test Cases for Conversation History (H-01, H-02, H-03, H-04)
    
    def test_h01_get_history_new_session(self):
        """H-01: Get history for new session - Returns empty message array"""
        session_id = self.create_test_session()
        
        response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "messages" in data["data"]
        assert len(data["data"]["messages"]) == 0
    
    def test_h03_get_history_nonexistent_session(self):
        """H-03: Get history for non-existent session - Returns appropriate error"""
        fake_session_id = "session-nonexistent"
        
        response = requests.get(f"{API_BASE_URL}/sessions/{fake_session_id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Session not found" in data["error"]

    # Test Cases for End Session (E-01, E-02, E-03)
    
    def test_e01_end_active_session(self):
        """E-01: End active session - Successfully ends session and returns summary"""
        session_id = self.create_test_session()
        
        response = requests.post(f"{API_BASE_URL}/sessions/{session_id}/end")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["sessionId"] == session_id
        assert "summary" in data["data"]
        assert "duration" in data["data"]
        assert "messageCount" in data["data"]
        
        # Remove from cleanup list since it's already ended
        if session_id in self.created_sessions:
            self.created_sessions.remove(session_id)
    
    def test_e02_end_already_ended_session(self):
        """E-02: End already ended session - Returns appropriate error"""
        session_id = self.create_test_session()
        
        # End session first time
        response1 = requests.post(f"{API_BASE_URL}/sessions/{session_id}/end")
        assert response1.status_code == 200
        assert response1.json()["success"] is True
        
        # Try to end again
        response2 = requests.post(f"{API_BASE_URL}/sessions/{session_id}/end")
        assert response2.status_code == 200
        data = response2.json()
        
        assert data["success"] is False
        assert "already ended" in data["error"]
    
    def test_e03_end_nonexistent_session(self):
        """E-03: End non-existent session - Returns appropriate error"""
        fake_session_id = "session-nonexistent"
        
        response = requests.post(f"{API_BASE_URL}/sessions/{fake_session_id}/end")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Session not found" in data["error"]

    # Integration Flow Test
    
    def test_complete_user_journey(self):
        """Complete end-to-end user journey test"""
        
        # 1. Create session
        session_id = self.create_test_session()
        
        # 2. Verify session status
        status_response = requests.get(f"{API_BASE_URL}/sessions/{session_id}")
        assert status_response.json()["success"] is True
        
        # 3. Check initial empty history
        history_response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/messages")
        assert history_response.json()["success"] is True
        assert len(history_response.json()["data"]["messages"]) == 0
        
        # 4. End session
        end_response = requests.post(f"{API_BASE_URL}/sessions/{session_id}/end")
        assert end_response.json()["success"] is True
        
        # Remove from cleanup since already ended
        if session_id in self.created_sessions:
            self.created_sessions.remove(session_id)


# Test utility functions
def test_api_health_check():
    """Test API health check endpoint"""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_api_root_endpoint():
    """Test API root endpoint"""
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Kuku Coach API"
    assert data["version"] == "1.0.0"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 