#!/usr/bin/env python3
"""
Test script for Supabase database integration
Run this after setting up your environment variables
"""
import os
import sys
from datetime import datetime

def test_database_connection():
    """Test basic database connection and operations"""
    print("🧪 Testing Supabase Database Integration...")
    
    # Check environment variables
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing environment variables!")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file")
        return False
    
    print(f"✅ Environment variables found")
    print(f"   SUPABASE_URL: {url[:30]}...")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {key[:20]}...")
    
    try:
        # Import and test database service
        from database_service import db_service
        print("✅ Database service imported successfully")
        
        # Test 1: Create a test session
        test_session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"🧪 Creating test session: {test_session_id}")
        
        session = db_service.create_session(test_session_id, user_id=None)
        print(f"✅ Session created: {session['id']}")
        
        # Test 2: Save test messages
        print("🧪 Saving test messages...")
        
        # Use unique message IDs to avoid duplicate key constraints
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        user_msg_id = f"msg-user-{timestamp}"
        ai_msg_id = f"msg-ai-{timestamp}"
        
        user_msg = db_service.save_message(test_session_id, user_msg_id, "user", "Hello, this is a test message!")
        print(f"✅ User message saved: {user_msg['id']}")
        
        ai_msg = db_service.save_message(test_session_id, ai_msg_id, "ai", "Hello! I'm here to help you. This is a test response.")
        print(f"✅ AI message saved: {ai_msg['id']}")
        
        # Test 3: Retrieve conversation history
        print("🧪 Retrieving conversation history...")
        
        history = db_service.get_conversation_history(test_session_id)
        print(f"✅ Retrieved {len(history)} messages")
        
        for msg in history:
            print(f"   {msg['sender']}: {msg['text_content'][:50]}...")
        
        # Test 4: End session with summary
        print("🧪 Ending session with summary...")
        
        ended_session = db_service.end_session(
            test_session_id, 
            summary="This was a successful test of the database integration.", 
            duration=120,  # 2 minutes
            rating=5,
            feedback="Great test!"
        )
        print(f"✅ Session ended: {ended_session['status']}")
        
        # Test 5: Search messages (global search)
        print("🧪 Testing global message search...")
        
        search_results = db_service.search_messages_global("test", user_id=None)
        print(f"✅ Found {len(search_results)} messages containing 'test'")
        
        print("\n🎉 All database tests passed!")
        print("\n📋 Test Summary:")
        print(f"   ✅ Database connection: OK")
        print(f"   ✅ Session creation: OK")
        print(f"   ✅ Message saving: OK")
        print(f"   ✅ History retrieval: OK")
        print(f"   ✅ Session ending: OK")
        print(f"   ✅ Message search: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import database service: {e}")
        print("Make sure you have installed supabase: pip install supabase")
        return False
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Kuku Coach - Database Integration Test")
    print("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment file loaded")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment variables")
    
    success = test_database_connection()
    
    if success:
        print("\n🚀 Database integration is ready for use!")
        print("You can now run your FastAPI server with database support.")
    else:
        print("\n💡 Next steps to fix issues:")
        print("1. Check your .env file has the correct Supabase credentials")
        print("2. Verify your Supabase database schema is set up")
        print("3. Make sure you can access your Supabase project")
        
    sys.exit(0 if success else 1) 