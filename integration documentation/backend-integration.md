# Backend Integration Plan - MVP

## Overview
This document outlines the minimal required backend API specifications for the Kuku Coach MVP, focusing on the core conversation flow.

## Architecture

### Current Implementation
- Mock API services simulate backend responses
- REST API-based design for simplicity and reliability
- Message state handled in local storage for persistence

### Target Architecture
- Clean API client interfaces that can switch between mock and real implementations
- Single source of truth for backend communication
- Proper separation between data fetching and UI state

## API Client Interface

```typescript
// Base types for all API responses
interface ApiResponse {
  success: boolean;
  error?: string;
}

// Essential API Client Interface for MVP
interface KukuCoachApiClient {
  // Session Management
  createSession(): Promise<SessionResponse>;
  getSession(sessionId: string): Promise<SessionResponse>;
  endSession(sessionId: string): Promise<SummaryResponse>;
  
  // Conversation
  sendAudioMessage(sessionId: string, audioBlob: Blob): Promise<MessageResponse>;
  getConversationHistory(sessionId: string): Promise<ConversationHistoryResponse>;
}
```

## Essential API Endpoints

### Session Endpoints

#### POST /api/sessions
Creates a new coaching session.

Request: (empty or with optional parameters)

Response:
```json
{
  "success": true,
  "data": {
    "sessionId": "session-1234567890",
    "createdAt": "2023-06-15T10:30:00Z",
    "status": "active"
  }
}
```

#### GET /api/sessions/{sessionId}
Gets the status and details of an existing session.

Response:
```json
{
  "success": true,
  "data": {
    "sessionId": "session-1234567890",
    "createdAt": "2023-06-15T10:30:00Z",
    "updatedAt": "2023-06-15T10:35:00Z",
    "status": "active",
    "messageCount": 6
  }
}
```

#### POST /api/sessions/{sessionId}/end
Ends an active session and generates a summary.

Response:
```json
{
  "success": true,
  "data": {
    "sessionId": "session-1234567890",
    "summary": "Session summary text...",
    "duration": 300,
    "messageCount": 6
  }
}
```

### Conversation Endpoints

#### POST /api/sessions/{sessionId}/messages
Sends audio to be processed and receives AI response.

Request:
- Content-Type: multipart/form-data
- Audio file as 'audio' field

Response:
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "msg-user-123",
        "timestamp": "2023-06-15T10:31:00Z",
        "sender": "user",
        "text": "Transcribed user message"
      },
      {
        "id": "msg-ai-456",
        "timestamp": "2023-06-15T10:31:05Z",
        "sender": "ai",
        "text": "AI response message",
        "audioUrl": "https://api.kukucoach.com/audio/response-456.mp3"
      }
    ]
  }
}
```

#### GET /api/sessions/{sessionId}/messages
Gets the conversation history for a session.

Response:
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "msg-user-123",
        "timestamp": "2023-06-15T10:31:00Z",
        "sender": "user", 
        "text": "User message"
      },
      {
        "id": "msg-ai-456",
        "timestamp": "2023-06-15T10:31:05Z",
        "sender": "ai",
        "text": "AI response message",
        "audioUrl": "https://api.kukucoach.com/audio/response-456.mp3"
      }
      // Additional messages...
    ]
  }
}
```

## Error Handling

All API error responses should follow this pattern:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common error cases:
- Session not found
- Invalid session ID
- Audio processing failed
- Session already ended

## Implementation Plan

### Priority Order
1. POST /api/sessions (Create session)
2. POST /api/sessions/{sessionId}/messages (Send audio)
3. GET /api/sessions/{sessionId}/messages (Get conversation history)
4. GET /api/sessions/{sessionId} (Check session status)
5. POST /api/sessions/{sessionId}/end (End session)