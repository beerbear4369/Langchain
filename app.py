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

# Conditional import for audio processing (for deployment compatibility)
try:
    from audio_input import transcribe_audio
    AUDIO_INPUT_AVAILABLE = True
except ImportError:
    AUDIO_INPUT_AVAILABLE = False
    print("Warning: audio_input module not available - audio transcription disabled")

from audio_output import text_to_speech_api

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
        messageCount=0
    )

def update_session_timestamp(session_id: str):
    """Update session's last activity timestamp."""
    if session_id in sessions:
        sessions[session_id]["updatedAt"] = get_current_timestamp()

# API Endpoints

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new coaching session."""
    try:
        session_id = generate_session_id()
        session_data = create_session_data(session_id)
        
        # Store session data
        sessions[session_id] = session_data.dict()
        
        # Create conversation instance
        session_conversations[session_id] = Conversation()
        
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
            if AUDIO_INPUT_AVAILABLE:
                user_text = transcribe_audio(temp_audio_path)
            else:
                return MessageResponse(
                    success=False,
                    error="Audio transcription not available in this deployment. Please use text input instead."
                )
            
            if not user_text or not user_text.strip():
                return MessageResponse(
                    success=False,
                    error="Could not transcribe audio. Please try again."
                )
            
            # Check for explicit user-initiated wrap-up requests (from main.py logic)
            user_text_lower = user_text.lower()
            wrap_up_commands = ["wrap up", "end session", "finish conversation", "summarize and end", "let's conclude", "finish session"]
            
            # Check if user requested wrap-up
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
                sessions[session_id]["messageCount"] += 2
                sessions[session_id]["awaitingWrapUpConfirmation"] = True
                update_session_timestamp(session_id)
                
                # Prepare response data with confirmation prompt
                response_data = {
                    "messages": [user_message, ai_message],
                    "awaitingWrapUpConfirmation": True
                }
                
                return MessageResponse(
                    success=True,
                    data=response_data
                )
            
            # Check if we're awaiting wrap-up confirmation
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
                        
                        # Update session message count
                        sessions[session_id]["messageCount"] += 2
                        
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
                    # User declined wrap-up
                    sessions[session_id]["awaitingWrapUpConfirmation"] = False
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
                    sessions[session_id]["messageCount"] += 2
                    update_session_timestamp(session_id)
                    
                    # Prepare response data
                    response_data = {"messages": [user_message, ai_message]}
                    
                    return MessageResponse(
                        success=True,
                        data=response_data
                    )
            
            # Normal conversation processing (not wrap-up related)
            # Process user input with existing conversation logic
            ai_response = conversation.process_input(user_text)
            
            # Check if session should be automatically wrapped up (identical to standalone version)
            should_end_session = False
            final_summary = None
            
            # Only check for wrap-up after conversation has progressed enough (matching standalone logic)
            if conversation.conversation_rounds >= 15:
                if conversation.should_wrap_up():
                    should_end_session = True
                    # Generate final summary using existing conversation logic
                    try:
                        final_summary = conversation.generate_closing_summary()
                        # Update session status to ended
                        sessions[session_id]["status"] = "ended"
                        update_session_timestamp(session_id)
                        # The conversation instance will be cleaned up by the frontend calling /end endpoint
                    except Exception as e:
                        print(f"Warning: Failed to generate closing summary: {e}")
                        # Still end the session even if summary generation fails
                        should_end_session = True
            
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
                        print("TTS reported success but file does not exist")
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
            sessions[session_id]["messageCount"] += 2  # User + AI message
            update_session_timestamp(session_id)
            
            # Prepare response data
            response_data = {"messages": [user_message, ai_message]}
            
            # Add session ending information if the session should be wrapped up
            if should_end_session:
                response_data["sessionEnded"] = True
                if final_summary:
                    response_data["finalSummary"] = final_summary
                print(f"Session {session_id} automatically ended after {conversation.conversation_rounds} rounds")
            
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
        
        # Get conversation instance
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