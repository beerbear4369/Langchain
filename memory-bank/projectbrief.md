# Project Brief: Kuku Coach API

## 1. Project Overview

This project is to develop a robust, voice-first AI coaching assistant API. The API serves as the backend for a frontend application, providing services for session management, voice-based conversation processing, and AI-driven coaching. The core of the project is to translate the functionality of a standalone Python coaching application into a scalable, stateless API that can be integrated with various clients.

## 2. Core Requirements

*   **Session Management:** The API must handle the creation, status tracking, and termination of coaching sessions.
*   **Voice-to-Text & Text-to-Speech:** The system must accept user audio input, transcribe it to text, and convert the AI's text responses back into audio.
*   **AI Conversation Logic:** The API needs to manage a coherent, context-aware coaching conversation, leveraging a large language model.
*   **Conversation Wrap-up:** A key feature is the ability to gracefully conclude a conversation. This includes:
    *   **User-Initiated Wrap-up:** Allowing the user to request the end of the session.
    *   **AI-Initiated Wrap-up:** Proactively suggesting a wrap-up based on conversation duration, turn count, or detection of conclusive content.
    *   **Confirmation Flow:** A two-step confirmation process to prevent accidental session termination.
*   **Stateless Architecture:** All session-specific data (like conversation history, timestamps, and counters) must be managed on the server, linked to a unique session ID, to allow clients to remain stateless.

## 3. Key Technologies

*   **Backend Framework:** FastAPI (Python)
*   **AI/LLM:** OpenAI (via LangChain)
*   **Speech-to-Text:** Whisper
*   **Text-to-Speech:** ElevenLabs
*   **Database:** Supabase (PostgreSQL) for persistent storage (optional but preferred).

## 4. Primary Goal

The primary goal is to create a reliable and scalable API that mirrors the intelligent behavior of the standalone prototype, with a particular focus on perfecting the complex, state-dependent logic (like conversation wrap-up) within a stateless request/response paradigm. 