# Kuku Coach API - To-Do List

This document tracks the progress, pending tasks, and potential future improvements for the Kuku Coach API.

## Completed Tasks (MVP)

*   [x] **Branch Creation**: Created `jules-try` branch for API development.
*   [x] **FastAPI Setup**: Initialized `api_main.py` with FastAPI and added dependencies (`fastapi`, `uvicorn`).
*   [x] **Session Management Endpoints**:
    *   [x] `POST /api/sessions` (Create session)
    *   [x] `GET /api/sessions/{sessionId}` (Get session status)
    *   [x] `POST /api/sessions/{sessionId}/end` (End session and get summary)
*   [x] **Conversation Endpoints**:
    *   [x] `GET /api/sessions/{sessionId}/messages` (Get conversation history)
    *   [x] `POST /api/sessions/{sessionId}/messages` (Send audio, transcribe, get AI response, provide audio URL for AI response)
*   [x] **Code Refactoring for API Compatibility**:
    *   [x] Refactored `conversation.py`, `config.py`, `audio_input.py`, and `audio_output.py` for API usage (logging, path handling, removed CLI specifics).
    *   [x] Configured static file serving for AI audio responses.
*   [x] **Error Handling**: Implemented standardized JSON error responses and a global exception handler.
*   [x] **Unit Tests**: Developed unit tests for all API endpoints using `pytest` and `TestClient`, covering success and error cases (15 tests passing).

## Pending Tasks / Next Steps

*   [ ] **Deployment Configuration (for Render.com)**:
    *   [ ] Ensure app uses environment variables for configuration (e.g., API keys, `PORT` for Uvicorn).
    *   [ ] Create a `Procfile` in the project root (e.g., `web: uvicorn api_main:app --host 0.0.0.0 --port $PORT`).
    *   [ ] Review Render.com deployment guides for Python/FastAPI.
    *   [ ] (Optional/Later) Explore Docker containerization if direct deployment proves difficult or for other hosting platforms.
*   [ ] **Security Enhancements**:
    *   [ ] Implement API key authentication for endpoints.
    *   [ ] Review input validation thoroughly (e.g., for audio file types, sizes).
    *   [ ] Consider rate limiting.
*   [ ] **Database Integration**:
    *   [ ] Replace in-memory session storage with a persistent database (e.g., PostgreSQL, MongoDB) to store session data and conversation history.
*   [ ] **Asynchronous Operations**:
    *   [ ] For potentially long-running tasks like transcription and LLM calls, consider implementing asynchronous processing (e.g., using FastAPI's `BackgroundTask` or a task queue like Celery) to prevent blocking and timeouts. The current TTS and transcription are synchronous.
*   [ ] **Audio File Management**:
    *   [ ] Implement a more robust solution for storing and serving AI-generated audio files (e.g., cloud storage like S3).
    *   [ ] Add cleanup for temporary audio files.
*   [ ] **Configuration Management**:
    *   [ ] Externalize more configurations (e.g., model parameters, paths) if needed.
*   [ ] **Logging Enhancements**:
    *   [ ] Configure structured logging for better analysis in production.
    *   [ ] Add more detailed logging for key events and errors.
*   [ ] **Documentation**:
    *   [ ] Generate API documentation (e.g., using FastAPI's automatic OpenAPI/Swagger docs, and supplement with tools like Sphinx).
*   [ ] **Testing**:
    *   [ ] Add integration tests that test the full flow with actual (or more comprehensively mocked) dependencies.
    *   [ ] Test specific error conditions from `sample-api-payloads.md` that might require more than just format validation (e.g., "Audio too long" might need actual file size check).

## Potential Future Improvements

*   [ ] WebSocket support for real-time conversation updates.
*   [ ] More sophisticated session management (e.g., session expiration).
*   [ ] User accounts and authentication.
*   [ ] Admin interface for monitoring.
