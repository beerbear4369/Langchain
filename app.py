from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import os
import tempfile
import json
from datetime import datetime
import asyncio
import threading
import time

# Import existing conversation logic
from conversation import Conversation
from audio_input import transcribe_audio
from audio_output import text_to_speech_api

# Import database service
try:
    from database_service import db_service
    DATABASE_AVAILABLE = True
    print("✅ Database service loaded successfully")
except Exception as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️ Database service not available: {e}")

# Conditional import for audio processing (for deployment compatibility)
try:
    AUDIO_INPUT_AVAILABLE = True
except ImportError:
    AUDIO_INPUT_AVAILABLE = False
    print("Warning: audio_input module not available - audio transcription disabled")

try:
    AUDIO_OUTPUT_AVAILABLE = True
except ImportError:
    AUDIO_OUTPUT_AVAILABLE = False
    print("Warning: audio_output module not available - TTS disabled")

app = FastAPI(
    title="Kuku Coach API",
    description="Voice coaching assistant API for frontend integration",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp_audio directory if it doesn't exist
os.makedirs("temp_audio", exist_ok=True)

# Mount static files for audio serving
app.mount("/audio", StaticFiles(directory="temp_audio"), name="audio")

# In-memory session storage (replace with database in production)
sessions: Dict[str, Dict[str, Any]] = {}
session_conversations: Dict[str, Conversation] = {}

# Data Models matching integration documentation schemas
class ApiResponse(BaseModel):
    success: bool
    error: Optional[str] = None

class SessionData(BaseModel):
    sessionId: str
    createdAt: str
    status: str
    updatedAt: Optional[str] = None
    messageCount: Optional[int] = 0
    wrapUpCooldown: Optional[int] = 0
    timeExtensionMinutes: Optional[int] = 0
    ignoreContentWrapUp: Optional[bool] = False
    awaitingWrapUpConfirmation: Optional[bool] = False
    rating: Optional[int] = None
    feedback: Optional[str] = None

class SessionResponse(ApiResponse):
    data: Optional[SessionData] = None

class Message(BaseModel):
    id: str
    timestamp: str
    sender: str  # "user" or "ai"
    text: str
    audioUrl: Optional[str] = None

class MessageResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None  # Changed to allow sessionEnded and finalSummary fields

class ConversationHistoryResponse(ApiResponse):
    data: Optional[Dict[str, List[Message]]] = None

class SummaryData(BaseModel):
    sessionId: str
    summary: str
    duration: int  # in seconds
    messageCount: int

class SummaryResponse(ApiResponse):
    data: Optional[SummaryData] = None

class RatingData(BaseModel):
    rating: int  # 1-5 scale
    feedback: Optional[str] = None

class RatingResponse(ApiResponse):
    data: Optional[Dict[str, Any]] = None

# Helper functions
def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"session-{uuid.uuid4().hex[:10]}"

def generate_message_id() -> str:
    """Generate a unique message ID."""
    return f"msg-{uuid.uuid4().hex[:8]}"

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"

def create_session_data(session_id: str) -> SessionData:
    """Create session data object."""
    return SessionData(
        sessionId=session_id,
        createdAt=get_current_timestamp(),
        status="active",
        messageCount=0,
        wrapUpCooldown=0,
        timeExtensionMinutes=0,
        ignoreContentWrapUp=False,
        awaitingWrapUpConfirmation=False
    )

def update_session_timestamp(session_id: str):
    """Update session's last activity timestamp."""
    if session_id in sessions:
        sessions[session_id]["updatedAt"] = get_current_timestamp()

def generate_tts_if_available(text: str, audio_path: str) -> bool:
    """Generate TTS if audio output is available, return True if successful."""
    if not AUDIO_OUTPUT_AVAILABLE:
        return False
    try:
        return text_to_speech_api(text, audio_path)
    except Exception as e:
        print(f"TTS generation failed: {e}")
        return False

def save_message_to_database(session_id: str, message_id: str, sender: str, text_content: str):
    """Save a message to the database if available."""
    if DATABASE_AVAILABLE:
        try:
            db_service.save_message(session_id, message_id, sender, text_content)
            print(f"✅ Message {message_id} saved to database")
        except Exception as e:
            print(f"⚠️ Failed to save message to database: {e}")
            # Continue without database - message still processed in memory

def update_message_count(session_id: str, increment: int):
    """Update message count in memory and database."""
    if session_id in sessions:
        new_count = sessions[session_id]["messageCount"] + increment
        sessions[session_id]["messageCount"] = new_count
        update_session_timestamp(session_id)
        if DATABASE_AVAILABLE:
            try:
                db_service.update_session(
                    session_id, 
                    {"message_count": new_count}
                )
                print(f"✅ Updated message_count to {new_count} in database for session {session_id}")
            except Exception as e:
                print(f"⚠️ Failed to update message_count in database for session {session_id}: {e}")

def set_message_count(session_id: str, count: int):
    """Set message count in memory and database."""
    if session_id in sessions:
        sessions[session_id]["messageCount"] = count
        update_session_timestamp(session_id)
        if DATABASE_AVAILABLE:
            try:
                db_service.update_session(
                    session_id, 
                    {"message_count": count}
                )
                print(f"✅ Set message_count to {count} in database for session {session_id}")
            except Exception as e:
                print(f"⚠️ Failed to set message_count in database for session {session_id}: {e}")

# API Endpoints

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new coaching session."""
    try:
        session_id = generate_session_id()
        session_data = create_session_data(session_id)
        
        # Store session data in memory (for immediate access)
        sessions[session_id] = session_data.dict()
        
        # Create conversation instance
        session_conversations[session_id] = Conversation()
        
        # Store in database if available
        if DATABASE_AVAILABLE:
            try:
                db_session = db_service.create_session(session_id, user_id=None)  # user_id None for now (Phase 2)
                print(f"✅ Session {session_id} created in database")
            except Exception as e:
                print(f"⚠️ Failed to create session in database: {e}")
                # Continue without database - in-memory session still works
        
        return SessionResponse(
            success=True,
            data=session_data
        )
    
    except Exception as e:
        return SessionResponse(
            success=False,
            error=f"Failed to create session: {str(e)}"
        )

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session status and details."""
    try:
        if session_id not in sessions:
            return SessionResponse(
                success=False,
                error="Session not found"
            )
        
        session_data = sessions[session_id]
        return SessionResponse(
            success=True,
            data=SessionData(**session_data)
        )
    
    except Exception as e:
        return SessionResponse(
            success=False,
            error=f"Failed to get session: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/end", response_model=SummaryResponse)
async def end_session(session_id: str):
    """End session and generate summary."""
    try:
        if session_id not in sessions:
            return SummaryResponse(
                success=False,
                error="Session not found"
            )
        
        # Get conversation instance
        conversation = session_conversations.get(session_id)
        if not conversation:
            return SummaryResponse(
                success=False,
                error="Conversation not found"
            )
        
        # Generate summary using existing conversation logic (even if already ended)
        summary = conversation.generate_closing_summary()
        
        # Calculate session duration (in seconds)
        created_at = datetime.fromisoformat(sessions[session_id]["createdAt"].replace("Z", "+00:00"))
        duration = int((datetime.utcnow().replace(tzinfo=created_at.tzinfo) - created_at).total_seconds())
        
        # Update session status to ended (if not already ended by automatic wrap-up)
        if sessions[session_id]["status"] != "ended":
            sessions[session_id]["status"] = "ended"
            update_session_timestamp(session_id)
        
        # Save to database if available
        if DATABASE_AVAILABLE:
            try:
                print(f"🔍 DEBUG: About to end session {session_id}")
                print(f"  In-memory session data: {sessions[session_id]}")
                print(f"  messageCount: {sessions[session_id]['messageCount']}")
                
                db_service.end_session(
                    session_id=session_id, 
                    summary=summary, 
                    duration=duration,
                    rating=None,  # Will be set by frontend later
                    feedback=None,  # Will be set by frontend later
                    message_count=sessions[session_id]["messageCount"]
                )
                print(f"✅ Session {session_id} ended and saved to database")
            except Exception as e:
                print(f"⚠️ Failed to save session summary to database: {e}")
                # Continue without database - session still ends successfully
        
        # Clean up conversation instance
        if session_id in session_conversations:
            del session_conversations[session_id]
        
        return SummaryResponse(
            success=True,
            data=SummaryData(
                sessionId=session_id,
                summary=summary,
                duration=duration,
                messageCount=sessions[session_id]["messageCount"]
            )
        )
    
    except Exception as e:
        return SummaryResponse(
            success=False,
            error=f"Failed to end session: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_audio_message(session_id: str, audio: UploadFile = File(...)):
    """Send audio message and get AI response."""
    try:
        if session_id not in sessions:
            return MessageResponse(
                success=False,
                error="Session not found"
            )
        
        if sessions[session_id]["status"] != "active":
            return MessageResponse(
                success=False,
                error="Session is not active"
            )
        
        # Get conversation instance
        conversation = session_conversations.get(session_id)
        if not conversation:
            return MessageResponse(
                success=False,
                error="Conversation not found"
            )
        
        # Validate audio file
        if not audio.content_type or not any(fmt in audio.content_type.lower() 
                                           for fmt in ['audio/', 'video/webm']):
            return MessageResponse(
                success=False,
                error="Invalid audio format. Please use MP3, WAV, or WebM format."
            )
        
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        try:
            # Transcribe audio using existing logic
            user_text = transcribe_audio(temp_audio_path)
            
            if not user_text or not user_text.strip():
                return MessageResponse(
                    success=False,
                    error="Could not transcribe audio. Please try again."
                )
            
            user_text_lower = user_text.lower()
            
            # Prioritize checking for wrap-up confirmation
            is_awaiting_confirmation = sessions[session_id].get("awaitingWrapUpConfirmation", False)
            
            if is_awaiting_confirmation:
                # User is responding to wrap-up confirmation prompt
                confirmation_lower = user_text_lower
                
                # Check for explicit confirmation commands (from main.py logic)
                explicit_commands = ["wrap up and summarize", "wrap up", "summarize", "end session", "yes"]
                has_explicit_command = any(cmd in confirmation_lower for cmd in explicit_commands)
                
                # Check for affirmative responses with context
                affirmative_with_context = (
                    ("yes" in confirmation_lower or "yeah" in confirmation_lower or "sure" in confirmation_lower) and
                    ("summary" in confirmation_lower or "wrap" in confirmation_lower or "end" in confirmation_lower)
                )
                
                if has_explicit_command or affirmative_with_context:
                    # User confirmed wrap-up
                    conversation.add_user_message_to_memory(user_text)
                    
                    try:
                        # Generate final summary using existing conversation logic
                        final_message = conversation.generate_closing_summary()
                        conversation.add_ai_message_to_memory(final_message)
                        
                        # Update session status to ended
                        sessions[session_id]["status"] = "ended"
                        sessions[session_id]["awaitingWrapUpConfirmation"] = False
                        update_session_timestamp(session_id)
                        
                        # Generate TTS for final summary
                        audio_url = None
                        try:
                            audio_filename = f"response-{generate_message_id()}.mp3"
                            audio_path = os.path.join("temp_audio", audio_filename)
                            os.makedirs("temp_audio", exist_ok=True)
                            
                            if text_to_speech_api(final_message, audio_path):
                                if os.path.exists(audio_path):
                                    audio_url = f"/audio/{audio_filename}"
                        except Exception as e:
                            print(f"TTS generation failed for final summary: {e}")
                        
                        # Create message objects
                        user_message = Message(
                            id=generate_message_id(),
                            timestamp=get_current_timestamp(),
                            sender="user",
                            text=user_text
                        )
                        
                        ai_message = Message(
                            id=generate_message_id(),
                            timestamp=get_current_timestamp(),
                            sender="ai",
                            text=final_message,
                            audioUrl=audio_url
                        )
                        
                        # Save messages to database
                        save_message_to_database(session_id, user_message.id, "user", user_text)
                        save_message_to_database(session_id, ai_message.id, "ai", final_message)
                        
                        # Update session message count
                        update_message_count(session_id, 2)
                        
                        # Save session summary to database if available (CRITICAL FIX)
                        if DATABASE_AVAILABLE:
                            try:
                                # Calculate session duration (same logic as manual ending)
                                created_at = datetime.fromisoformat(sessions[session_id]["createdAt"].replace("Z", "+00:00"))
                                duration = int((datetime.utcnow().replace(tzinfo=created_at.tzinfo) - created_at).total_seconds())
                                
                                print(f"🔍 DEBUG: About to auto-end session {session_id}")
                                print(f"  In-memory session data: {sessions[session_id]}")
                                print(f"  messageCount: {sessions[session_id]['messageCount']}")
                                
                                db_service.end_session(
                                    session_id=session_id, 
                                    summary=final_message, 
                                    duration=duration,
                                    rating=None,  # Will be set by frontend later
                                    feedback=None,  # Will be set by frontend later
                                    message_count=sessions[session_id]["messageCount"]
                                )
                                print(f"✅ Session {session_id} automatically ended and saved to database")
                            except Exception as e:
                                print(f"⚠️ Failed to save automatic session ending to database: {e}")
                                # Continue without database - session still ends successfully
                        
                        # Clean up conversation instance (same as manual ending)
                        if session_id in session_conversations:
                            del session_conversations[session_id]
                        
                        # Prepare response data with session ended flag
                        response_data = {
                            "messages": [user_message, ai_message],
                            "sessionEnded": True,
                            "finalSummary": final_message
                        }
                        
                        print(f"Session {session_id} manually ended via user confirmation")
                        
                        return MessageResponse(
                            success=True,
                            data=response_data
                        )
                        
                    except Exception as e:
                        print(f"Error generating final summary: {e}")
                        # Continue with normal conversation if summary generation fails
                        sessions[session_id]["awaitingWrapUpConfirmation"] = False
                        ai_response = "I had trouble creating a final summary. Let's continue our conversation."
                        conversation.add_user_message_to_memory(user_text)
                        conversation.add_ai_message_to_memory(ai_response)
                else:
                    # User declined wrap-up - implement cooldown and extension logic from standalone
                    sessions[session_id]["awaitingWrapUpConfirmation"] = False
                    
                    # Reset wrap-up conditions and add cooldown (from main.py lines 530-543)
                    # 1. Reset turn counter to avoid immediate re-prompting
                    current_message_count = sessions[session_id]["messageCount"]
                    new_count = max(0, current_message_count - 10) # Reduce by 5 exchanges
                    set_message_count(session_id, new_count)
                    
                    # 2. Set cooldown period for 5 conversation exchanges
                    sessions[session_id]["wrapUpCooldown"] = 5
                    
                    # 3. Extend session timeout by 5 minutes
                    sessions[session_id]["timeExtensionMinutes"] += 5
                    
                    # 4. Temporarily ignore should_wrap_up() results
                    sessions[session_id]["ignoreContentWrapUp"] = True
                    
                    ai_response = "Okay, let's continue our conversation."
                    conversation.add_user_message_to_memory(user_text)
                    conversation.add_ai_message_to_memory(ai_response)
                    
                    # Generate TTS for continuation message
                    audio_url = None
                    try:
                        audio_filename = f"response-{generate_message_id()}.mp3"
                        audio_path = os.path.join("temp_audio", audio_filename)
                        os.makedirs("temp_audio", exist_ok=True)
                        
                        if text_to_speech_api(ai_response, audio_path):
                            if os.path.exists(audio_path):
                                audio_url = f"/audio/{audio_filename}"
                    except Exception as e:
                        print(f"TTS generation failed for continuation message: {e}")
                    
                    # Create message objects
                    user_message = Message(
                        id=generate_message_id(),
                        timestamp=get_current_timestamp(),
                        sender="user",
                        text=user_text
                    )
                    
                    ai_message = Message(
                        id=generate_message_id(),
                        timestamp=get_current_timestamp(),
                        sender="ai",
                        text=ai_response,
                        audioUrl=audio_url
                    )
                    
                    # Update session message count
                    update_message_count(session_id, 2)
                    update_session_timestamp(session_id)
                    
                    # Prepare response data
                    response_data = {"messages": [user_message, ai_message]}
                    
                    return MessageResponse(
                        success=True,
                        data=response_data
                    )
            
            # Check for explicit user-initiated wrap-up requests
            wrap_up_commands = ["wrap up", "end session", "finish conversation", "summarize and end", "let's conclude", "finish session"]
            if any(wrap_cmd in user_text_lower for wrap_cmd in wrap_up_commands):
                # User requested wrap-up, provide confirmation prompt
                wrap_prompt = "Would you like to wrap up our session with a final summary and action plan? Please confirm by saying 'yes' or 'wrap up and summarize'."
                
                # Add both user message and wrap-up prompt to conversation memory
                conversation.add_user_message_to_memory(user_text)
                conversation.add_ai_message_to_memory(wrap_prompt)
                
                # Create message objects
                user_message = Message(
                    id=generate_message_id(),
                    timestamp=get_current_timestamp(),
                    sender="user",
                    text=user_text
                )
                
                ai_message = Message(
                    id=generate_message_id(),
                    timestamp=get_current_timestamp(),
                    sender="ai",
                    text=wrap_prompt
                )
                
                # Save messages to database
                save_message_to_database(session_id, user_message.id, "user", user_text)
                save_message_to_database(session_id, ai_message.id, "ai", wrap_prompt)
                
                # Generate TTS for the wrap-up prompt
                audio_url = None
                try:
                    audio_filename = f"response-{generate_message_id()}.mp3"
                    audio_path = os.path.join("temp_audio", audio_filename)
                    os.makedirs("temp_audio", exist_ok=True)
                    
                    if text_to_speech_api(wrap_prompt, audio_path):
                        if os.path.exists(audio_path):
                            audio_url = f"/audio/{audio_filename}"
                except Exception as e:
                    print(f"TTS generation failed for wrap-up prompt: {e}")
                
                ai_message.audioUrl = audio_url
                
                # Update session message count and add flag to indicate awaiting confirmation
                update_message_count(session_id, 2)
                sessions[session_id]["awaitingWrapUpConfirmation"] = True
                
                # Prepare response data with confirmation prompt
                response_data = {
                    "messages": [user_message, ai_message],
                    "awaitingWrapUpConfirmation": True
                }
                
                return MessageResponse(
                    success=True,
                    data=response_data
                )

            # Normal conversation processing (not wrap-up related)
            # Process user input with existing conversation logic
            ai_response = conversation.process_input(user_text)
            
            # COMPREHENSIVE WRAP-UP LOGIC (copied from main.py lines 411-543)
            # Calculate elapsed time and turn counter
            created_at = datetime.fromisoformat(sessions[session_id]["createdAt"].replace("Z", "+00:00"))
            elapsed_time = (datetime.utcnow().replace(tzinfo=created_at.tzinfo) - created_at).total_seconds()
            turn_counter = sessions[session_id]["messageCount"] // 2  # Each exchange = user + AI message
            max_turns = 25  # After 25 exchanges, propose wrapping up
            
            wrap_up_requested = False
            
            # Check if we're in the cooldown period
            if sessions[session_id]["wrapUpCooldown"] > 0:
                # Decrement cooldown
                sessions[session_id]["wrapUpCooldown"] -= 1
                print(f"Wrap-up cooldown active: {sessions[session_id]['wrapUpCooldown']} exchanges remaining")
                
            # Only check wrap-up conditions if not in cooldown
            elif (turn_counter >= max_turns or 
                  (not sessions[session_id]["ignoreContentWrapUp"] and conversation.should_wrap_up()) or 
                  elapsed_time >= (30*60 + sessions[session_id]["timeExtensionMinutes"]*60)):  # 30 min + any extension
                
                # Choose the appropriate wrap-up prompt based on what triggered it
                wrap_prompt = ""
                if not sessions[session_id]["ignoreContentWrapUp"] and conversation.should_wrap_up():
                    # Content-based wrap-up (detected Way Forward content)
                    wrap_prompt = "It looks like we've made good progress on your issue. Shall we wrap up today's session with a quick summary and an action plan? If yes, please say wrap up and summarize."
                elif turn_counter >= max_turns or elapsed_time >= (30*60 + sessions[session_id]["timeExtensionMinutes"]*60):
                    # Time or message count based wrap-up
                    wrap_prompt = "I think we have covered a lot today and it is about the end of our session today. Would you like to wrap up our session with a final summary and action plan? If yes, please say wrap up and summarize."
                
                # Add the wrap-up prompt to conversation history before presenting it
                conversation.add_ai_message_to_memory(wrap_prompt)
                
                # Set awaiting confirmation flag
                sessions[session_id]["awaitingWrapUpConfirmation"] = True
                update_session_timestamp(session_id)
                
                # Generate TTS for wrap-up prompt
                audio_url = None
                try:
                    audio_filename = f"response-{generate_message_id()}.mp3"
                    audio_path = os.path.join("temp_audio", audio_filename)
                    os.makedirs("temp_audio", exist_ok=True)
                    
                    if text_to_speech_api(wrap_prompt, audio_path):
                        if os.path.exists(audio_path):
                            audio_url = f"/audio/{audio_filename}"
                except Exception as e:
                    print(f"TTS generation failed for wrap-up prompt: {e}")
                
                # Create message objects for wrap-up prompt
                user_message = Message(
                    id=generate_message_id(),
                    timestamp=get_current_timestamp(),
                    sender="user",
                    text=user_text
                )
                
                ai_message = Message(
                    id=generate_message_id(),
                    timestamp=get_current_timestamp(),
                    sender="ai",
                    text=wrap_prompt,
                    audioUrl=audio_url
                )
                
                # Update session message count
                update_message_count(session_id, 2)
                update_session_timestamp(session_id)
                
                # Save messages to database
                save_message_to_database(session_id, user_message.id, "user", user_text)
                save_message_to_database(session_id, ai_message.id, "ai", wrap_prompt)
                
                # Prepare response data with awaiting confirmation flag
                response_data = {
                    "messages": [user_message, ai_message],
                    "awaitingWrapUpConfirmation": True
                }
                
                return MessageResponse(
                    success=True,
                    data=response_data
                )
            
            # Generate TTS for AI response
            audio_url = None
            try:
                # Create audio response (this would need to be served as a static file)
                audio_filename = f"response-{generate_message_id()}.mp3"
                audio_path = os.path.join("temp_audio", audio_filename)
                os.makedirs("temp_audio", exist_ok=True)
                
                print(f"Attempting TTS generation for: {ai_response[:50]}...")
                print(f"Audio file path: {audio_path}")
                
                if text_to_speech_api(ai_response, audio_path):
                    print(f"TTS successful, checking if file exists: {os.path.exists(audio_path)}")
                    if os.path.exists(audio_path):
                        audio_url = f"/audio/{audio_filename}"
                        print(f"Audio URL set to: {audio_url}")
                    else:
                        print("TTS generation failed - text_to_speech_api returned False")
                else:
                    print("TTS generation failed - text_to_speech_api returned False")
            except Exception as e:
                print(f"TTS generation failed with exception: {e}")
                import traceback
                traceback.print_exc()
                # Continue without audio - text response is still available
            
            # Create message objects
            user_message = Message(
                id=generate_message_id(),
                timestamp=get_current_timestamp(),
                sender="user",
                text=user_text
            )
            
            ai_message = Message(
                id=generate_message_id(),
                timestamp=get_current_timestamp(),
                sender="ai",
                text=ai_response,
                audioUrl=audio_url
            )
            
            # Update session message count
            update_message_count(session_id, 2)  # User + AI message
            
            # Save messages to database
            save_message_to_database(session_id, user_message.id, "user", user_text)
            save_message_to_database(session_id, ai_message.id, "ai", ai_response)
            
            # Prepare response data
            response_data = {"messages": [user_message, ai_message]}
            
            return MessageResponse(
                success=True,
                data=response_data
            )
        
        finally:
            # Clean up temporary audio file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
    
    except Exception as e:
        return MessageResponse(
            success=False,
            error=f"Failed to process audio: {str(e)}"
        )

@app.get("/api/sessions/{session_id}/messages", response_model=ConversationHistoryResponse)
async def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    try:
        if session_id not in sessions:
            return ConversationHistoryResponse(
                success=False,
                error="Session not found"
            )
        
        # Try to get conversation history from database first
        if DATABASE_AVAILABLE:
            try:
                db_messages = db_service.get_conversation_history(session_id)
                
                # Convert database messages to API format
                messages = []
                for db_msg in db_messages:
                    message = Message(
                        id=db_msg["message_id"],
                        timestamp=db_msg["created_at"],
                        sender=db_msg["sender"],
                        text=db_msg["text_content"]
                    )
                    messages.append(message)
                
                return ConversationHistoryResponse(
                    success=True,
                    data={"messages": messages}
                )
                
            except Exception as e:
                print(f"⚠️ Failed to get conversation history from database: {e}")
                # Fall back to in-memory conversation
        
        # Fallback: Get conversation instance from memory
        conversation = session_conversations.get(session_id)
        if not conversation:
            # Return empty messages for sessions without conversation
            return ConversationHistoryResponse(
                success=True,
                data={"messages": []}
            )
        
        # Clean up duplicates and empty messages before getting history
        conversation._remove_duplicate_messages()
        conversation._clean_empty_messages()
        
        # Get conversation history from existing logic
        history = conversation.get_conversation_history()
        
        # Convert to API message format
        messages = []
        for i, msg in enumerate(history):
            message = Message(
                id=f"msg-{session_id}-{i}",
                timestamp=get_current_timestamp(),  # Would need to store actual timestamps
                sender="user" if msg.type == "human" else "ai",
                text=msg.content
            )
            messages.append(message)
        
        return ConversationHistoryResponse(
            success=True,
            data={"messages": messages}
        )
    
    except Exception as e:
        return ConversationHistoryResponse(
            success=False,
            error=f"Failed to get conversation history: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/rating", response_model=RatingResponse)
async def submit_session_rating(session_id: str, rating_data: RatingData):
    """Submit rating and feedback for a completed session."""
    try:
        # Validate rating range
        if not (1 <= rating_data.rating <= 5):
            return RatingResponse(
                success=False,
                error="Rating must be between 1 and 5"
            )
        
        # Check if session exists and is ended
        if session_id not in sessions:
            return RatingResponse(
                success=False,
                error="Session not found"
            )
        
        if sessions[session_id]["status"] != "ended":
            return RatingResponse(
                success=False,
                error="Can only rate completed sessions"
            )
        
        # Update session with rating in database
        if DATABASE_AVAILABLE:
            try:
                db_service.update_session(
                    session_id, 
                    {
                        "rating": rating_data.rating,
                        "feedback": rating_data.feedback
                    }
                )
                print(f"✅ Rating {rating_data.rating} saved for session {session_id}")
            except Exception as e:
                print(f"⚠️ Failed to save rating to database: {e}")
                return RatingResponse(
                    success=False,
                    error="Failed to save rating"
                )
        
        # Update in-memory session data
        sessions[session_id]["rating"] = rating_data.rating
        sessions[session_id]["feedback"] = rating_data.feedback
        update_session_timestamp(session_id)
        
        return RatingResponse(
            success=True,
            data={
                "sessionId": session_id,
                "rating": rating_data.rating,
                "feedback": rating_data.feedback,
                "timestamp": get_current_timestamp()
            }
        )
    
    except Exception as e:
        return RatingResponse(
            success=False,
            error=f"Failed to submit rating: {str(e)}"
        )

@app.get("/api/sessions/{session_id}/rating", response_model=RatingResponse)
async def get_session_rating(session_id: str):
    """Get existing rating for a session."""
    try:
        if session_id not in sessions:
            return RatingResponse(
                success=False,
                error="Session not found"
            )
        
        # Try to get from database first
        if DATABASE_AVAILABLE:
            try:
                db_session = db_service.get_session(session_id)
                if db_session and (db_session.get("rating") or db_session.get("feedback")):
                    return RatingResponse(
                        success=True,
                        data={
                            "sessionId": session_id,
                            "rating": db_session.get("rating"),
                            "feedback": db_session.get("feedback"),
                            "hasRating": db_session.get("rating") is not None
                        }
                    )
            except Exception as e:
                print(f"⚠️ Failed to get rating from database: {e}")
        
        # Fallback to in-memory data
        session_data = sessions[session_id]
        return RatingResponse(
            success=True,
            data={
                "sessionId": session_id,
                "rating": session_data.get("rating"),
                "feedback": session_data.get("feedback"),
                "hasRating": session_data.get("rating") is not None
            }
        )
    
    except Exception as e:
        return RatingResponse(
            success=False,
            error=f"Failed to get rating: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": get_current_timestamp()}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Kuku Coach API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 