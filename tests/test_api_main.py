import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Adjust the import path based on your project structure.
# If tests/ is at the same level as api_main.py, this should work.
# If api_main.py is in a subdirectory (e.g., app/), it might be from app.api_main import app
import sys
import os

# Add the project root to the Python path
# This assumes tests/ is a subdirectory of the project root.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from api_main import app, sessions as api_sessions # Import sessions for cleanup

client = TestClient(app)

# Helper function or fixture for cleanup if needed
def clear_sessions():
    api_sessions.clear()

def test_create_session_success():
    clear_sessions() # Ensure a clean state
    response = client.post("/api/sessions")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert "sessionId" in json_response["data"]
    assert isinstance(json_response["data"]["sessionId"], str)
    assert len(json_response["data"]["sessionId"]) > 0
    assert json_response["data"]["status"] == "active"
    
    # Check if session was actually created in the backend
    session_id = json_response["data"]["sessionId"]
    assert session_id in api_sessions
    clear_sessions() # Clean up

def test_create_session_conversation_init_fails():
    clear_sessions()
    with patch("api_main.Conversation") as MockConversation:
        MockConversation.side_effect = Exception("Test Conversation Init Error")
        response = client.post("/api/sessions")
        
    assert response.status_code == 500 # Assuming generic exception handler returns 500
    json_response = response.json()
    assert json_response["success"] is False
    assert "error" in json_response
    # The exact error message depends on the generic_exception_handler in api_main.py
    assert "Internal server error" in json_response["error"] or "Could not initialize session" in json_response["error"]
    
    assert len(api_sessions) == 0 # Ensure no session was added
    clear_sessions()

@pytest.fixture
def created_session():
    clear_sessions() # Start with a clean state
    response = client.post("/api/sessions")
    assert response.status_code == 200 # Or 201 if that's what create_session returns
    session_id = response.json()["data"]["sessionId"]
    yield session_id # Provide the session_id to the test
    clear_sessions() # Clean up after the test

# Tests for GET /api/sessions/{sessionId}
def test_get_session_success(created_session):
    session_id = created_session
    response = client.get(f"/api/sessions/{session_id}")
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["data"]["sessionId"] == session_id
    assert json_response["data"]["status"] == "active" # Or whatever initial status is
    assert "messageCount" in json_response["data"] # Assuming 0 for a new session
    assert json_response["data"]["messageCount"] == 0 

def test_get_session_not_found():
    clear_sessions()
    response = client.get("/api/sessions/non_existent_session_id")
    assert response.status_code == 404
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"] == "Session not found"

# Tests for POST /api/sessions/{sessionId}/end
def test_end_session_success(created_session):
    session_id = created_session
    
    # Mock the generate_closing_summary method of the Conversation instance
    # This is important if the actual method makes external calls or is complex
    with patch.object(api_sessions[session_id], 'generate_closing_summary', return_value="Test summary") as mock_summary:
        response = client.post(f"/api/sessions/{session_id}/end")
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["data"]["sessionId"] == session_id
    assert json_response["data"]["summary"] == "Test summary"
    mock_summary.assert_called_once()
    
    # Verify session is removed from the global dictionary
    assert session_id not in api_sessions

def test_end_session_not_found():
    clear_sessions()
    response = client.post("/api/sessions/non_existent_session_id/end")
    assert response.status_code == 404
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"] == "Session not found"

def test_end_session_already_ended(created_session):
    session_id = created_session
    
    # First call to end the session
    with patch.object(api_sessions[session_id], 'generate_closing_summary', return_value="First summary"):
        response1 = client.post(f"/api/sessions/{session_id}/end")
    assert response1.status_code == 200
    assert session_id not in api_sessions # Session should be removed

    # Second call to end the same session (it's already removed, so should be "not found")
    # If the session object itself was marked as ended but not removed, the behavior would be different (400)
    # Based on current api_main.py, `del sessions[session_id]` happens.
    response2 = client.post(f"/api/sessions/{session_id}/end")
    assert response2.status_code == 404 # Because it's deleted
    json_response2 = response2.json()
    assert json_response2["success"] is False
    assert json_response2["error"] == "Session not found" 
    # If the requirement was to check an is_ended flag *before* deletion,
    # this test would target a 400 "Session already ended".
    # The current `api_main.py` for `end_session`:
    # 1. Gets session. If not found -> 404.
    # 2. Checks `is_ended()`. If true -> 400.
    # 3. Generates summary.
    # 4. `del sessions[session_id]`.
    # So, for the second call, it should be a 404 because the session is deleted.
    # To test the "Session already ended" (400) logic, we'd need to mock `del sessions[session_id]`
    # or prevent deletion to make a second call where the session *object* still exists but is marked.
    # For now, this test reflects the "deleted session means not found" behavior.

    # To properly test the "Session already ended" (400) case:
    clear_sessions()
    # Create a new session for this specific test case
    response_create = client.post("/api/sessions")
    session_id_for_already_ended_test = response_create.json()["data"]["sessionId"]
    
    # Mock the Conversation instance's is_ended to return True after the first call,
    # and prevent deletion to test the specific "already ended" logic.
    original_session_instance = api_sessions[session_id_for_already_ended_test]
    
    with patch.object(original_session_instance, 'generate_closing_summary', return_value="Summary") as mock_summary, \
         patch.object(original_session_instance, 'is_ended', return_value=False) as mock_is_ended_first_call, \
         patch.dict(api_sessions, {session_id_for_already_ended_test: original_session_instance}, clear=True): # Ensure session stays for this test
        
        # First call - should succeed
        response_end1 = client.post(f"/api/sessions/{session_id_for_already_ended_test}/end")
        assert response_end1.status_code == 200
        mock_is_ended_first_call.assert_called_once() # is_ended was checked
        # Now, simulate that the Conversation object's end_session() was called by generate_closing_summary()
        # and its internal _is_ended flag is now True.
        # For the next call, is_ended() should return True.
        mock_is_ended_first_call.return_value = True # This doesn't work as expected as it's a new mock object per call to patch.object
                                                     # Instead, we'd need to modify the actual instance's state if possible,
                                                     # or mock `is_ended` on the specific instance *before* the second call.
                                                     # A simpler way is to rely on the generate_closing_summary calling end_session()
                                                     # which sets the internal _is_ended flag on the actual Conversation object.
        
        # Manually set the instance to ended, as `generate_closing_summary` in `Conversation` calls `self.end_session()`
        original_session_instance.end_session()


    # Second call - now the instance should be marked as ended
    with patch.dict(api_sessions, {session_id_for_already_ended_test: original_session_instance}, clear=True):
         response_end2 = client.post(f"/api/sessions/{session_id_for_already_ended_test}/end")

    assert response_end2.status_code == 400
    json_response_end2 = response_end2.json()
    assert json_response_end2["success"] is False
    assert json_response_end2["error"] == "Session already ended"

# Imports for mocking Langchain messages and BytesIO for dummy files
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from io import BytesIO
import uuid # For mocking UUID if needed for predictable filenames, though not strictly required by current tests

# Tests for GET /api/sessions/{sessionId}/messages
def test_get_conversation_history_success(created_session):
    session_id = created_session
    
    # Mock conversation history
    mock_history = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!")
    ]
    
    with patch.object(api_sessions[session_id], 'get_conversation_history', return_value=mock_history):
        response = client.get(f"/api/sessions/{session_id}/messages")
        
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert len(json_response["data"]["messages"]) == 2
    
    # Verify structure and content of messages
    msg1 = json_response["data"]["messages"][0]
    assert msg1["sender"] == "user"
    assert msg1["text"] == "Hello"
    assert "id" in msg1
    assert "timestamp" in msg1
    
    msg2 = json_response["data"]["messages"][1]
    assert msg2["sender"] == "ai"
    assert msg2["text"] == "Hi there!"
    assert "id" in msg2
    assert "timestamp" in msg2

def test_get_conversation_history_empty(created_session):
    session_id = created_session
    
    # Ensure history is empty (or mock it to be empty)
    with patch.object(api_sessions[session_id], 'get_conversation_history', return_value=[]):
        response = client.get(f"/api/sessions/{session_id}/messages")
        
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert len(json_response["data"]["messages"]) == 0

def test_get_conversation_history_session_not_found():
    clear_sessions()
    response = client.get("/api/sessions/non_existent_session_id/messages")
    assert response.status_code == 404
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"] == "Session not found"

# Tests for POST /api/sessions/{sessionId}/messages
@patch("uuid.uuid4") # Mock uuid.uuid4 to get predictable filenames
@patch("api_main.text_to_speech_save_file") # Corresponds to 'from audio_output import text_to_speech_file as text_to_speech_save_file'
@patch("api_main.transcribe_audio") # Corresponds to 'from audio_input import transcribe_audio'
def test_send_audio_message_success(mock_transcribe_audio, mock_text_to_speech, mock_uuid, created_session):
    session_id = created_session
    
    # Setup mocks
    # Use a valid UUID hex string for mocking
    fixed_uuid_obj = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mock_uuid.return_value = fixed_uuid_obj # mock_uuid returns a UUID object
    
    # api_main.py uses str(uuid.uuid4()) for filename, which includes hyphens
    expected_tts_filename = f"{str(fixed_uuid_obj)}.mp3" 
    # The path used in api_main.py is relative to where the app runs, using STATIC_AUDIO_DIR
    expected_tts_full_path = os.path.join("static/audio", expected_tts_filename)

    mock_transcribe_audio.return_value = "User says hello"
    conversation_instance = api_sessions[session_id]
    with patch.object(conversation_instance, 'process_input', return_value="AI responds to hello") as mock_process_input:
        # mock_text_to_speech (which is text_to_speech_save_file) should return the path it saved to.
        mock_text_to_speech.return_value = expected_tts_full_path
        
        # Dummy audio file
        dummy_audio_content = b"dummy audio data for wav"
        files = {'audio': ('test.wav', BytesIO(dummy_audio_content), 'audio/wav')}
        
        response = client.post(f"/api/sessions/{session_id}/messages", files=files)
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    
    messages = json_response["data"]["messages"]
    assert len(messages) == 2
    
    user_msg = messages[0]
    assert user_msg["sender"] == "user"
    assert user_msg["text"] == "User says hello"
    
    ai_msg = messages[1]
    assert ai_msg["sender"] == "ai"
    assert ai_msg["text"] == "AI responds to hello"
    # The URL should be relative to the static mount point, using the predictable filename
    assert ai_msg["audioUrl"] == f"/audio/{expected_tts_filename}"
    
    mock_transcribe_audio.assert_called_once()
    mock_process_input.assert_called_once_with("User says hello")
    # api_main.text_to_speech_file calls the imported audio_output.text_to_speech_save_file
    # with the text and the constructed full path based on the (mocked) UUID.
    mock_text_to_speech.assert_called_once_with(text="AI responds to hello", output_file_path=expected_tts_full_path)


def test_send_audio_message_session_not_found():
    clear_sessions()
    dummy_audio_content = b"dummy audio data"
    files = {'audio': ('test.wav', BytesIO(dummy_audio_content), 'audio/wav')}
    response = client.post("/api/sessions/non_existent_session_id/messages", files=files)
    
    assert response.status_code == 404
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"] == "Session not found"

@patch("api_main.transcribe_audio")
def test_send_audio_message_transcription_fails(mock_transcribe_audio, created_session):
    session_id = created_session
    mock_transcribe_audio.return_value = None # Simulate transcription failure
    
    dummy_audio_content = b"dummy audio data"
    files = {'audio': ('test.wav', BytesIO(dummy_audio_content), 'audio/wav')}
    
    response = client.post(f"/api/sessions/{session_id}/messages", files=files)
    
    assert response.status_code == 500
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"] == "Audio transcription failed."
    mock_transcribe_audio.assert_called_once()

@patch("api_main.transcribe_audio")
def test_send_audio_message_ai_response_fails(mock_transcribe_audio, created_session):
    session_id = created_session
    mock_transcribe_audio.return_value = "User says something"
    
    conversation_instance = api_sessions[session_id]
    with patch.object(conversation_instance, 'process_input', return_value=None) as mock_process_input: # Simulate AI failing to respond
        dummy_audio_content = b"dummy audio data"
        files = {'audio': ('test.wav', BytesIO(dummy_audio_content), 'audio/wav')}
        response = client.post(f"/api/sessions/{session_id}/messages", files=files)

    assert response.status_code == 500
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"] == "AI did not return a response."
    mock_transcribe_audio.assert_called_once()
    mock_process_input.assert_called_once_with("User says something")

@patch("uuid.uuid4")
@patch("api_main.text_to_speech_save_file")
@patch("api_main.transcribe_audio")
def test_send_audio_message_tts_fails(mock_transcribe_audio, mock_text_to_speech, mock_uuid, created_session):
    session_id = created_session
    
    # Use a valid UUID hex string for mocking
    fixed_uuid_obj_tts_fails = uuid.UUID("abcdef01-2345-6789-abcd-ef0123456789")
    mock_uuid.return_value = fixed_uuid_obj_tts_fails # mock_uuid returns a UUID object
    
    # api_main.py uses str(uuid.uuid4()) for filename
    expected_tts_filename_tts_fails = f"{str(fixed_uuid_obj_tts_fails)}.mp3"
    # The path used in api_main.py is relative
    expected_tts_full_path = os.path.join("static/audio", expected_tts_filename_tts_fails)

    mock_transcribe_audio.return_value = "User says hello"
    conversation_instance = api_sessions[session_id]
    with patch.object(conversation_instance, 'process_input', return_value="AI responds but TTS fails") as mock_process_input:
        mock_text_to_speech.return_value = None # Simulate TTS failure (text_to_speech_save_file returns None)
    
        dummy_audio_content = b"dummy audio data"
        files = {'audio': ('test.wav', BytesIO(dummy_audio_content), 'audio/wav')}
        response = client.post(f"/api/sessions/{session_id}/messages", files=files)

    assert response.status_code == 200 # Endpoint should still succeed
    json_response = response.json()
    assert json_response["success"] is True
    
    messages = json_response["data"]["messages"]
    assert len(messages) == 2
    ai_msg = messages[1]
    assert ai_msg["text"] == "AI responds but TTS fails"
    assert ai_msg["audioUrl"] is None # Expect no audio URL
    
    mock_transcribe_audio.assert_called_once()
    mock_process_input.assert_called_once_with("User says hello")
    # The output_file_path for mock_text_to_speech will be dynamically generated in api_main.py
    # using the mocked UUID.
    mock_text_to_speech.assert_called_once_with(text="AI responds but TTS fails", output_file_path=expected_tts_full_path)
