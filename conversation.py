from langchain.memory import ConversationBufferMemory  # For storing conversation history
from langchain.memory import ConversationSummaryBufferMemory  # For storing conversation history with summaries
from langchain.chains import ConversationChain  # For managing conversation flow
from langchain_openai import ChatOpenAI  # For connecting to OpenAI's models
from langchain_core.messages import SystemMessage  # For structured system messages
from langchain_core.prompts import (  # For creating structured prompts
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
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
        # Step 1: Initialize the language models
        # Main LLM for conversation
        model_params = {
            "model": MODEL_NAME,
        }

        if MODEL_TEMPERATURE is not None:
            model_params["temperature"] = MODEL_TEMPERATURE

        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            **model_params
        )
        
        # Dedicated LLM for summarization
        # Using GPT-3.5-turbo which has proven reliability for summarization tasks
        self.summary_llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",  # Changed from GPT-4o-mini to GPT-3.5-turbo
            temperature=0.3,  # Lower temperature for more consistent summaries
            request_timeout=15  # Add timeout to prevent hanging
        )
        
        # Step 2: Set up conversation memory to store dialogue history
        # Using ConversationSummaryBufferMemory to maintain a summary of older messages
        # while keeping recent messages in full detail
        self.memory = ConversationSummaryBufferMemory(
            llm=self.summary_llm,  # Use dedicated summarization model
            memory_key="chat_history",
            max_token_limit=1500,  # Further reduced to ensure summarization happens more quickly
            return_messages=True,
            verbose=True  # Make summarization process visible in console output
        )
        
        # Track if summarization has failed before
        self.summarization_failed = False
        
        # Step 3: Create the prompt template with clear role separation
        # This makes it easier for the model to understand who is speaking
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),  # System prompt clearly labeled
            MessagesPlaceholder(variable_name="chat_history"),  # Dedicated placeholder for chat history
            HumanMessagePromptTemplate.from_template("{input}")  # Clear human input
        ])
        
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
        self.summary_log_file = os.path.join(self.log_dir, f"summary_{self.session_id}.txt")
    
    def get_conversation_summary(self):
        """
        Get the current summary of the conversation.
        
        Returns:
            dict: A dictionary containing:
                - 'summary': The current conversation summary
                - 'buffer_length': Number of messages in the recent buffer
                - 'total_messages': Total number of messages processed
                - 'summarization_status': Whether summarization is working properly
        """
        result = {
            'summary': '',
            'buffer_length': 0,
            'total_messages': 0,
            'summarization_status': 'ok'
        }
        
        try:
            # Get conversation history count safely
            try:
                result['total_messages'] = len(self.get_conversation_history())
            except Exception as e:
                safe_print(f"Error getting conversation history count: {e}")
                result['total_messages'] = -1
            
            # Get summary safely
            try:
                result['summary'] = self._safe_get_summary()
            except Exception as e:
                safe_print(f"Error getting summary in summary method: {e}")
                result['summarization_status'] = f"error: {str(e)}"
            
            # Get buffer length safely
            try:
                result['buffer_length'] = len(self.memory.buffer)
            except Exception as e:
                safe_print(f"Error getting buffer length: {e}")
                result['buffer_length'] = -1
                
            # Set status if summarization has failed before
            if self.summarization_failed:
                result['summarization_status'] = 'previously_failed'
                
            return result
        except Exception as e:
            safe_print(f"Error in get_conversation_summary: {e}")
            return {
                'summary': '',
                'buffer_length': 0, 
                'total_messages': 0,
                'summarization_status': f'critical_error: {str(e)}'
            }

    def _log_summary_update(self, old_summary, new_summary):
        """Log when the conversation summary is updated."""
        try:
            # Print to console as well for immediate visibility
            safe_print("\n" + "!" * 80)
            safe_print("SUMMARY UPDATE DETECTED!")
            safe_print("Previous summary length: " + str(len(old_summary)))
            safe_print("New summary length: " + str(len(new_summary)))
            safe_print("!" * 80 + "\n")
            
            with open(self.summary_log_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n=== Summary Update at {timestamp} ===\n")
                f.write("Previous summary:\n")
                f.write(f"{old_summary}\n")
                f.write("New summary:\n")
                f.write(f"{new_summary}\n")
                f.write("-" * 50 + "\n")
                
            # Create a flag file to indicate summarization has occurred
            flag_file = os.path.join(self.log_dir, f"summarization_occurred_{self.session_id}.flag")
            with open(flag_file, "w") as f:
                f.write(f"Summarization occurred at {timestamp}\n")
                f.write(f"Summary length: {len(new_summary)}\n")
                
        except Exception as e:
            safe_print(f"Warning: Could not log summary update: {e}")

    def _safe_get_summary(self):
        """Safely get the current summary with error handling."""
        try:
            return self.memory.moving_summary_buffer
        except Exception as e:
            safe_print(f"Warning: Error accessing summary: {e}")
            return ""
            
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
            # Get the current summary before processing - with error handling
            old_summary = self._safe_get_summary()

            # Step 2: Use the conversation chain to generate a response
            # This automatically updates the conversation memory
            response = self.conversation.predict(input=user_input)
            
            # Check if summary has changed and log if it has - with error handling
            try:
                new_summary = self._safe_get_summary()
                if old_summary != new_summary:
                    self._log_summary_update(old_summary, new_summary)
            except Exception as e:
                safe_print(f"Warning: Error during summary update check: {e}")
                self.summarization_failed = True
            
            # After getting a response, log the exchange
            self._log_exchange(user_input, response)
            
            # Step 3: Return the response
            return response
        except Exception as e:
            # Handle any errors that might occur during processing
            error_msg = str(e)
            safe_print(f"Error in conversation processing: {error_msg}")
            
            # Check if it's a timeout error
            if "timeout" in error_msg.lower():
                # Mark summarization as failed
                self.summarization_failed = True
                
                # Try to recover by using a fallback mechanism
                try:
                    # If there's an issue with summarization, try to continue without it
                    safe_print("Attempting to recover from summarization failure...")
                    
                    # Create a simpler memory object as fallback if needed
                    if not hasattr(self, '_fallback_memory'):
                        from langchain.memory import ConversationBufferWindowMemory
                        self._fallback_memory = ConversationBufferWindowMemory(
                            memory_key="chat_history",
                            k=10,  # Remember only the last 10 exchanges
                            return_messages=True
                        )
                        
                        # Copy current messages to fallback memory if possible
                        try:
                            # Get the most recent messages we can
                            recent_messages = self.memory.chat_memory.messages[-20:]
                            
                            # Add them to fallback memory
                            for msg in recent_messages:
                                self._fallback_memory.chat_memory.add_message(msg)
                                
                            safe_print(f"Loaded {len(recent_messages)} messages into fallback memory")
                        except Exception as fallback_error:
                            safe_print(f"Error initializing fallback memory: {fallback_error}")
                    
                    # Use the fallback memory for this request only
                    temp_chain = ConversationChain(
                        llm=self.llm,
                        memory=self._fallback_memory,
                        prompt=self.conversation.prompt,
                        verbose=False
                    )
                    
                    # Process with fallback
                    fallback_response = temp_chain.predict(input=user_input)
                    
                    # Update fallback memory
                    self._fallback_memory.save_context({"input": user_input}, {"output": fallback_response})
                    
                    # Log the exchange
                    self._log_exchange(user_input, fallback_response + " [FALLBACK MODE]")
                    
                    return fallback_response + "\n\n(Note: I've switched to a simplified memory mode to ensure our conversation continues smoothly.)"
                except Exception as fallback_error:
                    safe_print(f"Fallback mechanism failed: {fallback_error}")
                
                return "I'm taking a bit longer than expected to process your message. Let's continue our conversation - what else would you like to discuss?"
            
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

    def debug_summarization(self):
        """
        Force summarization to happen and debug the process.
        This can be called to explicitly test if summarization is working.
        
        Returns:
            dict: Debug information about the summarization process
        """
        safe_print("\n" + "=" * 80)
        safe_print("DEBUGGING SUMMARIZATION PROCESS")
        safe_print("=" * 80)
        
        results = {
            'success': False,
            'summary_before': '',
            'summary_after': '',
            'error': None,
            'buffer_size_before': 0,
            'buffer_size_after': 0
        }
        
        try:
            # Get current state
            results['summary_before'] = self._safe_get_summary()
            results['buffer_size_before'] = len(self.memory.buffer) if hasattr(self.memory, 'buffer') else 0
            
            safe_print(f"Current summary length: {len(results['summary_before'])}")
            safe_print(f"Current buffer size: {results['buffer_size_before']}")
            
            # Add a dummy message to force summarization
            dummy_message = "This is a long message to help trigger summarization. " * 20
            safe_print(f"Adding dummy message of length {len(dummy_message)}")
            
            # Add directly to memory
            self.memory.save_context(
                {"input": dummy_message}, 
                {"output": "Response to help trigger summarization. " * 10}
            )
            
            # Get updated state
            results['summary_after'] = self._safe_get_summary()
            results['buffer_size_after'] = len(self.memory.buffer) if hasattr(self.memory, 'buffer') else 0
            
            safe_print(f"New summary length: {len(results['summary_after'])}")
            safe_print(f"New buffer size: {results['buffer_size_after']}")
            
            # Check if summarization happened
            if results['summary_before'] != results['summary_after']:
                safe_print("✅ SUMMARIZATION SUCCESSFUL - Summary changed!")
                results['success'] = True
            else:
                safe_print("⚠️ No change in summary detected")
            
            # Log the attempt
            self._log_summary_update(results['summary_before'], results['summary_after'])
            
        except Exception as e:
            error_msg = str(e)
            safe_print(f"❌ ERROR during summarization debug: {error_msg}")
            results['error'] = error_msg
        
        safe_print("=" * 80)
        return results 