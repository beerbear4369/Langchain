# Kuku Coach API

FastAPI wrapper for the Kuku Coach voice coaching assistant, providing RESTful endpoints for frontend integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key configured in `config.py`
- Required dependencies (see Installation)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure OpenAI API key:**
Ensure your `config.py` file contains your OpenAI API key.

3. **Start the API server:**
```bash
python start_api.py
```

The API will be available at: `http://localhost:8000`

### API Documentation
- **Interactive Docs**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

## 📋 API Endpoints

All endpoints follow the integration specification in `integration documentation/`.

### Session Management

#### Create Session
```http
POST /api/sessions
```
**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "session-1234567890",
    "createdAt": "2023-06-15T10:30:00Z",
    "status": "active",
    "messageCount": 0
  }
}
```

#### Get Session Status
```http
GET /api/sessions/{sessionId}
```

#### End Session
```http
POST /api/sessions/{sessionId}/end
```
**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "session-1234567890",
    "summary": "Session summary...",
    "duration": 300,
    "messageCount": 6
  }
}
```

### Conversation

#### Send Audio Message
```http
POST /api/sessions/{sessionId}/messages
Content-Type: multipart/form-data

audio: [audio file]
```
**Supported formats**: MP3, WAV, WebM

**Response:**
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
        "audioUrl": "/audio/response-456.mp3"
      }
    ]
  }
}
```

#### Get Conversation History
```http
GET /api/sessions/{sessionId}/messages
```

## 🧪 Testing

### Run Test Suite
```bash
# Install test dependencies
pip install pytest requests

# Start API server (in separate terminal)
python start_api.py

# Run tests
python test_api.py
```

### Test Coverage
The test suite covers all requirements from `integration-testing-plan.md`:

**Session Creation (S-01, S-02, S-03)**
- ✅ Create new session with valid ID
- ✅ Create multiple unique sessions  
- ✅ Handle invalid requests

**Session Status (S-04, S-05, S-06)**
- ✅ Get existing session details
- ✅ Handle non-existent sessions
- ✅ Handle invalid session ID formats

**Audio Conversation (A-01, A-02, A-03, A-04, A-05)**
- ✅ Process audio messages
- ✅ Handle different audio formats
- ✅ Validate audio data
- ✅ Handle session errors

**Conversation History (H-01, H-02, H-03, H-04)**
- ✅ Empty history for new sessions
- ✅ Complete message history
- ✅ Chronological message order

**End Session (E-01, E-02, E-03)**
- ✅ Generate session summaries
- ✅ Prevent double-ending
- ✅ Handle invalid sessions

### Integration Flow Test
```bash
# Complete user journey test
python -m pytest test_api.py::TestKukuCoachAPI::test_complete_user_journey -v
```

## 🌐 Deployment

### Render.com (Recommended)

1. **Connect your repository** to Render.com
2. **Use the provided configuration** (`render.yaml`)
3. **Set environment variables**:
   - Add your OpenAI API key securely
   - Configure any other required settings

4. **Deploy**: Render will automatically build and deploy your API

### Alternative Deployment Options

#### Docker
```bash
# Build image
docker build -t kuku-coach-api .

# Run container  
docker run -p 8000:8000 kuku-coach-api
```

#### Manual Server Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Start with production settings
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🎯 Features

### ✅ Implemented
- **5 Core API Endpoints** as specified in integration docs
- **Session Management** with 30-round limit
- **Audio Processing** (MP3, WAV, WebM support)
- **Automatic Wrap-up Logic** at conversation threshold
- **Comprehensive Error Handling**
- **CORS Support** for frontend integration
- **Interactive API Documentation**
- **Complete Test Suite**
- **Deployment Ready** (Render.com config)

### 🔄 Session Flow
1. **Create Session** → Get unique session ID
2. **Send Audio** → Get transcription + AI response with TTS
3. **Auto Wrap-up** → AI prompts to end session around round 25-28
4. **End Session** → Generate summary and cleanup

### 🛡️ Error Handling
All endpoints return consistent error format:
```json
{
  "success": false,
  "error": "Error description"
}
```

Common error scenarios:
- Session not found
- Invalid audio format
- Audio processing failures
- Session already ended
- Transcription errors

## 🔧 Development

### Local Development
```bash
# Start with auto-reload
python start_api.py --reload

# Custom port
python start_api.py --port 8080

# Help
python start_api.py --help
```

### Project Structure
```
├── app.py                 # Main FastAPI application
├── start_api.py          # Development startup script
├── test_api.py           # Comprehensive test suite
├── render.yaml           # Render.com deployment config
├── requirements.txt      # Dependencies
├── conversation.py       # Existing conversation logic
├── audio_input.py        # Audio transcription
├── audio_output.py       # Text-to-speech
└── config.py            # Configuration
```

## 📈 Next Steps

### Future Enhancements
1. **Authentication System** (JWT tokens)
2. **Database Integration** (replace in-memory storage)
3. **Audio File Serving** (proper static file handling)
4. **Rate Limiting** (prevent abuse)
5. **Conversation Analytics** (usage tracking)
6. **WebSocket Support** (real-time communication)

### Frontend Integration
The API is ready for frontend integration following the specifications in:
- `frontend-api-integration.md` 
- `sample-api-payloads.md`
- `backend-integration.md`

All endpoints return exactly the expected JSON schemas for seamless integration.

## 🆘 Troubleshooting

### Common Issues

**"Session not found" errors**
- Sessions are stored in memory and reset on server restart
- Ensure session ID is correct and hasn't expired

**Audio transcription failures** 
- Check audio file format (MP3, WAV, WebM)
- Verify OpenAI API key is configured
- Ensure audio file is not corrupted

**CORS errors**
- API includes CORS middleware for all origins
- Configure specific origins for production

**Import errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

For more help, check the integration documentation in `integration documentation/` folder. 