# Tech Context: Kuku Coach API

## 1. Backend

*   **Framework:** `FastAPI`
    *   **Reason:** Provides high performance, automatic generation of interactive API documentation (like Swagger UI at `/docs`), and uses Python type hints for data validation (via Pydantic). This makes development fast and reliable.
*   **Web Server:** `Uvicorn`
    *   **Reason:** It is the recommended ASGI server for FastAPI, providing the asynchronous capabilities needed for a responsive API.

## 2. Conversation & AI

*   **Core Library:** `LangChain`
    *   **Reason:** It provides a framework to chain together different AI components, such as the language model, memory, and prompts. This modularizes the conversation logic.
*   **Language Model:** `OpenAI`
    *   **Reason:** Provides access to powerful, general-purpose language models that are well-suited for a coaching conversation.
*   **Conversation Memory:** `ConversationBufferMemory` from LangChain
    *   **Reason:** It is used to store the history of the conversation, which is essential for the AI to maintain context across multiple turns.

## 3. Audio Processing

*   **Speech-to-Text:** `Whisper` (via OpenAI's API)
    *   **Reason:** Offers high-accuracy transcription for a wide range of accents and languages.
*   **Text-to-Speech:** `ElevenLabs`
    *   **Reason:** Provides high-quality, natural-sounding voices that enhance the user experience.

## 4. Development & Testing

*   **Testing Framework:** `pytest`
    *   **Reason:** A powerful and popular Python testing framework that is used for writing unit and integration tests for the API.
*   **HTTP Client for Testing:** `requests`
    *   **Reason:** A simple and robust library for making HTTP requests in the test scripts, allowing us to simulate a client interacting with the API endpoints.

## 5. Session Management

*   **Current Implementation:** An in-memory Python dictionary.
    *   **Reason:** Simple and sufficient for the current development phase. It allows for rapid iteration without requiring a database setup.
*   **Future Plan:** `Supabase` (PostgreSQL)
    *   **Reason:** To provide persistent storage for session data, ensuring that conversations are not lost if the server restarts. The `database_service.py` file contains the initial integration logic for this. 