# Frontend API Integration Guide - MVP

This document provides guidelines for integrating the frontend with the essential API endpoints needed for the MVP.

## Overview

We're implementing a minimal set of API endpoints for the MVP:

1. Create Session
2. Get Session Status
3. Send Audio Message
4. Get Conversation History
5. End Session

## Getting Started

### Importing the API Client

```typescript
import { getApiClient } from '@/services/api/client';

// In your component or hook
const apiClient = getApiClient();
```

### Using the Essential API Methods

#### Session Management

```typescript
// Create a new session
const createSession = async () => {
  try {
    const response = await apiClient.createSession();
    if (response.success && response.data) {
      const { sessionId } = response.data;
      console.log(`Created session: ${sessionId}`);
      // Store the session ID for future API calls
      return sessionId;
    }
  } catch (error) {
    console.error('Failed to create session:', error);
  }
};

// Get session status
const getSessionStatus = async (sessionId) => {
  try {
    const response = await apiClient.getSession(sessionId);
    if (response.success && response.data) {
      console.log(`Session status: ${response.data.status}`);
      return response.data;
    }
  } catch (error) {
    console.error('Failed to get session:', error);
  }
};

// End a session
const endSession = async (sessionId) => {
  try {
    const response = await apiClient.endSession(sessionId);
    if (response.success && response.data) {
      console.log(`Session ended with summary: ${response.data.summary}`);
      return response.data.summary;
    }
  } catch (error) {
    console.error('Failed to end session:', error);
  }
};
```

#### Conversation

```typescript
// Send audio message
const sendAudio = async (sessionId, audioBlob) => {
  try {
    const response = await apiClient.sendAudioMessage(sessionId, audioBlob);
    if (response.success && response.data) {
      // Handle messages (user message and AI response)
      const messages = response.data.messages;
      console.log('Received messages:', messages);
      return messages;
    }
  } catch (error) {
    console.error('Failed to send audio:', error);
  }
};

// Get conversation history
const getHistory = async (sessionId) => {
  try {
    const response = await apiClient.getConversationHistory(sessionId);
    if (response.success && response.data) {
      const messages = response.data.messages;
      console.log('Conversation history:', messages);
      return messages;
    }
  } catch (error) {
    console.error('Failed to get conversation history:', error);
  }
};
```

## Migrating from Old API Services

### Before

```typescript
import { 
  createSession, 
  sendAudio,
  getHistory, 
  endSession 
} from '@/services/api/session';

// Component code
const startSession = async () => {
  try {
    const { sessionId } = await createSession();
    setSessionId(sessionId);
  } catch (err) {
    handleError(err);
  }
};

const handleRecording = async (audioBlob) => {
  try {
    const response = await sendAudio(sessionId, audioBlob);
    // Handle response
  } catch (err) {
    handleError(err);
  }
};
```

### After

```typescript
import { getApiClient } from '@/services/api/client';

// Component code
const apiClient = getApiClient();

const startSession = async () => {
  try {
    const response = await apiClient.createSession();
    if (response.success && response.data) {
      setSessionId(response.data.sessionId);
    } else {
      throw new Error(response.error || 'Failed to create session');
    }
  } catch (err) {
    handleError(err);
  }
};

const handleRecording = async (audioBlob) => {
  try {
    const response = await apiClient.sendAudioMessage(sessionId, audioBlob);
    if (response.success && response.data) {
      // Handle messages
      handleMessages(response.data.messages);
    } else {
      throw new Error(response.error || 'Failed to process audio');
    }
  } catch (err) {
    handleError(err);
  }
};
```

## Error Handling

```typescript
const performApiOperation = async () => {
  try {
    const response = await apiClient.someOperation();
    
    if (response.success) {
      // Handle successful response
      return response.data;
    } else {
      // Handle API error
      console.error('API Error:', response.error);
      // Show user-friendly error message
    }
  } catch (error) {
    // Handle network/unexpected errors
    console.error('Unexpected error:', error);
    // Show generic error message
  }
};
```

## Testing with the Mock Implementation

During development, the API client uses the mock implementation by default:

```typescript
import { resetApiClient } from '@/services/api/client';

// For local development with mock API
resetApiClient({ useMock: true });

// When backend is available
resetApiClient({ useMock: false, baseUrl: 'https://api.kukucoach.com' });
```