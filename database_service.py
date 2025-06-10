import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from datetime import datetime


class DatabaseService:
    """Database service for Kuku Coach using Supabase following official supabase-py patterns"""
    
    def __init__(self):
        """Initialize Supabase client following official documentation pattern"""
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
        
        self.supabase: Client = create_client(url, key)
    
    def create_session(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session in database following supabase-py insert pattern"""
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "active",
            "message_count": 0,  # Explicitly initialize message count
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Following supabase-py insert pattern from documentation
        result = self.supabase.table("sessions").insert(session_data).execute()
        
        # Check if data was inserted successfully
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            raise Exception("Failed to create session in database")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from database following supabase-py select pattern"""
        # Following supabase-py select + eq pattern from documentation
        result = self.supabase.table("sessions")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        
        # Return first result if exists
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update session in database following supabase-py update pattern"""
        updates["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        print(f"🔍 DEBUG update_session called:")
        print(f"  session_id: {session_id}")
        print(f"  updates: {updates}")
        
        # Following supabase-py update + eq pattern from documentation
        result = self.supabase.table("sessions")\
            .update(updates)\
            .eq("session_id", session_id)\
            .execute()
        
        print(f"🔍 Supabase update result: {result.data}")
        
        # Check if data was updated successfully
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            raise Exception(f"Failed to update session {session_id}")
    
    def end_session(self, session_id: str, summary: str, duration: int, 
                   rating: Optional[int] = None, feedback: Optional[str] = None, message_count: Optional[int] = None) -> Dict[str, Any]:
        """End session and save summary, including message count if provided"""
        print(f"🔍 DEBUG end_session called with:")
        print(f"  session_id: {session_id}")
        print(f"  summary: {summary[:50]}...")
        print(f"  duration: {duration}")
        print(f"  rating: {rating}")
        print(f"  feedback: {feedback}")
        print(f"  message_count: {message_count}")
        
        updates = {
            "status": "ended",
            "ended_at": datetime.utcnow().isoformat() + "Z",
            "summary": summary,
            "duration_seconds": duration,
            "rating": rating,
            "feedback": feedback
        }
        if message_count is not None:
            updates["message_count"] = message_count
            print(f"✅ Added message_count to updates: {message_count}")
        else:
            print(f"⚠️  message_count is None, not adding to updates")
        
        print(f"🔍 Full updates dict: {updates}")
        return self.update_session(session_id, updates)
    
    def save_message(self, session_id: str, message_id: str, sender: str, text_content: str) -> Dict[str, Any]:
        """Save message to database following supabase-py insert pattern"""
        # Get session UUID first
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        message_data = {
            "session_id": session["id"],  # Use UUID from session
            "message_id": message_id,
            "sender": sender,
            "text_content": text_content,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Following supabase-py insert pattern from documentation
        result = self.supabase.table("messages").insert(message_data).execute()
        
        # Check if data was inserted successfully
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            raise Exception("Failed to save message to database")
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session following supabase-py select pattern"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Following supabase-py select + eq + order pattern from documentation
        result = self.supabase.table("messages")\
            .select("*")\
            .eq("session_id", session["id"])\
            .order("created_at")\
            .execute()
        
        return result.data or []
    
    def search_messages_global(self, query: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search messages globally across all sessions for a user using PostgreSQL full-text search"""
        try:
            # Simplified approach: Search messages with text content containing the query
            # Following supabase-py select pattern from documentation
            
            if user_id:
                # When we add auth in Phase 2, we'll join with sessions table to filter by user
                # For now, just search all messages since user_id is None in Phase 1
                result = self.supabase.table("messages")\
                    .select("*, sessions!inner(session_id, user_id, created_at)")\
                    .ilike("text_content", f"%{query}%")\
                    .execute()
            else:
                # Phase 1: Search all messages (no user filtering)
                result = self.supabase.table("messages")\
                    .select("*")\
                    .ilike("text_content", f"%{query}%")\
                    .execute()
            
            return result.data or []
            
        except Exception as e:
            print(f"Search error: {e}")
            # Return empty list if search fails
            return []
    
    def debug_get_all_sessions(self) -> List[Dict[str, Any]]:
        """Debug method to get all sessions and their message counts"""
        try:
            result = self.supabase.table("sessions")\
                .select("session_id, status, message_count, created_at, ended_at, summary")\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data or []
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def debug_update_message_count(self, session_id: str, message_count: int) -> Dict[str, Any]:
        """Debug method to manually update a session's message count"""
        print(f"🔧 DEBUG: Manually updating message_count for {session_id} to {message_count}")
        updates = {"message_count": message_count}
        return self.update_session(session_id, updates)


# Initialize singleton service instance
db_service = DatabaseService() 