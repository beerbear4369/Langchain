# 🚀 Postman Testing Guide for Kuku Coach API

## Prerequisites
1. **Download Postman**: Get the latest version from [postman.com](https://www.postman.com/downloads/)
2. **API Server Running**: Make sure your API is running on `http://localhost:8000`
3. **Audio Files**: Prepare some test audio files (MP3, WAV, WebM format)

## 📥 Step 1: Import the Collection

### Method 1: Import from File
1. **Open Postman**
2. **Click "Import"** (top left corner)
3. **Select "Upload Files"**
4. **Choose** `Kuku_Coach_API_Postman_Collection.json` from your project folder
5. **Click "Import"**

### Method 2: Import from Raw JSON
1. **Open Postman**
2. **Click "Import"** → **"Raw text"**
3. **Copy and paste** the entire content of `Kuku_Coach_API_Postman_Collection.json`
4. **Click "Continue"** → **"Import"**

## 🎯 Step 2: Set Up Environment (Optional but Recommended)

1. **Click the gear icon** (⚙️) in top right → **"Manage Environments"**
2. **Click "Add"** to create new environment
3. **Name it**: `Kuku Coach Local`
4. **Add variables**:
   - Variable: `base_url` | Initial Value: `http://localhost:8000`
   - Variable: `session_id` | Initial Value: (leave empty)
5. **Click "Save"**
6. **Select this environment** from the dropdown (top right)

## 🧪 Step 3: Start API Server

```bash
# In your project directory
python start_api.py
```

Wait until you see: `INFO: Uvicorn running on http://0.0.0.0:8000`

## 🔍 Step 4: Run Basic Tests (In Order)

### Test 1: Health Check ✅
1. **Select** "1. Health Check" request
2. **Click "Send"**
3. **Verify**: Status `200 OK` and response shows `"status": "healthy"`

### Test 2: API Root Info ✅
1. **Select** "2. API Root Info" request  
2. **Click "Send"**
3. **Verify**: Response shows API name and version

### Test 3: Create Session ✅
1. **Select** "3. Create Session" request
2. **Click "Send"**
3. **Verify**: 
   - Status `200 OK`
   - Response has `"success": true`
   - A `sessionId` is returned (this gets auto-saved for next tests)

### Test 4: Get Session Status ✅
1. **Select** "4. Get Session Status" request
2. **Click "Send"**
3. **Verify**: Session details are returned with status `"active"`

## 🎤 Step 5: Audio Testing (CRITICAL!)

This is the most important test that validates your core functionality:

### Test 5: Send Audio Message 🔊
1. **Select** "5. Send Audio Message (MAIN TEST)" request
2. **In the Body tab**:
   - You'll see a form-data field named `audio`
   - **Click "Select Files"** next to the `audio` field
   - **Choose a real audio file** (MP3, WAV, or WebM)
   - **Recommended**: Record a short voice message saying "Hello, I need help with my depression"
3. **Click "Send"**
4. **Expected Results**:
   - Status: `200 OK`
   - Response contains both user and AI messages
   - User message has transcribed text from your audio
   - AI message has a coaching response
   - AI message may include `audioUrl` for TTS response

### Test 6: Get Conversation History ✅
1. **Select** "6. Get Conversation History" request
2. **Click "Send"**
3. **Verify**: All messages from the conversation are returned

### Test 7: End Session ✅
1. **Select** "8. End Session" request
2. **Click "Send"**
3. **Verify**: Session summary and statistics are returned

## 📊 Reading Test Results

### In the Response Section:
- **Status**: Should be `200 OK` for successful requests
- **Body**: Contains the JSON response data
- **Console**: Check for any logged information from test scripts

### In the Tests Tab:
- **Green checkmarks**: ✅ Tests passed
- **Red X marks**: ❌ Tests failed
- **Console output**: Additional debugging information

## 🔧 Common Issues & Solutions

### Issue 1: "Connection refused" or "Network Error"
**Solution**: 
- Make sure API server is running: `python start_api.py`
- Check the correct URL: `http://localhost:8000`

### Issue 2: Audio upload fails
**Solutions**:
- Use smaller audio files (< 10MB)
- Try different formats: MP3, WAV, WebM
- Ensure file isn't corrupted

### Issue 3: "Session not found"
**Solution**: 
- Run tests in order (Create Session first)
- If session_id gets lost, create a new session

### Issue 4: OpenAI API errors
**Solution**: 
- Check your OpenAI API key in `config.py`
- Ensure you have API credits available

## 🎯 What to Focus On

### 🔴 **CRITICAL TESTS** (Must Pass):
1. **Health Check** - Confirms API is running
2. **Create Session** - Core session management
3. **Send Audio Message** - Main functionality (transcription + AI response)
4. **End Session** - Session lifecycle

### 🟡 **Important Tests**:
- Get Session Status
- Get Conversation History
- Error handling tests

## 📈 Advanced Testing

### Test with Different Audio Types:
1. **Short audio** (< 10 seconds): Quick responses
2. **Long audio** (30+ seconds): Complex questions
3. **Different emotions**: Happy, sad, frustrated voices
4. **Background noise**: Test robustness
5. **Different languages**: If supported

### Load Testing:
1. Create multiple sessions simultaneously
2. Send rapid consecutive messages
3. Test session timeout behavior

## 🚀 Next Steps After Postman Testing

If all Postman tests pass ✅:
1. **Proceed to frontend integration** 
2. **Deploy to Render.com** (use `render.yaml`)
3. **Update frontend API endpoint** to your deployed URL

If tests fail ❌:
1. **Check console logs** for detailed error messages
2. **Verify OpenAI API configuration**
3. **Test with different audio files**
4. **Report specific error messages** for debugging

## 📝 Test Report Template

After testing, document your results:

```
## Postman Test Results - [Date]

### Basic Functionality ✅/❌
- [ ] Health Check
- [ ] Create Session  
- [ ] Get Session Status
- [ ] Send Audio Message
- [ ] Get Conversation History
- [ ] End Session

### Audio Testing Results ✅/❌
- [ ] MP3 upload
- [ ] WAV upload  
- [ ] WebM upload
- [ ] Transcription accuracy
- [ ] AI response quality
- [ ] TTS audio generation

### Performance Notes:
- Average response time: ___ms
- Audio processing time: ___ms
- Any timeouts or delays: ___

### Issues Found:
- List any problems encountered
- Include error messages
- Note which audio files work/don't work
```

## 🎉 Success Criteria

**Your API is ready for frontend integration when**:
- ✅ All basic tests pass
- ✅ Audio upload and transcription works
- ✅ AI responses are generated
- ✅ Session management works correctly
- ✅ Error handling is graceful

Good luck with your testing! 🚀 