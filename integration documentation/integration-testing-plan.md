# Integration Testing Plan - MVP

This document outlines the testing plan for the five essential API endpoints needed for the Kuku Coach MVP.

## Essential Endpoints to Test

1. `POST /api/sessions` - Create a new coaching session
2. `GET /api/sessions/{sessionId}` - Get session status
3. `POST /api/sessions/{sessionId}/messages` - Send audio and get AI response
4. `GET /api/sessions/{sessionId}/messages` - Get conversation history
5. `POST /api/sessions/{sessionId}/end` - End session and get summary

## Test Cases

### 1. Session Creation

| Test ID | Description | Expected Outcome | Priority |
|---------|-------------|------------------|----------|
| S-01    | Create new session | Successfully returns valid session ID | HIGH |
| S-02    | Create multiple sessions | Each session has a unique ID | MEDIUM |
| S-03    | Create session with invalid request format | Returns appropriate error | LOW |

### 2. Session Status

| Test ID | Description | Expected Outcome | Priority |
|---------|-------------|------------------|----------|
| S-04    | Get existing session | Successfully returns session details | HIGH |
| S-05    | Get non-existent session | Returns appropriate error | MEDIUM |
| S-06    | Get session with invalid ID format | Returns validation error | LOW |

### 3. Audio Conversation

| Test ID | Description | Expected Outcome | Priority |
|---------|-------------|------------------|----------|
| A-01    | Send short audio message | Returns transcription and AI response | HIGH |
| A-02    | Send longer audio message (30s) | Successfully processes longer audio | MEDIUM |
| A-03    | Send audio in different formats (MP3, WAV, WebM) | Successfully handles different formats | MEDIUM |
| A-04    | Send malformed audio data | Returns appropriate error | MEDIUM |
| A-05    | Send audio to non-existent session | Returns appropriate error | MEDIUM |

### 4. Conversation History

| Test ID | Description | Expected Outcome | Priority |
|---------|-------------|------------------|----------|
| H-01    | Get history for new session | Returns empty message array | MEDIUM |
| H-02    | Get history after sending messages | Returns complete message history | HIGH |
| H-03    | Get history for non-existent session | Returns appropriate error | MEDIUM |
| H-04    | Verify message order in history | Messages in chronological order | MEDIUM |

### 5. End Session

| Test ID | Description | Expected Outcome | Priority |
|---------|-------------|------------------|----------|
| E-01    | End active session | Successfully ends session and returns summary | HIGH |
| E-02    | End already ended session | Returns appropriate error | MEDIUM |
| E-03    | End non-existent session | Returns appropriate error | MEDIUM |

## Test Flow

For comprehensive testing, execute tests in this sequence:

1. Create session (S-01)
2. Verify session status (S-04)
3. Send audio message (A-01)
4. Verify conversation history (H-02)
5. End session (E-01)

## Test Environment Setup

### Frontend Configuration

```typescript
// In src/services/api/client.ts
import { resetApiClient } from '@/services/api/client';

// For local development against real backend
resetApiClient({
  useMock: false,
  baseUrl: 'http://localhost:8080/api'
});
```

### Backend Configuration

The backend should be configured to:

1. Allow CORS from the frontend development server
2. Log all API requests for debugging
3. Return standardized error formats

## Test Data

### Test Audio Files

Create a collection of test audio files:
- Short samples (5 seconds)
- Medium samples (15-30 seconds)
- Different formats (MP3, WAV, WebM)

## Implementation Priorities

To facilitate incremental testing and development, backend implementation should follow this priority order:

1. POST /api/sessions (Create session)
2. POST /api/sessions/{sessionId}/messages (Send audio)
3. GET /api/sessions/{sessionId}/messages (Get conversation history)
4. GET /api/sessions/{sessionId} (Check session status)
5. POST /api/sessions/{sessionId}/end (End session)

## Success Criteria

Integration testing will be considered successful when:

1. All HIGH priority tests pass with the expected outcomes
2. Response times are within acceptable limits (< 5 seconds for audio processing)
3. Error handling correctly manages expected failure modes
4. Complete user journey can be completed without errors

## Testing Schedule

| Phase | Focus Area | Deliverables |
|------|------------|--------------|
| 1    | Individual endpoint testing | Validation of each endpoint in isolation |
| 2    | End-to-end flow testing | Validation of complete user journey |

## Issue Tracking

All issues discovered during testing should be documented with:
1. Test ID
2. Issue description
3. Steps to reproduce
4. Expected vs. actual outcome
5. Severity (Critical, Major, Minor, Cosmetic)