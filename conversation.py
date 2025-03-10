from langchain.memory import ConversationBufferMemory  # For storing conversation history
from langchain.chains.conversation.base import ConversationChain  # For managing conversation flow
from langchain_openai import ChatOpenAI  # For connecting to OpenAI's models
from langchain.prompts import PromptTemplate  # For creating prompt templates
from config import OPENAI_API_KEY, SYSTEM_PROMPT, MODEL_NAME, MODEL_TEMPERATURE  # Import configuration
import os
import json
from datetime import datetime
import sys
import subprocess

# Fix console encoding for international characters
if sys.platform == 'win32':
    # Instead of redirecting stdout/stderr, just set the console mode
    try:
        # Use Windows-specific command to set UTF-8 mode
        subprocess.run(['chcp', '65001'], shell=True, check=False)
    except Exception as e:
        print(f"Warning: Could not set console to UTF-8 mode: {e}")
        
    # Ensure Python knows we want UTF-8 output
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(*args, **kwargs):
    """Print function that safely handles Unicode characters."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fall back to printing with limited encoding
        try:
            # Try to encode as ASCII with replacement characters
            encoded_args = [str(arg).encode('ascii', 'replace').decode('ascii') for arg in args]
            print(*encoded_args, **kwargs)
        except Exception as e:
            print(f"Error printing output: {e}")

class Conversation:
    """
    Manages the conversation between the user and the AI assistant.
    
    This class:
    1. Sets up the language model (fine-tuned GPT-4o-mini)
    2. Maintains conversation history
    3. Processes user input and generates responses
    4. Provides access to conversation history
    """
    
    def __init__(self):
        """
        Initialize the conversation manager with a language model and memory.
        
        This method:
        1. Sets up the fine-tuned language model
        2. Creates a memory component to store conversation history
        3. Creates a conversation chain to manage the flow
        """
        # Step 1: Initialize the language model
        # - model=MODEL_NAME: Use your fine-tuned model
        # - temperature=MODEL_TEMPERATURE: Control randomness (higher = more creative)
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=MODEL_NAME,
            temperature=MODEL_TEMPERATURE
        )
        
        # Step 2: Set up conversation memory to store dialogue history
        # This allows the AI to remember previous parts of the conversation
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Step 3: Create the prompt template
        # This defines the format of prompts sent to the language model
        # It includes the system prompt, conversation history, and current input
        template = f"{SYSTEM_PROMPT}\n\n{{history}}\nHuman: {{input}}\nAI:"
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],  # Variables to fill in
            template=template,  # The template string
        )
        
        # Step 4: Create the conversation chain
        # This connects the language model, memory, and prompt template
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=False  # Don't print debug information
        )
        
        # Add logging directory
        self.log_dir = "conversation_logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a log file for this session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"conversation_{self.session_id}.txt")
    
    def process_input(self, user_input):
        """
        Process user input and generate an AI response.
        
        This method:
        1. Checks if the input is valid
        2. Sends the input to the language model
        3. Returns the generated response
        
        Args:
            user_input (str): The user's text input
            
        Returns:
            str: The AI's response text
        """
        # Step 1: Check if the input is valid
        if not user_input:
            return "I couldn't hear you clearly. Could you please repeat that?"
        
        try:
            # Step 2: Use the conversation chain to generate a response
            # This automatically updates the conversation memory
            response = self.conversation.predict(input=user_input)
            
            # After getting a response, log the exchange
            self._log_exchange(user_input, response)
            
            # Step 3: Return the response
            return response
        except Exception as e:
            # Handle any errors that might occur during processing
            safe_print(f"Error in conversation processing: {e}")
            return "I'm having trouble processing that request. Let's try again."
    
    def _log_exchange(self, user_input, response):
        """Log the conversation exchange to a file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"User: {user_input}\n")
                f.write(f"Coach: {response}\n")
                f.write("-" * 50 + "\n")
        except Exception as e:
            safe_print(f"Warning: Could not log conversation: {e}")
    
    def get_conversation_history(self):
        """
        Get the full conversation history.
        
        This method returns all messages in the conversation, which can be
        useful for displaying the transcript or for further processing.
        
        Returns:
            list: List of conversation messages
        """
        return self.memory.chat_memory.messages 