# Sample API Payloads - MVP

This document provides detailed examples of request and response payloads for the five essential API endpoints in the Kuku Coach MVP.

## Session Endpoints

### 1. POST /api/sessions

**Request (Empty body is acceptable):**
```json
{}
```

**Successful Response:**
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

**Failed Response (Rate Limited):**
```json
{
  "success": false,
  "error": "Too many session requests. Please try again later."
}
```

### 2. GET /api/sessions/{sessionId}

**Successful Response:**
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

**Failed Response (Not Found):**
```json
{
  "success": false,
  "error": "Session not found"
}
```

**Failed Response (Invalid Session ID Format):**
```json
{
  "success": false,
  "error": "Invalid session ID format"
}
```

### 3. POST /api/sessions/{sessionId}/end

**Request (Empty body is acceptable):**
```json
{}
```

**Successful Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "session-1234567890",
    "summary": "In this coaching session, you discussed work stress and strategies to manage it. We explored mindfulness techniques, time management, and setting boundaries. Key insights included recognizing stress triggers and implementing regular wellness practices.",
    "duration": 300,
    "messageCount": 6
  }
}
```

**Failed Response (Session Already Ended):**
```json
{
  "success": false,
  "error": "Session already ended"
}
```

**Failed Response (Not Found):**
```json
{
  "success": false,
  "error": "Session not found"
}
```

## Conversation Endpoints

### 4. POST /api/sessions/{sessionId}/messages

**Request:**
Form data with audio file attached as 'audio' field.

**Successful Response (User Message and AI Response):**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "msg-user-123",
        "timestamp": "2023-06-15T10:31:00Z",
        "sender": "user",
        "text": "I'm feeling really overwhelmed with work lately."
      },
      {
        "id": "msg-ai-456",
        "timestamp": "2023-06-15T10:31:05Z",
        "sender": "ai",
        "text": "I understand how challenging it can be when work feels overwhelming. Let's break this down together. Could you tell me what aspects of work are causing you the most stress right now?",
        "audioUrl": "https://api.kukucoach.com/audio/response-456.mp3"
      }
    ]
  }
}
```

**Failed Response (Invalid Audio Format):**
```json
{
  "success": false,
  "error": "Invalid audio format. Please use MP3, WAV, or WebM format."
}
```

**Failed Response (Audio Too Long):**
```json
{
  "success": false,
  "error": "Audio duration exceeds maximum allowed (60 seconds)"
}
```

**Failed Response (Processing Error):**
```json
{
  "success": false,
  "error": "Error processing audio. Please try again."
}
```

### 5. GET /api/sessions/{sessionId}/messages

**Successful Response (Full Conversation History):**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "msg-user-123",
        "timestamp": "2023-06-15T10:31:00Z",
        "sender": "user",
        "text": "I'm feeling really overwhelmed with work lately."
      },
      {
        "id": "msg-ai-456",
        "timestamp": "2023-06-15T10:31:05Z",
        "sender": "ai",
        "text": "I understand how challenging it can be when work feels overwhelming. Let's break this down together. Could you tell me what aspects of work are causing you the most stress right now?",
        "audioUrl": "https://api.kukucoach.com/audio/response-456.mp3"
      },
      {
        "id": "msg-user-789",
        "timestamp": "2023-06-15T10:32:15Z",
        "sender": "user",
        "text": "I think it's the constant emails and my boss adding more tasks before I finish the previous ones."
      },
      {
        "id": "msg-ai-012",
        "timestamp": "2023-06-15T10:32:20Z",
        "sender": "ai",
        "text": "That's really challenging - dealing with email overload while also having new tasks assigned before completing existing ones. Let's tackle this from two angles: managing communications and setting boundaries. First, have you tried any email management strategies, like dedicated time blocks for handling emails?",
        "audioUrl": "https://api.kukucoach.com/audio/response-012.mp3"
      }
    ]
  }
}
```

**Successful Response (Empty Conversation):**
```json
{
  "success": true,
  "data": {
    "messages": []
  }
}
```

**Failed Response (Not Found):**
```json
{
  "success": false,
  "error": "Session not found"
}
```

## Error Response Patterns

All API error responses should follow this general pattern:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE" // Optional
}
```

## Special Cases

### Handling Large Audio Files

If the client needs to upload large audio files, consider implementing a chunked upload approach or utilizing compression.

### Long-Running Processes

For AI responses that take longer to generate:

**Initial Response (Processing Started):**
```json
{
  "success": true,
  "data": {
    "status": "processing",
    "messageId": "msg-user-123",
    "estimatedTimeSeconds": 5
  }
}
```

**Client should poll endpoint:**
GET /api/sessions/{sessionId}/messages/{messageId}/status

**Poll Response (Still Processing):**
```json
{
  "success": true,
  "data": {
    "status": "processing",
    "progress": 0.6
  }
}
```

**Poll Response (Complete):**
```json
{
  "success": true,
  "data": {
    "status": "complete",
    "message": {
      "id": "msg-ai-456",
      "timestamp": "2023-06-15T10:31:05Z",
      "sender": "ai",
      "text": "I understand how challenging it can be when work feels overwhelming...",
      "audioUrl": "https://api.kukucoach.com/audio/response-456.mp3"
    }
  }
}
```