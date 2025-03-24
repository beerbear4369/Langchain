"""
Test script that uses real conversation data from log files to test the conversation module.
This script closely mimics the behavior of main.py but uses pre-recorded conversations.
"""

import time
import re
from conversation import Conversation, safe_print

def parse_conversation_log(log_file_path):
    """
    Parse a conversation log file into a list of user and coach messages.
    
    Args:
        log_file_path (str): Path to the conversation log file.
        
    Returns:
        list: List of tuples (role, message) where role is 'User' or 'Coach'.
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split by the separator line
        sections = content.split('--------------------------------------------------')
        
        messages = []
        for section in sections:
            if not section.strip():
                continue
                
            # Extract user and coach messages
            user_match = re.search(r'User:\s*(.*?)(?=\nCoach:|$)', section, re.DOTALL)
            coach_match = re.search(r'Coach:\s*(.*?)(?=\nUser:|$)', section, re.DOTALL)
            
            if user_match:
                user_message = user_match.group(1).strip()
                if user_message:
                    messages.append(('User', user_message))
            
            if coach_match:
                coach_message = coach_match.group(1).strip()
                if coach_message:
                    messages.append(('Coach', coach_message))
        
        return messages
        
    except Exception as e:
        safe_print(f"Error parsing conversation log: {e}")
        return []

def display_conversation_history(conversation):
    """
    Display the conversation history in a readable format.
    
    Args:
        conversation: The Conversation object with chat history
    """
    messages = conversation.get_conversation_history()
    
    print("\n" + "="*50)
    print("CONVERSATION HISTORY")
    print("="*50)
    
    for i, message in enumerate(messages):
        role = "User" if message.type == "human" else "Coach"
        print(f"{role}: {message.content}")
    
    print("="*50 + "\n")

def test_with_real_conversation(log_file_path):
    """
    Test the conversation module with real conversation data from a log file.
    
    Args:
        log_file_path (str): Path to the conversation log file.
    """
    print(f"Testing conversation module with log file: {log_file_path}")
    
    # Parse the conversation log
    messages = parse_conversation_log(log_file_path)
    if not messages:
        print("No messages found in the log file. Exiting.")
        return
    
    print(f"Found {len(messages)} messages in the log file.")
    
    # Create a conversation instance
    conversation = Conversation()
    
    # Record session start time and initialize a turn counter
    session_start = time.time()
    turn_counter = 0
    max_turns = 25  # After 25 exchanges, propose wrapping up
    wrap_up_attempted = False
    
    # Process each message in the log file
    user_messages = [msg for role, msg in messages if role == 'User']
    
    # Mimic main.py logic but with pre-recorded user messages
    for i, user_message in enumerate(user_messages):
        print(f"\nProcessing user message {i+1}/{len(user_messages)}: {user_message[:50]}..." if len(user_message) > 50 else f"\nProcessing user message {i+1}/{len(user_messages)}: {user_message}")
        
        # Add the user's message to conversation history
        conversation.add_user_message_to_memory(user_message)
        
        # Check if the conversation should be wrapped up BEFORE processing
        elapsed_time = time.time() - session_start
        wrap_up_requested = False
        
        # Check wrap-up conditions
        if (turn_counter >= max_turns or conversation.should_wrap_up() or elapsed_time >= 30*60) and not wrap_up_attempted:
            wrap_up_attempted = True
            
            # Choose the appropriate wrap-up prompt
            if conversation.should_wrap_up():
                # Content-based wrap-up (detected Way Forward content)
                wrap_prompt = "It looks like we've made good progress on your issue. Shall we wrap up today's session with a quick summary and an action plan? If yes, please say wrap up and summarize."
            else:
                # Time or message count based wrap-up
                wrap_prompt = "I think we have covered a lot today and it is about the end of our session today. Would you like to wrap up our session with a final summary and action plan? If yes, please say wrap up and summarize."
            
            # Add the wrap-up prompt to conversation history
            conversation.add_ai_message_to_memory(wrap_prompt)
            print(f"\nAssistant: {wrap_prompt}")
            
            # Simulate user confirmation - ALWAYS AGREE TO WRAP UP
            confirmation = "Yes, please wrap up and summarize"
            print(f"User confirmation: {confirmation}")
            
            # Add this confirmation to the conversation history
            conversation.add_user_message_to_memory(confirmation)
            
            # Check for explicit wrap-up commands or affirmative responses
            confirmation_lower = confirmation.lower()
            explicit_commands = ["wrap up and summarize", "wrap up", "summarize", "end session"]
            has_explicit_command = any(cmd in confirmation_lower for cmd in explicit_commands)
            
            affirmative_with_context = (
                ("yes" in confirmation_lower or "yeah" in confirmation_lower or "sure" in confirmation_lower) and
                ("summary" in confirmation_lower or "wrap" in confirmation_lower or "end" in confirmation_lower)
            )
            
            print(f"Has explicit command: {has_explicit_command}")
            print(f"Has affirmative with context: {affirmative_with_context}")
            
            if has_explicit_command or affirmative_with_context:
                # Generate closing summary
                print("\nGenerating closing summary...")
                try:
                    closing_summary = conversation.generate_closing_summary()
                    print("\nCLOSING SUMMARY:")
                    print("="*50)
                    print(closing_summary)
                    print("="*50)
                    
                    # Save to file for inspection
                    with open("test_real_closing_summary.txt", "w", encoding="utf-8") as f:
                        f.write("FINAL SUMMARY AND ACTION PLAN\n")
                        f.write("="*50 + "\n\n")
                        f.write(closing_summary)
                    print("Final summary saved to 'test_real_closing_summary.txt'")
                    
                    # End the session
                    print("\nEnding session.")
                    break
                except Exception as e:
                    print(f"Error generating final summary: {e}")
            else:
                print("\nUser declined to wrap up, continuing conversation.")
        
        # Only process with main LLM if we're not wrapping up
        if not wrap_up_requested:
            try:
                # Process the message without adding it to memory again
                start_time = time.time()
                response = conversation.process_input_with_existing_message(user_message)
                processing_time = time.time() - start_time
                print(f"Processing completed in {processing_time:.2f} seconds")
                
                # Display the response
                short_response = response[:100] + "..." if len(response) > 100 else response
                print(f"Assistant: {short_response}")
                
                # Increment turn counter
                turn_counter += 1
                
                # Debug print of memory state
                summary_info = conversation.get_conversation_summary()
                print(f"Buffer length: {summary_info['buffer_length']}")
                print(f"Summary length: {len(summary_info['summary'])}")
                print(f"Should wrap up: {conversation.should_wrap_up()}, Turn counter: {turn_counter}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
        
        print("-" * 50)
        # Short pause between messages for readability
        time.sleep(0.5)
    
    # If we processed all messages without wrapping up, force a summary at the end
    if not wrap_up_attempted:
        print("\nReached end of conversation without wrap-up. Generating final summary...")
        
        try:
            closing_summary = conversation.generate_closing_summary()
            print("\nCLOSING SUMMARY:")
            print("="*50)
            print(closing_summary)
            print("="*50)
            
            # Save to file for inspection
            with open("test_real_final_summary.txt", "w", encoding="utf-8") as f:
                f.write("FINAL SUMMARY AND ACTION PLAN\n")
                f.write("="*50 + "\n\n")
                f.write(closing_summary)
            print("Final summary saved to 'test_real_final_summary.txt'")
        except Exception as e:
            print(f"Error generating final summary: {e}")
    
    # Display the final conversation history
    display_conversation_history(conversation)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    # Test with the provided conversation log
    test_with_real_conversation("conversation_logs/conversation_20250324_164307.txt") 