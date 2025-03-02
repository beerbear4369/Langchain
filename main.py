import time
from audio_input import record_audio, transcribe_audio
from conversation import Conversation
from audio_output import text_to_speech
from config import RECORDING_START_MESSAGE, RECORDING_STOP_MESSAGE, RESPONSE_START_MESSAGE

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
    print("Voice-Enabled Chatbot")
    print("Say 'exit' or 'quit' to end the conversation.")
    print("-" * 50)
    
    # Create a new conversation instance
    # This sets up the language model and memory
    conversation = Conversation()
    
    # Define and speak a welcome message to the user
    welcome_message = "Hello! I'm your voice assistant. How can I help you today?"
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
                if transcription.lower() in ["exit", "quit", "bye", "goodbye"]:
                    # Say goodbye and end the conversation
                    farewell = "Goodbye! Have a great day!"
                    print(f"Assistant: {farewell}")
                    text_to_speech(farewell)
                    break  # Exit the while loop
                
                # Step 4: Process the user's input and generate a response
                print(RESPONSE_START_MESSAGE)  # Inform user we're thinking
                response = conversation.process_input(transcription)
                
                # Step 5: Display and speak the response
                print(f"Assistant: {response}")
                text_to_speech(response)  # Convert text to spoken audio
            else:
                # Handle case where transcription failed
                print("No transcription available. Please try again.")
        
        # Handle user pressing Ctrl+C to exit
        except KeyboardInterrupt:
            print("\nStopping the application...")
            break
        
        # Handle any other errors that might occur
        except Exception as e:
            print(f"An error occurred: {e}")
            continue  # Continue the loop despite the error

# This is the standard way to make a Python script runnable
# It means this code only runs if this file is executed directly
if __name__ == "__main__":
    main() 