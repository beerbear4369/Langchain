# Deployment Log

## 2025-06-16: AI Model Enhancement - gpt41mini_hyper2 Deployment

**MAJOR UPDATE**: Upgraded AI coaching model to enhance conversation quality and emotional intelligence.

### Changes Made:
- **Model Update**: Migrated from previous model to `gpt41mini_hyper2`
- **Model ID**: `ft:gpt-4.1-mini-2025-04-14:kuku-tech:coach-prompt10-purevetted49-basemodel-outofshell-parachange2:Bj66Dtia`
- **Key Enhancement**: Enhanced emotional intelligence (EQ) in coaching prompts
- **Training Data**: 49 vetted coaching dialogs for improved conversation quality
- **Base Model**: GPT-4.1-mini (2025-04-14)

### Expected Impact:
- More emotionally aware coaching responses
- Better understanding of user emotional context
- Improved coaching effectiveness and user satisfaction
- Enhanced conversation flow following proven coaching patterns

### Technical Details:
- Updated `config.py` line 58: `MODEL_NAME = AVAILABLE_MODELS["gpt41mini_hyper2"]`
- No changes required to API endpoints or conversation logic
- Backward compatible with existing session management

### Memory Bank Updates:
- Updated techContext.md to reflect new model specifications
- Updated activeContext.md to focus on model enhancement
- Updated progress.md to highlight improved AI capabilities
- Updated productContext.md to emphasize emotional intelligence features

---

     ==> Deploying...
==> Running 'uvicorn app:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process [103]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
=== Config Debug Info ===
Python executable: /opt/render/project/src/.venv/bin/python
Current working directory: /opt/render/project/src
Not running from PyInstaller package
Final API key status: Set
=== End Config Debug Info ===
Warning: pyaudio not available - record_audio function disabled
Warning: sounddevice not available - play_audio function disabled
⚠️ Database service not available: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required
INFO:     127.0.0.1:38416 - "HEAD / HTTP/1.1" 405 Method Not Allowed
     ==> Your service is live 🎉
INFO:     35.247.111.159:0 - "GET / HTTP/1.1" 200 OK
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [108]
  self.memory = ConversationSummaryBufferMemory(
/opt/render/project/src/conversation.py:135: LangChainDeprecationWarning: The class `ConversationChain` was deprecated in LangChain 0.2.7 and will be removed in 1.0. Use :meth:`~RunnableWithMessageHistory: https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html` instead.
  self.conversation = ConversationChain(
INFO:     54.254.158.144:0 - "POST /api/sessions HTTP/1.1" 200 OK
     ==> Detected service running on port 10000
     ==> Docs on specifying a port: https://render.com/docs/web-services#port-binding
INFO:     54.254.158.144:0 - "GET /health HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "POST /api/sessions HTTP/1.1" 200 OK
Starting transcription...
Transcription completed in 2.67 seconds
Attempting TTS generation for: Hi Ian, what would you like to explore or achieve ...
Audio file path: temp_audio/response-msg-e2221597.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-e2221597.mp3
INFO:     54.254.158.144:0 - "POST /api/sessions/session-6ea874c83e/messages HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "GET /audio/response-msg-e2221597.mp3 HTTP/1.1" 206 Partial Content
     ==> Deploying...
==> Running 'uvicorn app:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process [104]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
     ==> Your service is live 🎉
=== Config Debug Info ===
Python executable: /opt/render/project/src/.venv/bin/python
Current working directory: /opt/render/project/src
Not running from PyInstaller package
Final API key status: Set
=== End Config Debug Info ===
Warning: pyaudio not available - record_audio function disabled
Warning: sounddevice not available - play_audio function disabled
✅ Database service loaded successfully
INFO:     127.0.0.1:55112 - "HEAD / HTTP/1.1" 405 Method Not Allowed
Starting transcription...
Transcription completed in 1.67 seconds
INFO:     54.254.158.144:0 - "POST /api/sessions/session-6ea874c83e/messages HTTP/1.1" 200 OK
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [103]
INFO:     54.254.158.144:0 - "GET /health HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "OPTIONS /api/sessions HTTP/1.1" 200 OK
/opt/render/project/src/conversation.py:107: LangChainDeprecationWarning: Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/
  self.memory = ConversationSummaryBufferMemory(
/opt/render/project/src/conversation.py:135: LangChainDeprecationWarning: The class `ConversationChain` was deprecated in LangChain 0.2.7 and will be removed in 1.0. Use :meth:`~RunnableWithMessageHistory: https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html` instead.
  self.conversation = ConversationChain(
✅ Session session-56ee77d980 created in database
INFO:     54.254.158.144:0 - "POST /api/sessions HTTP/1.1" 200 OK
     ==> Detected service running on port 10000
     ==> Docs on specifying a port: https://render.com/docs/web-services#port-binding
Starting transcription...
Transcription completed in 1.04 seconds
Attempting TTS generation for: What would you like to explore or accomplish today...
Audio file path: temp_audio/response-msg-9e387951.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-9e387951.mp3
🔍 DEBUG update_session called:
  session_id: session-56ee77d980
  updates: {'message_count': 2, 'updated_at': '2025-06-10T19:56:21.727303Z'}
🔍 Supabase update result: [{'id': '37c222dc-9bc5-4cef-80a7-a789e16434e2', 'session_id': 'session-56ee77d980', 'user_id': None, 'status': 'active', 'created_at': '2025-06-10T19:50:31.762804+00:00', 'updated_at': '2025-06-10T19:56:21.727303+00:00', 'ended_at': None, 'message_count': 2, 'summary': None, 'duration_seconds': None, 'rating': None, 'feedback': None}]
✅ Updated message_count to 2 in database for session session-56ee77d980
✅ Message msg-7697de98 saved to database
✅ Message msg-41c28fcc saved to database
INFO:     54.254.158.144:0 - "POST /api/sessions/session-56ee77d980/messages HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "GET /health HTTP/1.1" 200 OK
Starting transcription...
Transcription completed in 0.90 seconds
Attempting TTS generation for: Help me understand what isn't working for you righ...
Audio file path: temp_audio/response-msg-1d39672b.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-1d39672b.mp3
🔍 DEBUG update_session called:
  session_id: session-56ee77d980
  updates: {'message_count': 4, 'updated_at': '2025-06-10T19:56:25.782069Z'}
🔍 Supabase update result: [{'id': '37c222dc-9bc5-4cef-80a7-a789e16434e2', 'session_id': 'session-56ee77d980', 'user_id': None, 'status': 'active', 'created_at': '2025-06-10T19:50:31.762804+00:00', 'updated_at': '2025-06-10T19:56:25.782069+00:00', 'ended_at': None, 'message_count': 4, 'summary': None, 'duration_seconds': None, 'rating': None, 'feedback': None}]
✅ Updated message_count to 4 in database for session session-56ee77d980
✅ Message msg-c3e71454 saved to database
✅ Message msg-ccb931d0 saved to database
INFO:     54.254.158.144:0 - "POST /api/sessions/session-56ee77d980/messages HTTP/1.1" 200 OK
Starting transcription...
Transcription completed in 0.95 seconds
Attempting TTS generation for: What specific outcome were you expecting that isn't working for you right now...
Audio file path: temp_audio/response-msg-b4f0287b.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-b4f0287b.mp3
🔍 DEBUG update_session called:
  session_id: session-56ee77d980
  updates: {'message_count': 6, 'updated_at': '2025-06-10T19:56:31.833561Z'}
🔍 Supabase update result: [{'id': '37c222dc-9bc5-4cef-80a7-a789e16434e2', 'session_id': 'session-56ee77d980', 'user_id': None, 'status': 'active', 'created_at': '2025-06-10T19:50:31.762804+00:00', 'updated_at': '2025-06-10T19:56:31.833561+00:00', 'ended_at': None, 'message_count': 6, 'summary': None, 'duration_seconds': None, 'rating': None, 'feedback': None}]
✅ Updated message_count to 6 in database for session session-56ee77d980
✅ Message msg-4ec47808 saved to database
✅ Message msg-5692b219 saved to database
INFO:     54.254.158.144:0 - "POST /api/sessions/session-56ee77d980/messages HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "GET /health HTTP/1.1" 200 OK
✅ Session session-172f51b404 created in database
INFO:     54.254.158.144:0 - "POST /api/sessions HTTP/1.1" 200 OK
Starting transcription...
Transcription completed in 0.97 seconds
Attempting TTS generation for: Help me understand—what are you referring to that isn't working for you right now...
Audio file path: temp_audio/response-msg-e1c3b357.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-e1c3b357.mp3
🔍 DEBUG update_session called:
  session_id: session-172f51b404
  updates: {'message_count': 2, 'updated_at': '2025-06-10T19:57:37.790128Z'}
🔍 Supabase update result: [{'id': '6297aa41-2584-4bf4-82ac-778b31f91cba', 'session_id': 'session-172f51b404', 'user_id': None, 'status': 'active', 'created_at': '2025-06-10T19:56:44.57597+00:00', 'updated_at': '2025-06-10T19:57:37.790128+00:00', 'ended_at': None, 'message_count': 2, 'summary': None, 'duration_seconds': None, 'rating': None, 'feedback': None}]
✅ Updated message_count to 2 in database for session session-172f51b404
✅ Message msg-91301e33 saved to database
✅ Message msg-2df85219 saved to database
INFO:     54.254.158.144:0 - "POST /api/sessions/session-172f51b404/messages HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "GET /audio/response-msg-e1c3b357.mp3 HTTP/1.1" 206 Partial Content
Starting transcription...
Transcription completed in 1.39 seconds
Attempting TTS generation for: Thanks for sharing, Steven. What would you like to...
Audio file path: temp_audio/response-msg-ea7a491e.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-ea7a491e.mp3
🔍 DEBUG update_session called:
  session_id: session-172f51b404
  updates: {'message_count': 4, 'updated_at': '2025-06-10T19:58:19.011349Z'}
🔍 Supabase update result: [{'id': '6297aa41-2584-4bf4-82ac-778b31f91cba', 'session_id': 'session-172f51b404', 'user_id': None, 'status': 'active', 'created_at': '2025-06-10T19:56:44.57597+00:00', 'updated_at': '2025-06-10T19:58:19.011349+00:00', 'ended_at': None, 'message_count': 4, 'summary': None, 'duration_seconds': None, 'rating': None, 'feedback': None}]
✅ Updated message_count to 4 in database for session session-172f51b404
✅ Message msg-8937008a saved to database
✅ Message msg-9094ae18 saved to database
INFO:     54.254.158.144:0 - "POST /api/sessions/session-172f51b404/messages HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "GET /audio/response-msg-ea7a491e.mp3 HTTP/1.1" 206 Partial Content
Starting transcription...
Transcription completed in 1.84 seconds
Attempting TTS generation for: What function are you referring to, and what does ...
Audio file path: temp_audio/response-msg-f0d6666e.mp3
TTS successful, checking if file exists: True
Audio URL set to: /audio/response-msg-f0d6666e.mp3
🔍 DEBUG update_session called:
  session_id: session-172f51b404
  updates: {'message_count': 6, 'updated_at': '2025-06-10T19:59:08.947065Z'}
🔍 Supabase update result: [{'id': '6297aa41-2584-4bf4-82ac-778b31f91cba', 'session_id': 'session-172f51b404', 'user_id': None, 'status': 'active', 'created_at': '2025-06-10T19:56:44.57597+00:00', 'updated_at': '2025-06-10T19:59:08.947065+00:00', 'ended_at': None, 'message_count': 6, 'summary': None, 'duration_seconds': None, 'rating': None, 'feedback': None}]
✅ Updated message_count to 6 in database for session session-172f51b404
✅ Message msg-8f45fc71 saved to database
✅ Message msg-dea11898 saved to database
INFO:     54.254.158.144:0 - "POST /api/sessions/session-172f51b404/messages HTTP/1.1" 200 OK
INFO:     54.254.158.144:0 - "GET /audio/response-msg-f0d6666e.mp3 HTTP/1.1" 206 Partial Content