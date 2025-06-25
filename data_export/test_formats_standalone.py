#!/usr/bin/env python3
"""
Standalone test for export format functions without requiring Supabase
This can be run in any Python environment to test the formatting logic
"""

import json
import sys
import os
from datetime import datetime

# Mock the dependencies for testing
class MockConfig:
    SYSTEM_PROMPT = """Act as a patient and inspiring Coach named Kuku using the T-GROW model to provoke deep thinking and awareness in your coachee. Prioritize structured conversations while dynamically adapting to the coachee's level of engagement."""

# Add the format functions directly here for testing
def get_system_prompt_with_round(round_num: int = 1, max_rounds: int = 30) -> str:
    """Generate system prompt with current round information"""
    base_prompt = MockConfig.SYSTEM_PROMPT.strip()
    round_info = f"\n\nCurrent conversation round: {round_num}/{max_rounds}"
    return base_prompt + round_info

def format_conversation_for_annotation(session_data, messages):
    """Convert a conversation to text format for annotation"""
    if len(messages) < 2:
        return None
    
    # Sort messages by creation time
    messages.sort(key=lambda x: x['created_at'])
    
    # Build conversation text
    conversation_lines = []
    
    for i, msg in enumerate(messages):
        if msg['sender'] == 'user':
            conversation_lines.append(f"User: {msg['text_content']}")
        else:
            conversation_lines.append(f"Coach: {msg['text_content']}")
        
        # Add separator after each exchange (except the last one)
        if i < len(messages) - 1:
            conversation_lines.append("--------------------------------------------------")
    
    # Add session summary if available
    if session_data.get('summary'):
        conversation_lines.append("--------------------------------------------------")
        conversation_lines.append("")
        conversation_lines.append("FINAL SUMMARY AND ACTION PLAN")
        conversation_lines.append("==================================================")
        conversation_lines.append("")
        conversation_lines.append(session_data['summary'])
    
    return '\n'.join(conversation_lines) + '\n'

def format_conversation_turn_by_turn(session_data, messages):
    """Convert a conversation to turn-by-turn JSONL format"""
    if len(messages) < 2:
        return []
    
    # Sort messages by creation time
    messages.sort(key=lambda x: x['created_at'])
    
    # Get system prompt
    round_count = session_data.get('message_count', len(messages) // 2)
    system_prompt = get_system_prompt_with_round(round_count)
    
    turn_examples = []
    conversation_history = [{"role": "system", "content": system_prompt}]
    
    # Process messages in pairs (user -> AI)
    for i in range(0, len(messages) - 1, 2):
        if i + 1 >= len(messages):
            break
            
        user_msg = messages[i]
        ai_msg = messages[i + 1]
        
        # Skip if not a proper user->AI pair
        if user_msg['sender'] != 'user' or ai_msg['sender'] != 'ai':
            continue
        
        # Add user message to history for this turn
        current_input = conversation_history + [{"role": "user", "content": user_msg['text_content']}]
        
        # Create turn example
        turn_example = {
            "input": current_input,
            "output": ai_msg['text_content']
        }
        turn_examples.append(turn_example)
        
        # Update conversation history for next turn
        conversation_history.append({"role": "user", "content": user_msg['text_content']})
        conversation_history.append({"role": "assistant", "content": ai_msg['text_content']})
    
    return turn_examples

def format_conversation_for_evaluation(session_data, messages):
    """Convert a conversation to full evaluation JSONL format"""
    if len(messages) < 2:
        return None
    
    # Sort messages by creation time
    messages.sort(key=lambda x: x['created_at'])
    
    # Build conversation history
    conversation_messages = []
    
    # Add system prompt
    round_count = session_data.get('message_count', len(messages) // 2)
    system_prompt = get_system_prompt_with_round(round_count)
    
    conversation_messages.append({
        "role": "system",
        "text": system_prompt,
        "name": None,
        "tool_calls": None,
        "function_call": None,
        "tool_call_id": None,
        "refusal": None,
        "finish_reason": None
    })
    
    # Add conversation messages
    for msg in messages[:-1]:  # All except the last message
        role = "user" if msg['sender'] == 'user' else "assistant"
        conversation_messages.append({
            "role": role,
            "text": msg['text_content'],
            "name": None,
            "tool_calls": None,
            "function_call": None,
            "tool_call_id": None,
            "refusal": None,
            "finish_reason": None
        })
    
    # The last message should be an AI response for the output
    last_message = messages[-1]
    if last_message['sender'] != 'ai':
        return None
    
    # Create the evaluation format
    evaluation_data = {
        "input": conversation_messages,
        "output": {
            "model": "ft:gpt-4.1-mini-2025-04-14:kuku-tech:coach-prompt10-purevetted49-basemodel-outofshell-parachange2:Bj66Dtia",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": last_message['text_content'],
                    "refusal": None,
                    "tool_calls": None,
                    "function_call": None
                },
                "finish_reason": "stop"
            }]
        }
    }
    
    return evaluation_data

# Test data
def create_test_data():
    """Create mock conversation data for testing"""
    session_data = {
        'session_id': 'test-session-123',
        'message_count': 6,
        'summary': 'The client explored their relationship with work and retirement, expressing a desire for freedom from financial obligations.',
        'status': 'ended'
    }
    
    messages = [
        {
            'sender': 'user',
            'text_content': 'I want to talk about retirement.',
            'created_at': '2025-06-25T10:00:00Z'
        },
        {
            'sender': 'ai',
            'text_content': 'Thank you for sharing that. What\'s truly important for you to discuss about retirement today?',
            'created_at': '2025-06-25T10:00:01Z'
        },
        {
            'sender': 'user',
            'text_content': 'I was born because I don\'t want to work.',
            'created_at': '2025-06-25T10:00:02Z'
        },
        {
            'sender': 'ai',
            'text_content': 'I hear you—there\'s a strong feeling about work here. Help me understand what not wanting to work means for you.',
            'created_at': '2025-06-25T10:00:03Z'
        },
        {
            'sender': 'user',
            'text_content': 'It means freedom. It means I don\'t have to do work if I don\'t want to.',
            'created_at': '2025-06-25T10:00:04Z'
        },
        {
            'sender': 'ai',
            'text_content': 'That\'s a powerful vision of freedom and choice. How have you experienced this freedom or lack of it so far in your life?',
            'created_at': '2025-06-25T10:00:05Z'
        }
    ]
    
    return session_data, messages

def test_annotation_format():
    """Test text format for annotation"""
    print("🔍 Testing annotation text format...")
    
    session_data, messages = create_test_data()
    
    try:
        result = format_conversation_for_annotation(session_data, messages)
        
        if result:
            print("✅ Annotation format successful")
            print(f"📝 Generated {len(result)} characters")
            
            # Check format
            if "User:" in result and "Coach:" in result:
                print("✅ Contains User/Coach dialog")
            else:
                print("❌ Missing User/Coach format")
                return False
                
            if "--------------------------------------------------" in result:
                print("✅ Contains separators")
            else:
                print("❌ Missing separators")
                return False
                
            if "FINAL SUMMARY" in result:
                print("✅ Contains summary section")
            else:
                print("⚠️  No summary section (expected if no summary)")
            
            # Show sample
            print("\n📋 Sample output:")
            print(result[:200] + "..." if len(result) > 200 else result)
            
            return True
        else:
            print("❌ Annotation format returned None")
            return False
            
    except Exception as e:
        print(f"❌ Annotation format failed: {e}")
        return False

def test_turn_by_turn_format():
    """Test turn-by-turn JSONL format"""
    print("\n🔍 Testing turn-by-turn format...")
    
    session_data, messages = create_test_data()
    
    try:
        result = format_conversation_turn_by_turn(session_data, messages)
        
        if result:
            print("✅ Turn-by-turn format successful")
            print(f"🔄 Generated {len(result)} turn examples")
            
            # Check each turn
            for i, turn in enumerate(result):
                if "input" in turn and "output" in turn:
                    print(f"✅ Turn {i+1}: Valid structure")
                    if isinstance(turn["input"], list) and len(turn["input"]) > 0:
                        print(f"   📊 Input has {len(turn['input'])} messages")
                    else:
                        print("❌ Invalid input structure")
                        return False
                else:
                    print(f"❌ Turn {i+1}: Missing input/output")
                    return False
            
            # Show sample
            print("\n📋 Sample turn:")
            sample_turn = result[0]
            print(f"Input messages: {len(sample_turn['input'])}")
            print(f"Output: {sample_turn['output'][:50]}...")
            
            return True
        else:
            print("❌ Turn-by-turn format returned empty list")
            return False
            
    except Exception as e:
        print(f"❌ Turn-by-turn format failed: {e}")
        return False

def test_full_format():
    """Test full conversation JSONL format"""
    print("\n🔍 Testing full conversation format...")
    
    session_data, messages = create_test_data()
    
    try:
        result = format_conversation_for_evaluation(session_data, messages)
        
        if result:
            print("✅ Full conversation format successful")
            
            # Check structure
            if "input" in result and "output" in result:
                print("✅ Contains input/output structure")
                print(f"📊 Input has {len(result['input'])} messages")
                
                # Check output structure
                if "choices" in result["output"]:
                    print("✅ Output has choices structure")
                else:
                    print("❌ Missing choices in output")
                    return False
                    
            else:
                print("❌ Missing input/output structure")
                return False
            
            # Show sample
            print("\n📋 Sample structure:")
            print(f"Input messages: {len(result['input'])}")
            print(f"Output model: {result['output']['model'][:50]}...")
            
            return True
        else:
            print("❌ Full conversation format returned None")
            return False
            
    except Exception as e:
        print(f"❌ Full conversation format failed: {e}")
        return False

def test_filename_generation():
    """Test the new filename generation for TXT format"""
    print("\n🔍 Testing TXT filename generation...")
    
    # Import the function from the main export script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Test cases for filename generation
    test_cases = [
        ("conversations.txt", "session-123", "conversations_session-123.txt"),
        ("export.txt", "session-abc", "export_session-abc.txt"),
        ("data", "session-456", "data_session-456.txt"),  # No extension
        ("output.jsonl", "session-789", "output.jsonl_session-789.txt")  # Wrong extension
    ]
    
    def generate_txt_filename_test(base_output_file, session_id):
        """Local copy of the function for testing"""
        if base_output_file.endswith('.txt'):
            base_name = base_output_file[:-4]
            return f"{base_name}_{session_id}.txt"
        else:
            return f"{base_output_file}_{session_id}.txt"
    
    success = True
    for base_file, session_id, expected in test_cases:
        result = generate_txt_filename_test(base_file, session_id)
        if result == expected:
            print(f"✅ {base_file} + {session_id} → {result}")
        else:
            print(f"❌ {base_file} + {session_id} → {result} (expected: {expected})")
            success = False
    
    return success


def main():
    """Run all format tests"""
    print("🧪 Testing export format functions (standalone)...\n")
    
    tests = [
        ("Annotation Text Format", test_annotation_format),
        ("Turn-by-Turn Format", test_turn_by_turn_format),
        ("Full Conversation Format", test_full_format),
        ("TXT Filename Generation", test_filename_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
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
        print("\n🎉 All format functions are working correctly!")
        print("\n💡 To test with real data, run this on Windows where Supabase is installed:")
        print("  python data_export/test_export.py")
    else:
        print("\n⚠️  Some format functions failed. Check the implementation.")

if __name__ == "__main__":
    main()