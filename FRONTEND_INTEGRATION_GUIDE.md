# 🚀 Frontend-Backend Integration Guide

## 🎯 **Integration Overview**

Your frontend is **perfectly positioned** for backend integration! The architecture is already REST API-based with a mock client that can be easily swapped for the real backend.

## ⚡ **Quick Start Steps**

### **Step 1: Update Frontend API Configuration**

In your frontend project, modify `src/services/api/client.ts`:

```typescript
const DEFAULT_CONFIG: ApiClientConfig = {
  baseUrl: 'http://localhost:8000/api', // Your backend URL
  useMock: false, // Switch from mock to real API
  timeout: 30000
};
```

### **Step 2: Create Real API Client**

Create `src/services/api/real/RealApiClient.ts` in your frontend:

```typescript
import { KukuCoachApiClient, ApiClientConfig, SessionData, ConversationMessage } from '../types';

export class RealApiClient implements KukuCoachApiClient {
  constructor(private config: ApiClientConfig) {}

  async createSession(): Promise<SessionData> {
    const response = await fetch(`${this.config.baseUrl}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) throw new Error('Failed to create session');
    const data = await response.json();
    return data.data;
  }

  async sendAudio(sessionId: string, audioBlob: Blob): Promise<ConversationMessage[]> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    const response = await fetch(`${this.config.baseUrl}/sessions/${sessionId}/audio`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Failed to send audio');
    const data = await response.json();
    return data.data.messages;
  }

  async getMessages(sessionId: string): Promise<ConversationMessage[]> {
    const response = await fetch(`${this.config.baseUrl}/sessions/${sessionId}/messages`);
    
    if (!response.ok) throw new Error('Failed to get messages');
    const data = await response.json();
    return data.data.messages;
  }
}
```

### **Step 3: Update Client Factory**

Modify `src/services/api/client.ts` to use the real client:

```typescript
import { RealApiClient } from './real/RealApiClient';

export const createApiClient: ApiClientFactory = (config) => {
  const mergedConfig: ApiClientConfig = { ...DEFAULT_CONFIG, ...config };
  
  if (mergedConfig.useMock) {
    return new MockApiClient(mergedConfig);
  }
  return new RealApiClient(mergedConfig); // Add this line
};
```

## 🔄 **Frontend-Backend API Mapping**

| Frontend Feature | Backend Endpoint | Request Format | Response Format |
|------------------|------------------|----------------|-----------------|
| **Session Creation** | `POST /api/sessions` | `{}` | `{success: true, data: {sessionId: string}}` |
| **Audio Upload** | `POST /api/sessions/{sessionId}/audio` | `FormData` with audio file | `{success: true, data: {messages: Message[]}}` |
| **Message History** | `GET /api/sessions/{sessionId}/messages` | None | `{success: true, data: {messages: Message[]}}` |
| **Audio Playback** | `GET /audio/{filename}` | None | Audio file (MP3) |

## 🎵 **Audio Integration Details**

### **Frontend Audio Recording:**
- Records in `webm` format using MediaRecorder API
- Sends as `FormData` with key `audio`
- Filename: `recording.webm`

### **Backend Audio Processing:**
- Receives audio file via FastAPI `UploadFile`
- Transcribes using OpenAI Whisper
- Generates AI response using conversation logic
- Creates TTS audio file in `temp_audio/` directory
- Returns JSON with `audioUrl` field pointing to static file

### **Frontend Audio Playback:**
- Receives `audioUrl` in message response
- Creates HTML5 Audio element
- Plays audio with real-time visualization
- Handles audio level monitoring for UI effects

## 🧪 **Testing Plan**

### **Phase 1: Basic Connection**
1. ✅ Start backend: `python start_api.py`
2. ✅ Verify health endpoint: `curl http://localhost:8000/health`
3. 🔄 Update frontend config to use real API
4. 🔄 Test session creation in frontend

### **Phase 2: Audio Flow**
1. 🔄 Test audio recording in frontend
2. 🔄 Verify audio upload to backend
3. 🔄 Check transcription and AI response
4. 🔄 Test audio playback from backend URL

### **Phase 3: Full Integration**
1. 🔄 End-to-end conversation flow
2. 🔄 Session persistence across page reloads
3. 🔄 Error handling and recovery
4. 🔄 Audio visualization during playback

## 📁 **Key Files to Modify in Frontend**

### **Configuration Files:**
- `src/services/api/client.ts` - Switch from mock to real API
- `src/services/api/types.ts` - Verify type definitions match backend

### **New Files to Create:**
- `src/services/api/real/RealApiClient.ts` - HTTP client implementation
- `src/services/api/real/index.ts` - Export real client

### **Files to Verify:**
- `src/hooks/useConversation.ts` - Should work without changes
- `src/contexts/SessionContext.tsx` - Should work without changes
- `src/components/kuku-coach/kuku-coach.tsx` - Should work without changes

## 🔧 **Environment Configuration**

### **Frontend Environment Variables:**
Create `.env.local` in frontend root:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK_API=false
```

### **Backend CORS Configuration:**
Already configured in `app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚨 **Common Integration Issues & Solutions**

### **Issue 1: CORS Errors**
- **Symptom**: Browser blocks requests to backend
- **Solution**: Verify CORS middleware in `app.py` includes frontend URL

### **Issue 2: Audio Format Mismatch**
- **Symptom**: Backend can't process audio file
- **Solution**: Ensure frontend sends `webm` format, backend handles it

### **Issue 3: Session ID Mismatch**
- **Symptom**: Messages not appearing or session errors
- **Solution**: Verify session ID consistency between frontend and backend

### **Issue 4: Audio URLs Not Working**
- **Symptom**: Audio files return 404 errors
- **Solution**: Verify static file serving is configured in `app.py`

## 🎉 **Success Indicators**

You'll know integration is successful when:
- ✅ Frontend creates sessions and receives valid session IDs
- ✅ Audio recording uploads successfully to backend
- ✅ Backend transcribes audio and returns AI responses
- ✅ Frontend plays AI audio responses with visualization
- ✅ Conversation history persists and displays correctly
- ✅ No CORS or network errors in browser console

## 📞 **Next Steps After Integration**

1. **Performance Testing**: Test with longer audio files
2. **Error Handling**: Test network failures and recovery
3. **Mobile Testing**: Verify audio works on mobile devices
4. **Production Deployment**: Configure for production URLs
5. **Monitoring**: Add logging and analytics

---

## 🎯 **Ready to Integrate?**

Your backend is **fully functional** and your frontend is **architecturally ready**. The integration should be straightforward since both sides are designed to work together!

**Start with Step 1** above and work through each phase systematically. The mock API client in your frontend makes this transition seamless. 