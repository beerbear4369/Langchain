import uuid
import shutil
import os
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from conversation import Conversation # Assuming conversation.py exists and is importable
from audio_input import transcribe_audio
from audio_output import text_to_speech_file as text_to_speech_save_file # Renamed for clarity
# import config # Assuming config.py exists and is configured

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Ensure static/audio directory exists (consider moving to config.py or startup event)
STATIC_AUDIO_DIR = "static/audio" 
os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=STATIC_AUDIO_DIR), name="audio_files")

# Generic Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error. Please try again later."}
    )

# In-memory storage for sessions
sessions = {}

# Pydantic Models
class SessionData(BaseModel):
    sessionId: str
    createdAt: datetime
    status: str

class CreateSessionResponse(BaseModel):
    success: bool = True
    data: SessionData

class GetSessionData(SessionData):
    updatedAt: datetime
    messageCount: int

class GetSessionResponse(BaseModel):
    success: bool = True
    data: GetSessionData

class EndSessionData(BaseModel):
    sessionId: str
    summary: str
    duration: int # Assuming duration is in seconds
    messageCount: int

class EndSessionResponse(BaseModel):
    success: bool = True
    data: EndSessionData

# Pydantic Models for Conversation History
class Message(BaseModel):
    id: str
    timestamp: datetime
    sender: str # "user" or "ai"
    text: str
    audioUrl: str | None = None

class ConversationHistoryData(BaseModel):
    messages: list[Message]

class ConversationHistoryResponse(BaseModel):
    success: bool = True
    data: ConversationHistoryData

# Pydantic Models for Sending Messages
class SendMessageData(BaseModel):
    messages: list[Message] # Typically user's transcribed message and AI's response

class SendMessageResponse(BaseModel):
    success: bool = True
    data: SendMessageData

# Refactored audio functions (to be placed here or imported appropriately)
# For now, defining them in-place for clarity, will move if they become too large

# The previously in-place defined transcribe_audio_file and text_to_speech_file 
# are now expected to be imported from audio_input.py and audio_output.py (as text_to_speech_save_file)
# These utility functions in audio_input/output should use logging instead of print.

@app.get("/")
async def root():
    return {"message": "Kuku Coach API"}

@app.post("/api/sessions", response_model=CreateSessionResponse)
async def create_session():
    session_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    try:
        # Initialize Conversation class
        # This might require config.py to be set up correctly
        # For now, we assume it works or will be handled if errors arise
        conversation_instance = Conversation(user_id=session_id) # Pass session_id as user_id or a more general identifier
        sessions[session_id] = conversation_instance
    except Exception as e:
        # Log the exception e for debugging
        logging.error(f"Error creating session: {e}", exc_info=True)
        # Directly return JSONResponse for this specific failure, matching generic handler's intent
        return JSONResponse(status_code=500, content={"success": False, "error": "Could not initialize session."})

    return CreateSessionResponse(
        data=SessionData(
            sessionId=session_id,
            createdAt=created_at,
            status="active"
        )
    )

@app.post("/api/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(session_id: str, audio: UploadFile = File(...)):
    conversation_instance = sessions.get(session_id)
    if not conversation_instance:
        return JSONResponse(status_code=404, content={"success": False, "error": "Session not found"})

    # Ensure session is not already ended (idempotency for send_message might be complex)
    if conversation_instance.is_ended():
        return JSONResponse(status_code=400, content={"success": False, "error": "Session already ended"})

    temp_audio_path = None
    try:
        # Consider using a truly temporary directory from config.TEMP_DIR
        temp_audio_filename = f"{uuid.uuid4()}_{audio.filename if audio.filename else 'audio.dat'}"
        # temp_audio_path = os.path.join(config.TEMP_DIR, temp_audio_filename) 
        # Fallback if config not fully integrated yet for TEMP_DIR
        temp_dir_for_audio = os.path.join(os.getcwd(), "temp_audio")
        os.makedirs(temp_dir_for_audio, exist_ok=True)
        temp_audio_path = os.path.join(temp_dir_for_audio, temp_audio_filename)


        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # 2. Transcribe audio (using imported function)
        user_transcription = transcribe_audio(temp_audio_path) # This is now synchronous
        if user_transcription is None:
            logging.error(f"Audio transcription failed for session {session_id}, file {temp_audio_path}")
            return JSONResponse(status_code=500, content={"success": False, "error": "Audio transcription failed."})

        # Create user message object
        user_message = Message(
            id=f"msg-user-{uuid.uuid4()}",
            timestamp=datetime.utcnow(),
            sender="user",
            text=user_transcription
        )

        # 3. Conversation Logic: Add user message and get AI response
        # Assuming conversation_instance.add_user_message_to_memory(text) exists or can be adapted
        # For now, let's assume the Conversation class handles history internally when processing input
        # conversation_instance.add_user_message_to_memory(user_transcription) # Or similar method

        # This method should take the user's text, process it, and return the AI's text response.
        # Assuming Conversation.process_input is synchronous based on prior refactoring
        ai_response_text = conversation_instance.process_input(user_transcription)

        if not ai_response_text:
            logging.error(f"AI did not return a response for session {session_id}")
            return JSONResponse(status_code=500, content={"success": False, "error": "AI did not return a response."})

        # 4. AI Audio Response (using imported and renamed function)
        ai_audio_url = None
        # Construct full path for saving TTS audio
        tts_output_filename = f"{uuid.uuid4()}.mp3"
        tts_output_full_path = os.path.join(STATIC_AUDIO_DIR, tts_output_filename)
        
        saved_tts_path = text_to_speech_save_file(text=ai_response_text, output_file_path=tts_output_full_path)
        
        if saved_tts_path:
            ai_audio_url = f"/audio/{tts_output_filename}" # Construct URL relative to STATIC_AUDIO_DIR mount
        else:
            logging.warning(f"AI text-to-speech failed for session {session_id}. Proceeding without audio URL.")

        # Create AI message object
        ai_message = Message(
            id=f"msg-ai-{uuid.uuid4()}",
            timestamp=datetime.utcnow(),
            sender="ai",
            text=ai_response_text,
            audioUrl=ai_audio_url # This will be None if TTS failed
        )

        return SendMessageResponse(
            data=SendMessageData(messages=[user_message, ai_message])
        )

    except HTTPException: # Re-raise HTTPExceptions to let FastAPI handle them
        raise
    except Exception as e:
        # Log the exception e for debugging
        logging.error(f"Error processing message for session {session_id}: {e}", exc_info=True)
        # This will be caught by the generic_exception_handler
        raise # Re-raise
        # return JSONResponse(status_code=500, content={"success": False, "error": "Failed to process message."})
    finally:
        # Clean up temporary uploaded audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except Exception as e:
                logging.error(f"Error deleting temporary audio file {temp_audio_path}: {e}", exc_info=True)

@app.get("/api/sessions/{session_id}/messages", response_model=ConversationHistoryResponse)
async def get_conversation_history_endpoint(session_id: str):
    conversation_instance = sessions.get(session_id)
    if not conversation_instance:
        return JSONResponse(status_code=404, content={"success": False, "error": "Session not found"})

    try:
        langchain_messages = conversation_instance.get_conversation_history()
        
        formatted_messages: list[Message] = []
        for i, lc_message in enumerate(langchain_messages):
            sender_type = "user" if lc_message.type == "human" else "ai"
            
            # Ensure content is a string. If it's not, attempt conversion or use a placeholder.
            text_content = ""
            if hasattr(lc_message, 'content') and isinstance(lc_message.content, str):
                text_content = lc_message.content
            elif hasattr(lc_message, 'content'):
                 # Attempt to convert to string if not already a string (e.g. if it's a complex object)
                try:
                    text_content = str(lc_message.content)
                except:
                    text_content = "[Unsupported message content type]" # Placeholder for unsupported content
            else:
                text_content = "[Message content not available]" # Placeholder if content attribute is missing


            formatted_messages.append(
                Message(
                    id=f"msg-{i}", # Placeholder ID
                    timestamp=datetime.utcnow(), # Placeholder timestamp
                    sender=sender_type,
                    text=text_content,
                    audioUrl=None # Placeholder audioUrl
                )
            )
        
        return ConversationHistoryResponse(
            data=ConversationHistoryData(messages=formatted_messages)
        )
    except Exception as e:
        # Log the exception e for debugging
        logging.error(f"Error retrieving conversation history for session {session_id}: {e}", exc_info=True)
        # This will be caught by the generic_exception_handler
        raise # Re-raise
        # return JSONResponse(status_code=500, content={"success": False, "error": "Could not retrieve conversation history."})

@app.get("/api/sessions/{session_id}", response_model=GetSessionResponse)
async def get_session(session_id: str):
    # Add basic validation for session_id format (e.g., if it's expected to be UUID)
    # try:
    #     uuid.UUID(session_id)
    # except ValueError:
    #     return JSONResponse(status_code=400, content={"success": False, "error": "Invalid session ID format"})

    conversation_instance = sessions.get(session_id)
    if not conversation_instance:
        return JSONResponse(status_code=404, content={"success": False, "error": "Session not found"})

    # Access history via the get_conversation_history() method
    message_count = len(conversation_instance.get_conversation_history())
    
    # For updatedAt, using current time as a placeholder
    updated_at = datetime.utcnow()

    return GetSessionResponse(
        data=GetSessionData(
            sessionId=session_id,
            createdAt=conversation_instance.start_time, # Assuming Conversation object has a start_time attribute
            status="active", # Assuming active until explicitly ended
            updatedAt=updated_at,
            messageCount=message_count
        )
    )

@app.post("/api/sessions/{session_id}/end", response_model=EndSessionResponse)
async def end_session(session_id: str):
    conversation_instance = sessions.get(session_id)
    if not conversation_instance:
        return JSONResponse(status_code=404, content={"success": False, "error": "Session not found"})

    if conversation_instance.is_ended():
        return JSONResponse(status_code=400, content={"success": False, "error": "Session already ended"})

    try:
        # Assuming generate_closing_summary is synchronous after refactoring
        summary = conversation_instance.generate_closing_summary() 
    except Exception as e:
        logging.error(f"Error generating summary for session {session_id}: {e}", exc_info=True)
        # This will be caught by the generic_exception_handler
        raise # Re-raise
        # return JSONResponse(status_code=500, content={"success": False, "error": "Could not generate session summary."})

    duration = int((datetime.utcnow() - conversation_instance.start_time).total_seconds())
    message_count = len(conversation_instance.get_conversation_history())

    # Mark as ended (or remove, depending on desired behavior for subsequent calls)
    # For now, let's assume we mark it as ended and then remove.
    # If the Conversation class has an end_session or similar method, call it.
    # conversation_instance.end_session() 

    # Remove session from memory
    del sessions[session_id]

    return EndSessionResponse(
        data=EndSessionData(
            sessionId=session_id,
            summary=summary,
            duration=duration,
            messageCount=message_count
        )
    )
