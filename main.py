import os
import sys
import json

# Fix import paths for PyInstaller
try:
    # First, try to import our custom fix_imports module
    import fix_imports
    base_dir = fix_imports.setup_import_paths()
    print(f"Import paths fixed. Base directory: {base_dir}")
except ImportError:
    # Fallback to manual path setup if the module isn't found
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable
        if sys._MEIPASS not in sys.path:
            sys.path.insert(0, sys._MEIPASS)
            print(f"Added {sys._MEIPASS} to Python path")
        
        # Set current working directory to PyInstaller directory
        os.chdir(sys._MEIPASS)
        print(f"Changed working directory to {sys._MEIPASS}")

import time
import signal
from functools import wraps
from audio_input import record_audio, transcribe_audio
from conversation import Conversation
from audio_output import text_to_speech
from config import RECORDING_START_MESSAGE, RECORDING_STOP_MESSAGE, RESPONSE_START_MESSAGE
import config

# Timeout decorator for functions that might hang
def timeout(seconds, error_message="Function call timed out"):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the timeout handler - only on platforms that support SIGALRM
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                return result
            else:
                # On platforms without SIGALRM (e.g., Windows), we can't use this timeout mechanism
                # Just call the function directly
                return func(*args, **kwargs)
        return wrapper
    return decorator

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
        role = "You" if message.type == "human" else "Coach"
        print(f"{role}: {message.content}")
    
    print("="*50 + "\n")

def save_conversation_history(conversation):
    """
    Save the conversation history to a text file.
    
    Args:
        conversation: The Conversation object with chat history
    """
    # Clean up any empty messages first
    conversation._clean_empty_messages()
    
    # Get all messages from memory
    messages = conversation.get_conversation_history()
    
    try:
        # First save to the standard conversation_history.txt file
        with open("conversation_history.txt", "w", encoding="utf-8") as f:
            f.write("CONVERSATION HISTORY\n")
            f.write("="*50 + "\n\n")
            
            for message in messages:
                role = "User" if message.type == "human" else "Coach"
                f.write(f"{role}: {message.content}\n\n")
            
            # Ensure file is flushed to disk
            f.flush()
        
        # Also update the conversation log in the logs directory
        session_id = conversation.session_id
        log_file = os.path.join("conversation_logs", f"conversation_{session_id}.txt")
        
        # Force write all conversation content to ensure completeness
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                last_role = None
                current_content = ""
                
                for i, message in enumerate(messages):
                    current_role = "User" if message.type == "human" else "Coach"
                    
                    # If role changes, write the previous content
                    if last_role and last_role != current_role and current_content:
                        f.write(f"{last_role}: {current_content}\n")
                        f.write("-"*50 + "\n")
                        current_content = ""
                    
                    # Set or append to current content
                    if not current_content:
                        current_content = message.content
                    else:
                        current_content += "\n\n" + message.content
                    
                    last_role = current_role
                    
                    # If this is the last message, write it
                    if i == len(messages) - 1 and current_content:
                        f.write(f"{current_role}: {current_content}\n")
                        if i < len(messages) - 1:  # Not the last message
                            f.write("-"*50 + "\n")
                
                # Ensure file is flushed to disk
                f.flush()
                
        except Exception as e:
            print(f"Error writing to conversation log file: {e}")
        
        print("Conversation history saved to 'conversation_history.txt'")
    except Exception as e:
        print(f"Error saving conversation history: {e}")

def debug_conversation_memory(conversation):
    """Print details about the conversation memory for debugging."""
    messages = conversation.get_conversation_history()
    print(f"\nDEBUG: Memory contains {len(messages)} messages")
    
    if messages:
        # Print the first and last message if they exist
        print(f"First message: [{messages[0].type}] {messages[0].content[:50]}...")
        print(f"Last message: [{messages[-1].type}] {messages[-1].content[:50]}...")
        
        # Get the raw prompt that would be sent to OpenAI
        # This helps verify the history is included in prompts
        try:
            test_input = "This is a test."
            # In the new approach, we need to use different methods to see the prompt
            # First we need to create the input values
            input_values = {"input": test_input}
            # Then we can get the prompt messages
            prompt_value = conversation.conversation.prompt.invoke(
                {"input": test_input, "chat_history": conversation.memory.chat_memory.messages}
            )
            print(f"\nPrompt that would be sent to OpenAI:\n")
            # Print each message in the prompt to clearly show the structure
            for i, message in enumerate(prompt_value.messages):
                print(f"Message {i+1} [{message.type}]: {message.content[:100]}..." if len(message.content) > 100 else message.content)
        except Exception as e:
            print(f"Error preparing prompt: {e}")

def main():
    """
    Main application function that runs the voice-enabled chatbot.
    
    This function:
    1. Sets up the conversation
    2. Presents a welcome message
    3. Runs the main conversation loop:
       - Records audio from the user
       - Converts speech to text
       - Processes the text with the language model
       - Converts response to speech
       - Repeats until user exits
    """
    # Check for model_config.json file first
    model_config_path = "model_config.json"
    skip_selection_menu = False
    available_keys = list(config.AVAILABLE_MODELS.keys())
    
    if os.path.exists(model_config_path):
        try:
            with open(model_config_path, 'r') as f:
                model_config = json.load(f)
                if 'model' in model_config:
                    selected_model = model_config['model']
                    # Accept key or full model string
                    if selected_model in config.AVAILABLE_MODELS:
                        config.MODEL_NAME = config.AVAILABLE_MODELS[selected_model]
                        print(f"Using model from config file: {selected_model} -> {config.MODEL_NAME}")
                        skip_selection_menu = True
                    elif selected_model in config.AVAILABLE_MODELS.values():
                        config.MODEL_NAME = selected_model
                        print(f"Using model from config file: {config.MODEL_NAME}")
                        skip_selection_menu = True
                    else:
                        print(f"Model '{selected_model}' not found in config.AVAILABLE_MODELS. Falling back to menu.")
        except Exception as e:
            print(f"Error reading model_config.json: {e}")
            print("Falling back to selection menu.")
    
    # Show selection menu if not using config file
    if not skip_selection_menu:
        print("=" * 50)
        print("AI COACH MODEL SELECTION")
        print("=" * 50)
        print("Please select a model to use:")
        
        for idx, key in enumerate(available_keys, 1):
            desc = key
            print(f"{idx}. {key} -> {config.AVAILABLE_MODELS[key]}")
        print("=" * 50)
        
        # Get user selection
        while True:
            selection = input(f"Enter your selection (1-{len(available_keys)}): ")
            if selection.isdigit() and 1 <= int(selection) <= len(available_keys):
                selected_key = available_keys[int(selection)-1]
                config.MODEL_NAME = config.AVAILABLE_MODELS[selected_key]
                print(f"Selected model: {selected_key} -> {config.MODEL_NAME}")
                # Ask if user wants to save this selection for future
                save_selection = input("Save this selection for future runs? (y/n): ").lower()
                if save_selection == 'y':
                    try:
                        with open(model_config_path, 'w') as f:
                            json.dump({"model": selected_key}, f)
                        print(f"Model preference saved to {model_config_path}")
                    except Exception as e:
                        print(f"Error saving model preference: {e}")
                break
            else:
                print("Invalid selection. Please try again.")
    
    # Reset model temperature based on the selected model
    config.MODEL_TEMPERATURE = config.get_model_temperature()
    
    # Print welcome information to the console
    print("\nVoice-Enabled Coaching Assistant")
    print("Say 'exit' or 'quit' to end the conversation.")
    print("Press any key to stop recording when you're done speaking.")
    print("-" * 50)
    
    # Create a new conversation instance
    # This sets up the language model and memory
    conversation = Conversation()
    
    # Record session start time and initialize a turn counter
    session_start = time.time()
    turn_counter = 0
    max_turns = 25  # After 25 exchanges, propose wrapping up
    
    # Define and speak a welcome message to the user
    welcome_message = "Hello! I'm your AI coaching assistant. How can I help you today?"
    print(f"Assistant: {welcome_message}")
    text_to_speech(welcome_message)  # Convert text to spoken audio
    
    # Main conversation loop - continues until user exits
    while True:
        try:
            # Clean up any lingering empty messages at the start of each loop
            conversation._clean_empty_messages()
            
            # Step 1: Record audio from the microphone
            print(RECORDING_START_MESSAGE)  # Inform user we're listening
            audio_file = record_audio()  # Record and save to temporary file
            
            # Step 2: Convert speech to text using Whisper API
            print(RECORDING_STOP_MESSAGE)  # Inform user we're processing
            transcription = transcribe_audio(audio_file)
            
            # If we got a valid transcription, process it
            if transcription:
                # Display what the user said
                print(f"You: {transcription}")
                
                # Step 3: Check if user wants to exit
                transcription_lower = transcription.lower().strip()
                
                # Check for exit commands
            #    if any(exit_cmd in transcription_lower for exit_cmd in ["exit", "quit", "bye", "goodbye"]):
            #        # Say goodbye and end the conversation
            #        farewell = "Goodbye! Have a great day!"
            #        print(f"Assistant: {farewell}")
            #        text_to_speech(farewell)
            #        break  # Exit the while loop
                
                # Special command to show history
                if any(history_cmd in transcription_lower for history_cmd in ["show history", "display history", "show conversation"]):
                    display_conversation_history(conversation)
                    response = "I've displayed your conversation history in the console."
                    print(f"Assistant: {response}")
                    text_to_speech(response)
                    continue
                
                # Check for user-initiated wrap-up requests
                elif any(wrap_cmd in transcription_lower for wrap_cmd in ["wrap up", "end session", "finish conversation", "summarize and end", "let's conclude", "finish session"]):
                    wrap_prompt = "Would you like to wrap up our session with a final summary and action plan? Please confirm by saying 'yes' or 'wrap up and summarize'."
                    conversation.add_ai_message_to_memory(wrap_prompt)
                    print(f"\nAssistant: {wrap_prompt}")
                    text_to_speech(wrap_prompt)
                    
                    # Directly log the wrap-up proposal to the log file
                    try:
                        with open(conversation.log_file, "a", encoding="utf-8") as f:
                            f.write(f"Coach: {wrap_prompt}\n")
                            f.write("-" * 50 + "\n")
                    except Exception as log_error:
                        print(f"Warning: Could not log wrap-up proposal: {log_error}")
                    
                    # Record user's confirmation response
                    print(RECORDING_START_MESSAGE)
                    confirm_audio = record_audio()
                    print(RECORDING_STOP_MESSAGE)
                    confirmation = transcribe_audio(confirm_audio)
                    
                    if confirmation:
                        print(f"You: {confirmation}")
                        
                        # Add this confirmation response to the conversation history as well
                        conversation.add_user_message_to_memory(confirmation)
                        
                        # Directly log the user's confirmation to the log file
                        try:
                            with open(conversation.log_file, "a", encoding="utf-8") as f:
                                f.write(f"User: {confirmation}\n")
                                f.write("-" * 50 + "\n")
                        except Exception as log_error:
                            print(f"Warning: Could not log user confirmation: {log_error}")
                        
                        # More stringent confirmation commands
                        confirmation_lower = confirmation.lower()
                        explicit_commands = ["wrap up and summarize", "wrap up", "summarize", "end session", "yes"]
                        has_explicit_command = any(cmd in confirmation_lower for cmd in explicit_commands)
                        
                        # Check for affirmative responses with context
                        affirmative_with_context = (
                            ("yes" in confirmation_lower or "yeah" in confirmation_lower or "sure" in confirmation_lower) and
                            ("summary" in confirmation_lower or "wrap" in confirmation_lower or "end" in confirmation_lower)
                        )
                        
                        if has_explicit_command or affirmative_with_context:
                            # User confirmed wrap-up request
                            wrap_up_requested = True
                            
                            try:
                                # Generate the final summary and action plan using the closing chain
                                print("Generating final summary and action plan...")
                                final_message = conversation.generate_closing_summary()
                                print(f"Assistant: {final_message}")
                                text_to_speech(final_message)
                                
                                # Add the final summary to the conversation memory before saving
                                conversation.add_ai_message_to_memory(final_message)
                                
                                # Save the conversation and final summary
                                save_conversation_history(conversation)
                                with open("final_summary.txt", "w", encoding="utf-8") as f:
                                    f.write("FINAL SUMMARY AND ACTION PLAN\n")
                                    f.write("="*50 + "\n\n")
                                    f.write(final_message)
                                print("Final summary saved to 'final_summary.txt'")
                                
                                # End the session
                                break
                            except Exception as e:
                                print(f"Error generating final summary: {e}")
                                error_response = "I had trouble creating a final summary. Let's continue our conversation."
                                print(f"Assistant: {error_response}")
                                text_to_speech(error_response)
                                wrap_up_requested = False  # If error occurred, continue conversation
                        else:
                            # User doesn't want to wrap up
                            reminder = "Okay, let's continue our conversation."
                            print(f"Assistant: {reminder}")
                            text_to_speech(reminder)
                            # Add coach's response to memory
                            conversation.add_ai_message_to_memory(reminder)
                            continue
                
                # Special command for debugging
                elif any(debug_cmd in transcription_lower for debug_cmd in ["debug messages", "check messages", "debug conversation"]):
                    # Call the debug_messages function to check for issues
                    conversation.debug_messages()
                    response = "I've performed a debug check on the conversation messages. Results are in the console."
                    print(f"Assistant: {response}")
                    text_to_speech(response)
                    continue
                
                # # Special command to save history to file
                # elif any(save_cmd in transcription_lower for save_cmd in ["save history", "export history", "save conversation"]):
                #     save_conversation_history(conversation)
                #     response = "Conversation history has been saved to 'conversation_history.txt'."
                #     print(f"Assistant: {response}")
                #     text_to_speech(response)
                #     continue
                
                # Step 4: Add the user's message to conversation history
                # We need to properly add to memory to preserve buffer functionality
                conversation.add_user_message_to_memory(transcription)
                
                # Step 5: Check if the conversation should be wrapped up BEFORE processing with main LLM
                elapsed_time = time.time() - session_start
                wrap_up_requested = False
                
                # Define variables to track wrap-up cooldown if they don't exist
                if not hasattr(main, 'wrap_up_cooldown'):
                    main.wrap_up_cooldown = 0
                if not hasattr(main, 'wrap_up_time_extension'):
                    main.wrap_up_time_extension = 0
                if not hasattr(main, 'ignore_should_wrap_up'):
                    main.ignore_should_wrap_up = False
                
                # Check if we're in the cooldown period
                if main.wrap_up_cooldown > 0:
                    # print(f"Wrap-up cooldown active: {main.wrap_up_cooldown} exchanges remaining")
                    main.wrap_up_cooldown -= 1
                    
                # Only check wrap-up conditions if not in cooldown
                elif (turn_counter >= max_turns or 
                      (not main.ignore_should_wrap_up and conversation.should_wrap_up()) or 
                      elapsed_time >= (30*60 + main.wrap_up_time_extension)):  # 30 min + any extension
                    
                    # Choose the appropriate wrap-up prompt based on what triggered it
                    wrap_prompt = ""
                    if not main.ignore_should_wrap_up and conversation.should_wrap_up():
                        # Content-based wrap-up (detected Way Forward content)
                        wrap_prompt = "It looks like we've made good progress on your issue. Shall we wrap up today's session with a quick summary and an action plan? If yes, please say wrap up and summarize."
                    elif turn_counter >= max_turns or elapsed_time >= (30*60 + main.wrap_up_time_extension):
                        # Time or message count based wrap-up
                        wrap_prompt = "I think we have covered a lot today and it is about the end of our session today. Would you like to wrap up our session with a final summary and action plan? If yes, please say wrap up and summarize."
                    
                    # Add the wrap-up prompt to conversation history before presenting it
                    conversation.add_ai_message_to_memory(wrap_prompt)
                    
                    print(f"\nAssistant: {wrap_prompt}")
                    text_to_speech(wrap_prompt)
                    
                    # Directly log the wrap-up proposal to the log file
                    try:
                        with open(conversation.log_file, "a", encoding="utf-8") as f:
                            f.write(f"Coach: {wrap_prompt}\n")
                            f.write("-" * 50 + "\n")
                    except Exception as log_error:
                        print(f"Warning: Could not log wrap-up proposal: {log_error}")
                    
                    # Record user's confirmation response
                    print(RECORDING_START_MESSAGE)
                    confirm_audio = record_audio()
                    print(RECORDING_STOP_MESSAGE)
                    confirmation = transcribe_audio(confirm_audio)
                    
                    if confirmation:
                        print(f"You: {confirmation}")
                        
                        # Add this confirmation response to the conversation history as well
                        conversation.add_user_message_to_memory(confirmation)
                        
                        # Directly log the user's confirmation to the log file
                        try:
                            with open(conversation.log_file, "a", encoding="utf-8") as f:
                                f.write(f"User: {confirmation}\n")
                                f.write("-" * 50 + "\n")
                        except Exception as log_error:
                            print(f"Warning: Could not log user confirmation: {log_error}")
                        
                        # More stringent confirmation commands
                        confirmation_lower = confirmation.lower()
                        # Check for explicit wrap-up commands
                        explicit_commands = ["wrap up and summarize", "wrap up", "summarize", "end session"]
                        has_explicit_command = any(cmd in confirmation_lower for cmd in explicit_commands)
                        
                        # Check for affirmative responses with context
                        affirmative_with_context = (
                            ("yes" in confirmation_lower or "yeah" in confirmation_lower or "sure" in confirmation_lower) and
                            ("summary" in confirmation_lower or "wrap" in confirmation_lower or "end" in confirmation_lower)
                        )
                        
                        if has_explicit_command or affirmative_with_context:
                            wrap_up_requested = True
                            
                            # Get the current conversation summary
                            summary_data = conversation.get_conversation_summary()
                            summary = summary_data.get('summary', 'No summary available.')
                            
                            try:
                                # Generate the final summary and action plan using the closing chain
                                print("Generating final summary and action plan...")
                                final_message = conversation.generate_closing_summary()
                                print(f"Assistant: {final_message}")
                                text_to_speech(final_message)
                                
                                # Add the final summary to the conversation memory before saving
                                conversation.add_ai_message_to_memory(final_message)
                                
                                # Save the conversation and final summary
                                save_conversation_history(conversation)
                                with open("final_summary.txt", "w", encoding="utf-8") as f:
                                    f.write("FINAL SUMMARY AND ACTION PLAN\n")
                                    f.write("="*50 + "\n\n")
                                    f.write(final_message)
                                print("Final summary saved to 'final_summary.txt'")
                                
                                # End the session
                                break
                            except Exception as e:
                                print(f"Error generating final summary: {e}")
                                error_response = "I had trouble creating a final summary. Let's continue our conversation."
                                print(f"Assistant: {error_response}")
                                text_to_speech(error_response)
                                wrap_up_requested = False  # If error occurred, continue conversation
                        else:
                            # User doesn't want to wrap up
                            reminder = "Okay, let's continue our conversation."
                            print(f"Assistant: {reminder}")
                            text_to_speech(reminder)
                            # Add coach's response to memory
                            conversation.add_ai_message_to_memory(reminder)
                            
                            # Reset wrap-up conditions and add cooldown
                            # 1. Reset turn counter to avoid immediate re-prompting
                            turn_counter = max(0, turn_counter - 5)
                            
                            # 2. Set cooldown period for 5 conversation exchanges
                            main.wrap_up_cooldown = 5
                            # print(f"Set wrap-up cooldown for next {main.wrap_up_cooldown} exchanges")
                            
                            # 3. Extend session timeout by 5 minutes
                            main.wrap_up_time_extension += 5 * 60  # 5 minutes in seconds
                            # print(f"Extended session timeout by 5 minutes (total extension: {main.wrap_up_time_extension/60:.1f} minutes)")
                            
                            # 4. Temporarily ignore should_wrap_up() results
                            main.ignore_should_wrap_up = True
                            # print("Ignoring should_wrap_up() results until cooldown ends")
                
                # Step 6: Only process with main LLM if we're not wrapping up
                if not wrap_up_requested:
                    print(RESPONSE_START_MESSAGE)  # Inform user we're thinking
                    try:
                        # Since we already added the user message to memory, we need to
                        # process it differently to avoid duplication
                        start_time = time.time()
                        
                        # Use our dedicated method to process input without adding to memory again
                        response = conversation.process_input_with_existing_message(transcription)
                        
                        processing_time = time.time() - start_time
                        # print(f"Processing completed in {processing_time:.2f} seconds")
                    except Exception as e:
                        print(f"Error processing input: {e}")
                        response = "I'm having trouble processing that right now. Could we try something else?"
                    
                    # Step 7: Display and speak the response
                    print(f"Assistant: {response}")
                    text_to_speech(response)  # Convert text to spoken audio
                    
                    # Increment turn counter after each exchange
                    turn_counter += 1
                    
                    # Reset ignore_should_wrap_up flag if cooldown is over
                    if main.wrap_up_cooldown == 0 and main.ignore_should_wrap_up:
                        main.ignore_should_wrap_up = False
                        # print("Cooldown ended, should_wrap_up() results will be checked again")
            else:
                # Handle case where transcription failed
                print("No transcription available. Please try again.")
                error_msg = "I couldn't hear what you said. Could you please try again?"
                print(f"Assistant: {error_msg}")
                text_to_speech(error_msg)
                
                # Add a delay to prevent immediate retry loop
                time.sleep(1.5)  # Give the user 1.5 seconds to prepare before next recording
        
        # Handle user pressing Ctrl+C to exit
        except KeyboardInterrupt:
            print("\nStopping the application...")
            break
        
        # Handle any other errors that might occur
        except Exception as e:
            print(f"An error occurred: {e}")
            try:
                error_msg = "Sorry, I encountered an error. Let's continue our conversation."
                print(f"Assistant: {error_msg}")
                text_to_speech(error_msg)
            except Exception as speech_error:
                print(f"Could not provide error feedback: {speech_error}")
            continue  # Continue the loop despite the error

# This is the standard way to make a Python script runnable
# It means this code only runs if this file is executed directly
if __name__ == "__main__":
    main() 