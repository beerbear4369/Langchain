import time
import signal
from functools import wraps
from audio_input import record_audio, transcribe_audio
from conversation import Conversation
from audio_output import text_to_speech
from config import RECORDING_START_MESSAGE, RECORDING_STOP_MESSAGE, RESPONSE_START_MESSAGE

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
    messages = conversation.get_conversation_history()
    
    try:
        with open("conversation_history.txt", "w", encoding="utf-8") as f:
            f.write("CONVERSATION HISTORY\n")
            f.write("="*50 + "\n\n")
            
            for message in messages:
                role = "User" if message.type == "human" else "Coach"
                f.write(f"{role}: {message.content}\n\n")
        
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
     # Print welcome information to the console
    print("Voice-Enabled Coaching Assistant")
    print("Say 'exit' or 'quit' to end the conversation.")
    print("Press any key to stop recording when you're done speaking.")
    print("-" * 50)
    
    # Create a new conversation instance
    # This sets up the language model and memory
    conversation = Conversation()
    
    # Define and speak a welcome message to the user
    welcome_message = "Hello! I'm your AI coaching assistant. How can I help you today?"
    print(f"Assistant: {welcome_message}")
    text_to_speech(welcome_message)  # Convert text to spoken audio
    
    # Main conversation loop - continues until user exits
    while True:
        try:
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
                if any(exit_cmd in transcription_lower for exit_cmd in ["exit", "quit", "bye", "goodbye"]):
                    # Say goodbye and end the conversation
                    farewell = "Goodbye! Have a great day!"
                    print(f"Assistant: {farewell}")
                    text_to_speech(farewell)
                    break  # Exit the while loop
                
                # Special command to show history
                elif any(history_cmd in transcription_lower for history_cmd in ["show history", "display history", "show conversation"]):
                    display_conversation_history(conversation)
                    response = "I've displayed your conversation history in the console."
                    print(f"Assistant: {response}")
                    text_to_speech(response)
                    continue
                
                # Special command to save history to file
                elif any(save_cmd in transcription_lower for save_cmd in ["save history", "export history", "save conversation"]):
                    save_conversation_history(conversation)
                    response = "Conversation history has been saved to 'conversation_history.txt'."
                    print(f"Assistant: {response}")
                    text_to_speech(response)
                    continue
                
                # Special command for debugging
                elif any(debug_cmd in transcription_lower for debug_cmd in ["debug memory", "debug"]):
                    debug_conversation_memory(conversation)
                    response = "Debug information has been displayed in the console."
                    print(f"Assistant: {response}")
                    text_to_speech(response)
                    continue
                
                # Step 4: Process the user's input and generate a response
                print(RESPONSE_START_MESSAGE)  # Inform user we're thinking
                try:
                    # Add timeout protection for API call
                    start_time = time.time()
                    response = conversation.process_input(transcription)
                    processing_time = time.time() - start_time
                    print(f"Processing completed in {processing_time:.2f} seconds")
                except Exception as e:
                    print(f"Error processing input: {e}")
                    response = "I'm having trouble processing that right now. Could we try something else?"
                
                # Step 5: Display and speak the response
                print(f"Assistant: {response}")
                text_to_speech(response)  # Convert text to spoken audio
            else:
                # Handle case where transcription failed
                print("No transcription available. Please try again.")
                error_msg = "I couldn't hear what you said. Could you please try again?"
                print(f"Assistant: {error_msg}")
                text_to_speech(error_msg)
        
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