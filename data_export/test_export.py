#!/usr/bin/env python3
"""
Test script for the conversation export functionality
"""

import os
import json
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export_conversations import (
    export_conversations, 
    format_conversation_for_evaluation,
    format_conversation_for_annotation,
    format_conversation_turn_by_turn
)
from database_service import db_service


def test_database_connection():
    """Test if we can connect to Supabase and get sessions"""
    print("🔍 Testing database connection...")
    
    try:
        sessions = db_service.debug_get_all_sessions()
        print(f"✅ Successfully connected! Found {len(sessions)} sessions")
        
        if sessions:
            print("\n📋 Sample sessions:")
            for i, session in enumerate(sessions[:3]):  # Show first 3
                print(f"  {i+1}. {session['session_id']} - {session['status']} - {session.get('message_count', 0)} messages")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_message_retrieval():
    """Test retrieving messages for a session"""
    print("\n🔍 Testing message retrieval...")
    
    try:
        sessions = db_service.debug_get_all_sessions()
        
        if not sessions:
            print("❌ No sessions available for testing")
            return False
        
        # Find a session with messages
        test_session = None
        for session in sessions:
            if session.get('message_count', 0) > 0:
                test_session = session
                break
        
        if not test_session:
            print("❌ No sessions with messages found")
            return False
        
        session_id = test_session['session_id']
        messages = db_service.get_conversation_history(session_id)
        
        print(f"✅ Retrieved {len(messages)} messages for session {session_id}")
        
        if messages:
            print("\n📝 Sample messages:")
            for i, msg in enumerate(messages[:3]):  # Show first 3
                print(f"  {i+1}. {msg['sender']}: {msg['text_content'][:50]}...")
        
        return True, test_session, messages
    except Exception as e:
        print(f"❌ Message retrieval failed: {e}")
        return False, None, None


def test_format_conversion():
    """Test converting conversation to all supported formats"""
    print("\n🔍 Testing format conversion...")
    
    success, session, messages = test_message_retrieval()
    if not success:
        return False
    
    try:
        # Test full conversation format (existing)
        evaluation_data = format_conversation_for_evaluation(session, messages)
        if evaluation_data:
            print("✅ Full conversation format successful")
            print(f"📊 Input messages: {len(evaluation_data['input'])}")
        else:
            print("❌ Full conversation format failed")
            return False
        
        # Test annotation text format
        annotation_text = format_conversation_for_annotation(session, messages)
        if annotation_text:
            print("✅ Annotation text format successful")
            print(f"📝 Text length: {len(annotation_text)} characters")
        else:
            print("❌ Annotation text format failed")
            return False
        
        # Test turn-by-turn format
        turn_examples = format_conversation_turn_by_turn(session, messages)
        if turn_examples:
            print("✅ Turn-by-turn format successful")
            print(f"🔄 Generated {len(turn_examples)} turn examples")
        else:
            print("❌ Turn-by-turn format failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Format conversion failed: {e}")
        return False


def test_export_functionality():
    """Test the full export functionality for all formats"""
    print("\n🔍 Testing export functionality...")
    
    test_files = [
        ("test_full.jsonl", "full"),
        ("test_turns.jsonl", "turn-by-turn"), 
        ("test_annotation.txt", "txt")
    ]
    
    success_count = 0
    
    for test_file, format_type in test_files:
        try:
            print(f"\n📋 Testing {format_type} format...")
            
            # Export recent conversations
            export_conversations(
                output_file=test_file,
                format_type=format_type,
                recent=30,  # Last 30 days
                min_messages=1  # Allow shorter conversations for testing
            )
            
            # Check if file was created and has content
            if os.path.exists(test_file):
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"✅ {format_type} export successful! Created {test_file}")
                
                if content:
                    if format_type in ["full", "turn-by-turn"]:
                        # Validate JSON format
                        lines = content.strip().split('\n')
                        try:
                            sample_data = json.loads(lines[0])
                            print(f"✅ JSON format is valid ({len(lines)} examples)")
                            if format_type == "turn-by-turn":
                                print(f"📊 Turn example: input={len(sample_data.get('input', []))} messages")
                            else:
                                print(f"📊 Full example: input={len(sample_data.get('input', []))} messages")
                        except json.JSONDecodeError as e:
                            print(f"❌ Invalid JSON format: {e}")
                            continue
                    else:  # txt format
                        print(f"✅ Text format valid ({len(content)} characters)")
                        if "User:" in content and "Coach:" in content:
                            print("✅ Contains expected User/Coach dialog")
                        else:
                            print("❌ Missing expected dialog format")
                            continue
                
                # Clean up test file
                os.remove(test_file)
                success_count += 1
            else:
                print(f"❌ Export file {test_file} was not created")
                
        except Exception as e:
            print(f"❌ {format_type} export test failed: {e}")
    
    return success_count == len(test_files)


def main():
    """Run all tests"""
    print("🧪 Starting export functionality tests...\n")
    
    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("❌ Missing required environment variables:")
        print("   SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Message Retrieval", test_message_retrieval),
        ("Format Conversion", test_format_conversion), 
        ("Export Functionality", test_export_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            # Handle functions that return tuples
            if isinstance(result, tuple):
                result = result[0]
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The export script is ready to use.")
        print("\n💡 Usage examples:")
        print("  # Full conversation format")
        print("  python export_conversations.py output.jsonl --format full")
        print("  # Turn-by-turn for OpenAI evaluation")  
        print("  python export_conversations.py turns.jsonl --format turn-by-turn")
        print("  # Text format for annotation")
        print("  python export_conversations.py conversations.txt --format txt")
        print("  # With filters")
        print("  python export_conversations.py output.jsonl --recent 7 --min-rating 4")
    else:
        print("\n⚠️  Some tests failed. Please check the database connection and configuration.")


if __name__ == "__main__":
    main()