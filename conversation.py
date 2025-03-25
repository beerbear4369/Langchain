from langchain.memory import ConversationBufferMemory  # For storing conversation history
from langchain.memory import ConversationSummaryBufferMemory  # For storing conversation history with summaries
from langchain.chains import ConversationChain  # For managing conversation flow
from langchain_openai import ChatOpenAI  # For connecting to OpenAI's models
from langchain_core.messages import SystemMessage  # For structured system messages
from langchain.chains import LLMChain  # For the closing chain
from langchain_core.prompts import (  # For creating structured prompts
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from config import (  # Import configuration
    OPENAI_API_KEY, 
    SYSTEM_PROMPT, 
    MODEL_NAME, 
    MODEL_TEMPERATURE, 
    CUSTOM_SUMMARY_PROMPT,
    PROGRESSION_ANALYSIS_PROMPT,
    FALLBACK_PROMPT,
    CLOSING_PROMPT,
    WRAP_UP_DECISION_PROMPT
)
import os
import json
from datetime import datetime
import sys
import subprocess
import time

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
            model="gpt-3.5-turbo",  
            temperature=0.3,  # Lower temperature for more consistent summaries
            request_timeout=20  # Increased timeout for more thorough summarization
        )
        
        # Step 2: Set up conversation memory to store dialogue history with custom summarization
        # Create a custom summarization prompt that focuses on conversation history
        
        # Convert string template to PromptTemplate object
        custom_summary_template = PromptTemplate.from_template(CUSTOM_SUMMARY_PROMPT)
        
        # Initialize memory with custom prompt
        self.memory = ConversationSummaryBufferMemory(
            llm=self.summary_llm,
            memory_key="chat_history",
            max_token_limit=2000,  # Increased to retain more context
            return_messages=True,
            prompt=custom_summary_template,
            verbose=True  # Make summarization process visible in console output
        )
        
        # Track if summarization has failed before
        self.summarization_failed = False
        
        # Add a conversation rounds counter that persists regardless of summarization
        self.conversation_rounds = 0
        
        # Step 3: Create the prompt template with clear role separation and include conversation rounds
        # This makes it easier for the model to understand who is speaking and track conversation progress
        self.prompt_template = lambda rounds: ChatPromptTemplate.from_messages([
            SystemMessage(content=f"{SYSTEM_PROMPT}\n\nCurrent conversation round: {rounds}/30"),  # System prompt with rounds info
            MessagesPlaceholder(variable_name="chat_history"),  # Dedicated placeholder for chat history
            HumanMessagePromptTemplate.from_template("{input}")  # Clear human input
        ])
        
        # Initialize the prompt with conversation_rounds = 0
        prompt = self.prompt_template(self.conversation_rounds)
        
        # Step 4: Create the conversation chain
        # This connects the language model, memory, and prompt template
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=False  # Don't print debug information
        )
        
        # Patch the conversation's predict method to prevent empty inputs from being saved
        original_predict = self.conversation.predict
        
        def patched_predict(input: str, **kwargs):
            # If input is empty, don't save it to memory
            if not input.strip():
                # Get current history
                chat_history = self.memory.chat_memory.messages
                
                # Prepare the prompt with existing history but without adding empty input
                input_values = {"input": "", "chat_history": chat_history}
                prompt_value = self.conversation.prompt.invoke(input_values)
                
                # Get response directly from LLM
                response = self.llm.invoke(prompt_value.messages).content
                
                # Add only the assistant's response to memory
                self.memory.chat_memory.add_ai_message(response)
                
                # Clean up any empty messages that might still exist
                self._clean_empty_messages()
                
                return response
            else:
                # Use the original predict method for non-empty inputs
                return original_predict(input, **kwargs)
        
        # Replace the predict method with our patched version
        # This isn't allowed directly with Pydantic, so we use a wrapper approach
        def predict_wrapper(*args, **kwargs):
            return patched_predict(*args, **kwargs)
            
        # Store the original method
        self._original_predict = original_predict
        # Store our wrapper function
        self._patched_predict = predict_wrapper
        
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
            # safe_print("\n" + "!" * 80)
            # safe_print("SUMMARY UPDATE DETECTED!")
            # safe_print("Previous summary length: " + str(len(old_summary)))
            # safe_print("New summary length: " + str(len(new_summary)))
            # safe_print("!" * 80 + "\n")
            
            with open(self.summary_log_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n=== Summary Update at {timestamp} ===\n")
                f.write("<PREVIOUS_SUMMARY>\n")
                f.write(f"{old_summary}\n")
                f.write("</PREVIOUS_SUMMARY>\n\n")
                f.write("<UPDATED_SUMMARY>\n")
                f.write(f"{new_summary}\n")
                f.write("</UPDATED_SUMMARY>\n")
                f.write("-" * 50 + "\n")
                
            # Create a flag file to indicate summarization has occurred
            flag_file = os.path.join(self.log_dir, f"summarization_occurred_{self.session_id}.flag")
            with open(flag_file, "w") as f:
                f.write(f"Summarization occurred at {timestamp}\n")
                f.write(f"Summary length: {len(new_summary)}\n")
                
        except Exception as e:
            # safe_print(f"Warning: Could not log summary update: {e}")
            pass

    def _safe_get_summary(self):
        """Safely get the current summary with error handling."""
        try:
            return self.memory.moving_summary_buffer
        except Exception as e:
            safe_print(f"Warning: Error accessing summary: {e}")
            return ""
            
    def analyze_conversation_progression(self):
        """
        Analyze the conversation progression through the T-GROW coaching model.
        
        Returns:
            dict: Analysis of conversation progression through T-GROW stages
        """
        try:
            # Get current summary and recent messages
            summary = self._safe_get_summary()
            history = self.get_conversation_history()
            recent_messages = history[-min(10, len(history)):]
            
            # Format the recent messages in a readable way
            formatted_recent_messages = ""
            for msg in recent_messages:
                if msg.type == "human":
                    formatted_recent_messages += f"Client: {msg.content}\n\n"
                else:
                    formatted_recent_messages += f"Coach: {msg.content}\n\n"
            
            # Format the progression analysis prompt with actual values
            formatted_prompt = PROGRESSION_ANALYSIS_PROMPT.format(
                summary=summary,
                recent_messages=formatted_recent_messages
            )
            
            # Get analysis
            analysis = self.summary_llm.predict(formatted_prompt)
            
            return {
                'progression_analysis': analysis,
                'summary': summary
            }
        except Exception as e:
            safe_print(f"Warning: Could not analyze conversation progression: {e}")
            return {
                'progression_analysis': "Error analyzing conversation progression",
                'summary': self._safe_get_summary()
            }
            
    def should_wrap_up(self):
        """
        Determine if the session should be wrapped up based on LLM analysis of the conversation.
        
        Uses an LLM to analyze the entire conversation history and determine if it has reached 
        a natural conclusion point according to the T-GROW coaching model.
        
        Returns:
          bool: True if session should be wrapped up, False otherwise.
        """
        # Get conversation history and summary
        history = self.get_conversation_history()
        
        # Add debug print statements
        # print("\n--- DEBUG CONVERSATION HISTORY ---")
        # print(f"Conversation rounds: {self.conversation_rounds}")
        # print("--- END DEBUG ---\n")
        
        # IMPORTANT: Only check for wrap-up if we have enough conversation rounds
        # Use conversation_rounds counter which is immune to summarization effects
        if self.conversation_rounds < 20:  # Threshold set to 15 rounds (adjust as needed)
            # print(f"Not enough conversation rounds for wrap-up check ({self.conversation_rounds}/15 rounds). Skipping LLM call.")
            return False
            
        try:
            # Format conversation history for the LLM
            formatted_history = ""
            for msg in history:
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    # It's a Message object
                    msg_type = msg.type
                    msg_content = msg.content
                else:
                    # It's a dict
                    msg_type = msg.get('type', 'unknown')
                    msg_content = msg.get('content', '')
                
                # Add the message to the formatted history
                if msg_type in ['human', 'user']:
                    formatted_history += f"User: {msg_content}\n\n"
                elif msg_type in ['ai', 'assistant']:
                    formatted_history += f"Coach: {msg_content}\n\n"
            
            # Get the conversation summary
            summary_data = self.get_conversation_summary()
            summary = summary_data.get('summary', '')
            
            # Create a dedicated LLM for wrap-up decision
            wrap_up_llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model="gpt-3.5-turbo",  # Using 3.5 turbo for efficiency
                temperature=0.1  # Low temperature for more consistent decisions
            )
            
            # Create prompt from WRAP_UP_DECISION_PROMPT template
            wrap_up_template = PromptTemplate.from_template(WRAP_UP_DECISION_PROMPT)
            
            # Create the chain
            wrap_up_chain = LLMChain(
                llm=wrap_up_llm,
                prompt=wrap_up_template,
                verbose=False
            )
            
            # Run the chain
            response = wrap_up_chain.run({
                'conversation_history': formatted_history,
                'conversation_summary': summary
            })
            
            # Clean up and parse the response
            clean_response = response.strip().lower()
            # print(f"\n--- WRAP-UP DECISION ---\nLLM decision: '{clean_response}'\n--- END DECISION ---\n")
            
            # Return True if the LLM says "yes", False otherwise
            return clean_response == "yes"
            
        except Exception as e:
            # Log the error and fall back to the default behavior (no wrap-up)
            print(f"Error in LLM-based wrap-up decision: {e}")
            print("Falling back to default behavior: no wrap-up")
            return False
            
    def process_input(self, user_input, timeout_seconds=60):
        """
        Process user input and generate an AI response with timeout protection.
        
        This method:
        1. Checks if the input is valid
        2. Sends the input to the language model with timeout protection
        3. Returns the generated response
        
        Args:
            user_input (str): The user's text input
            timeout_seconds (int): Maximum time in seconds to wait for a response
            
        Returns:
            str: The AI's response text
        """
        # Step 1: Check if the input is valid
        if not user_input:
            return "I couldn't hear you clearly. Could you please repeat that?"
            
        try:
            # Clean up any empty messages first
            self._remove_duplicate_messages()
            self._clean_empty_messages()
            
            # Add the input to memory
            self.memory.chat_memory.add_user_message(user_input)
            
            # Update the conversation prompt with current conversation_rounds
            updated_prompt = self.prompt_template(self.conversation_rounds)
            self.conversation.prompt = updated_prompt
            
            # Track the start time for timeout purposes
            start_time = time.time()
            
            # Get the current summary before processing - with error handling
            old_summary = self._safe_get_summary()

            # Step 2: Use the conversation chain to generate a response with timeout
            try:
                # This automatically updates the conversation memory
                # Add a timeout parameter if the API wrapper supports it
                if hasattr(self.llm, 'request_timeout'):
                    original_timeout = self.llm.request_timeout
                    self.llm.request_timeout = timeout_seconds
                    response = self.conversation.predict(input=user_input)
                    self.llm.request_timeout = original_timeout
                else:
                    # If no timeout support, use the regular predict method
                    response = self.conversation.predict(input=user_input)
                
                # Clean up any empty messages that might have been introduced
                self._clean_empty_messages()
                
                # Track and log response time
                elapsed_time = time.time() - start_time
                # print(f"Response generated in {elapsed_time:.2f} seconds")
                
            except Exception as timeout_error:
                elapsed_time = time.time() - start_time
                # print(f"API call failed after {elapsed_time:.2f} seconds: {timeout_error}")
                
                # Try a fallback approach - simpler and more reliable
                try:
                    # Let the user know we're trying again
                    # print("Attempting fallback response generation...")
                    
                    # Use a simpler prompt with the same model but direct call
                    formatted_fallback_prompt = FALLBACK_PROMPT.format(user_input=user_input)
                    fallback_response = self.llm.predict(formatted_fallback_prompt)
                    
                    # Since we're bypassing the conversation chain, manually add to memory
                    self.memory.chat_memory.add_user_message(user_input)
                    self.memory.chat_memory.add_ai_message(fallback_response)
                    
                    # Clean up any empty messages that might have been introduced
                    self._clean_empty_messages()
                    
                    # Increment conversation round counter even when using fallback
                    self.conversation_rounds += 1
                    # print(f"Conversation round incremented to {self.conversation_rounds} (via fallback)")
                    
                    return fallback_response
                except Exception as fallback_error:
                    safe_print(f"Fallback approach also failed: {fallback_error}")
                    raise timeout_error  # Re-raise the original error
            
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
            
            # Increment conversation round counter after successful completion
            self.conversation_rounds += 1
            # print(f"Conversation round incremented to {self.conversation_rounds}")
            
            # Step 3: Return the response
            return response
        except Exception as e:
            # Handle any errors that might occur during processing
            error_msg = str(e)
            safe_print(f"Error in conversation processing: {error_msg}")
            
            # Check if it's a timeout error
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return "I'm taking too long to respond. Let's try a different approach. Could you ask me something else or rephrase your question?"
            
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
        # Clean up any empty messages before returning history
        self._clean_empty_messages()
        return self.memory.chat_memory.messages

    def debug_summarization(self):
        """
        Force summarization to happen and debug the process.
        This can be called to explicitly test if summarization is working.
        
        Returns:
            dict: Debug information about the summarization process
        """
        # safe_print("\n" + "=" * 80)
        # safe_print("DEBUGGING SUMMARIZATION PROCESS")
        # safe_print("=" * 80)
        
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
            
            # safe_print(f"Current summary length: {len(results['summary_before'])}")
            # safe_print(f"Current buffer size: {results['buffer_size_before']}")
            
            # Add a dummy message to force summarization
            dummy_message = "This is a test message to trigger summarization. Let's discuss our progress on the project goals, particularly focusing on topic continuity and development. We need to make sure we maintain focus on the main topics we've been discussing." * 5
            # safe_print(f"Adding dummy message of length {len(dummy_message)}")
            
            # Add directly to memory
            self.memory.save_context(
                {"input": dummy_message}, 
                {"output": "I understand the importance of maintaining topic continuity and development in our conversation. Let's ensure we stay focused on our key goals while making progress in our discussion." * 3}
            )
            
            # Get updated state
            results['summary_after'] = self._safe_get_summary()
            results['buffer_size_after'] = len(self.memory.buffer) if hasattr(self.memory, 'buffer') else 0
            
            # safe_print(f"New summary length: {len(results['summary_after'])}")
            # safe_print(f"New buffer size: {results['buffer_size_after']}")
            
            # Check if summarization happened
            if results['summary_before'] != results['summary_after']:
                # safe_print("✅ SUMMARIZATION SUCCESSFUL - Summary changed!")
                results['success'] = True
            else:
                # safe_print("⚠️ No change in summary detected")
                pass
            
            # Log the attempt
            self._log_summary_update(results['summary_before'], results['summary_after'])
            
        except Exception as e:
            error_msg = str(e)
            # safe_print(f"❌ ERROR during summarization debug: {error_msg}")
            results['error'] = error_msg
        
        # safe_print("=" * 80)
        return results
        
    def generate_closing_summary(self):
        """
        Generate a final summary and action plan for the coaching session.
        
        Uses a dedicated LLM instance with the CLOSING_PROMPT to create
        a structured summary with actionable next steps based on the
        entire conversation history.
        
        Returns:
            str: The final summary and action plan
        """
        try:
            # Get the entire conversation history
            messages = self.get_conversation_history()
            
            # Format the conversation history into a readable string
            conversation_text = "Full conversation history:\n\n"
            for msg in messages:
                if msg.type == "human":
                    conversation_text += f"Client: {msg.content}\n\n"
                else:
                    conversation_text += f"Coach: {msg.content}\n\n"
            
            # Create a dedicated LLM instance for the closing summary
            closing_llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            # Create the closing chain with the explicitly formatted prompt
            # Note: CLOSING_PROMPT should be updated in config.py to handle full conversation history
            formatted_closing_prompt = CLOSING_PROMPT.format(conversation_history=conversation_text)
            # safe_print("Passing complete conversation history to closing prompt...")
            
            # Use direct LLM prediction instead of chain to ensure proper formatting
            final_message = closing_llm.predict(formatted_closing_prompt)
            
            # Log the final summary
            try:
                with open(os.path.join(self.log_dir, f"final_summary_{self.session_id}.txt"), "w", encoding="utf-8") as f:
                    f.write("FINAL SUMMARY AND ACTION PLAN\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(final_message)
            except Exception as log_error:
                # safe_print(f"Warning: Could not log final summary: {log_error}")
                pass
                
            return final_message
        except Exception as e:
            # safe_print(f"Error generating closing summary: {e}")
            return "I'm unable to generate a final summary at this time. Let's continue our conversation."

    def process_input_without_adding_to_memory(self, user_input, timeout_seconds=60):
        """
        Process user input that's already been added to memory.
        
        Similar to process_input but skips adding the input to memory again to avoid duplication.
        
        Args:
            user_input (str): The user's text input that's already been added to memory
            timeout_seconds (int): Maximum time in seconds to wait for a response
            
        Returns:
            str: The AI's response text
        """
        # Step 1: Check if the input is valid
        if not user_input:
            return "I couldn't hear you clearly. Could you please repeat that?"
        
        try:
            # Track the start time for timeout purposes
            start_time = time.time()
            
            # Clean up any duplicates or empty messages before processing
            self._remove_duplicate_messages()
            self._clean_empty_messages()
            
            # Update the conversation prompt with current conversation_rounds
            updated_prompt = self.prompt_template(self.conversation_rounds)
            self.conversation.prompt = updated_prompt
            
            # Get the current summary before processing - with error handling
            old_summary = self._safe_get_summary()

            # Step 2: Use the conversation chain's LLM to generate a response with timeout
            try:
                # Use the LLM directly with the conversation's prompt
                if hasattr(self.llm, 'request_timeout'):
                    original_timeout = self.llm.request_timeout
                    self.llm.request_timeout = timeout_seconds
                    
                    # Get the current conversation history
                    chat_history = self.memory.chat_memory.messages
                    
                    # Check for and remove duplicated messages (if the user input is already in memory twice)
                    self._remove_duplicate_messages()
                    
                    # Get updated chat history after removing duplicates
                    chat_history = self.memory.chat_memory.messages
                    
                    # Create input values for the prompt without including user_input again
                    # This is the key difference - we don't pass the user_input separately
                    # since it's already in the chat history
                    input_values = {"input": "", "chat_history": chat_history}
                    
                    # Get the prompt with history
                    prompt_value = self.conversation.prompt.invoke(input_values)
                    
                    # Get the response directly from the LLM
                    response = self.llm.invoke(prompt_value.messages).content
                    
                    # Only add the AI's response to memory
                    self.memory.chat_memory.add_ai_message(response)
                    
                    # Trigger summarization if needed
                    if hasattr(self.memory, 'buffer') and len(self.memory.buffer) > self.memory.max_token_limit:
                        # Force summarization
                        # print("Triggering manual summarization due to buffer size")
                        buffer_content = self.memory.buffer
                        summary = self.memory.summarize(buffer_content)
                        if summary:
                            old_summary = self._safe_get_summary() 
                            # Update the summary
                            self.memory.moving_summary_buffer = summary
                            # Clear the buffer after summarization
                            self.memory.buffer = []
                            # Log the update
                            self._log_summary_update(old_summary, summary)
                    
                    # Restore original timeout
                    self.llm.request_timeout = original_timeout
                else:
                    # If no timeout support, use the same approach without timeout handling
                    # Check for and remove duplicated messages
                    self._remove_duplicate_messages()
                    
                    # Get the current conversation history after duplicate removal
                    chat_history = self.memory.chat_memory.messages
                    
                    # Use empty input since the user input is already in chat history
                    input_values = {"input": "", "chat_history": chat_history}
                    prompt_value = self.conversation.prompt.invoke(input_values)
                    response = self.llm.invoke(prompt_value.messages).content
                    
                    # Only add the AI response to memory
                    self.memory.chat_memory.add_ai_message(response)
                    
                    # Trigger summarization if needed
                    if hasattr(self.memory, 'buffer') and len(self.memory.buffer) > self.memory.max_token_limit:
                        # Force summarization
                        # print("Triggering manual summarization due to buffer size")
                        buffer_content = self.memory.buffer
                        summary = self.memory.summarize(buffer_content)
                        if summary:
                            old_summary = self._safe_get_summary()
                            self.memory.moving_summary_buffer = summary
                            self.memory.buffer = []
                            self._log_summary_update(old_summary, summary)
                
                # Track and log response time
                elapsed_time = time.time() - start_time
                # print(f"Response generated in {elapsed_time:.2f} seconds")
                
                # Clean up any empty messages that might have been introduced
                self._clean_empty_messages()
                
            except Exception as timeout_error:
                elapsed_time = time.time() - start_time
                # print(f"API call failed after {elapsed_time:.2f} seconds: {timeout_error}")
                
                # Try a fallback approach - simpler and more reliable
                try:
                    # Let the user know we're trying again
                    # print("Attempting fallback response generation...")
                    
                    # Use a simpler prompt with the same model but direct call
                    formatted_fallback_prompt = FALLBACK_PROMPT.format(user_input=user_input)
                    fallback_response = self.llm.predict(formatted_fallback_prompt)
                    
                    # Only add the AI's response to memory (input already added)
                    self.memory.chat_memory.add_ai_message(fallback_response)
                    
                    # Clean up any empty messages that might have been introduced
                    self._clean_empty_messages()
                    
                    # Increment conversation round counter even when using fallback
                    self.conversation_rounds += 1
                    # print(f"Conversation round incremented to {self.conversation_rounds} (via fallback in without_adding)")
                    
                    return fallback_response
                except Exception as fallback_error:
                    print(f"Fallback approach also failed: {fallback_error}")
                    raise timeout_error  # Re-raise the original error
            
            # Check if summary has changed and log if it has - with error handling
            try:
                new_summary = self._safe_get_summary()
                if old_summary != new_summary:
                    self._log_summary_update(old_summary, new_summary)
            except Exception as e:
                print(f"Warning: Error during summary update check: {e}")
                self.summarization_failed = True
            
            # After getting a response, log the exchange
            self._log_exchange(user_input, response)
            
            # Increment conversation round counter after successful completion
            self.conversation_rounds += 1
            # print(f"Conversation round incremented to {self.conversation_rounds} (via without_adding)")
            
            # Step 3: Return the response
            return response
        except Exception as e:
            # Handle any errors that might occur during processing
            error_msg = str(e)
            print(f"Error in conversation processing: {error_msg}")
            
            # Check if it's a timeout error
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return "I'm taking too long to respond. Let's try a different approach. Could you ask me something else or rephrase your question?"
            
            return "I'm having trouble processing that request. Let's try again."
            
    def _remove_duplicate_messages(self):
        """Remove any duplicate messages from chat memory."""
        messages = self.memory.chat_memory.messages
        i = len(messages) - 1
        
        # Skip if fewer than 2 messages
        if i < 1:
            return
            
        while i > 0:  # Start from the end, comparing each message with the previous
            current = messages[i]
            previous = messages[i-1]
            
            if (current.type == previous.type and 
                current.content == previous.content):
                # Found duplicate - remove the current (later) message
                # print(f"Removing duplicate message: [{current.type}] {current.content[:50]}...")
                messages.pop(i)
            i -= 1 
            
    def _clean_empty_messages(self):
        """Remove any empty messages from chat memory."""
        messages = self.memory.chat_memory.messages
        cleaned = False
        
        # Iterate through messages and remove empty ones
        i = len(messages) - 1
        while i >= 0:
            message = messages[i]
            if message.content == "":
                # print(f"Removing empty {message.type} message from memory")
                messages.pop(i)
                cleaned = True
            i -= 1
            
        return cleaned

    def add_user_message_to_memory(self, user_input):
        """
        Add a user message to memory properly, ensuring both chat_memory and buffer are updated.
        This preserves ConversationSummaryBufferMemory functionality.
        
        Args:
            user_input (str): The user's message to add
        """
        # Clean up any existing duplicates and empty messages first
        self._remove_duplicate_messages()
        self._clean_empty_messages()
        
        # Use the memory's proper channels to add the message
        # This ensures the buffer is updated correctly for summarization
        self.memory.save_context({"input": user_input}, {"output": ""})
        
        # Now remove the empty AI message we just added as a side effect
        if len(self.memory.chat_memory.messages) > 0 and self.memory.chat_memory.messages[-1].content == "":
            self.memory.chat_memory.messages.pop()
            
        # Final cleanup of any empty messages
        self._clean_empty_messages()
            
        # print(f"Added user message to memory: '{user_input[:50]}...'")
        
        # Debug buffer state
        if hasattr(self.memory, 'buffer'):
            # print(f"Buffer size after adding: {len(self.memory.buffer)}")
            pass
            
    def add_ai_message_to_memory(self, ai_message):
        """
        Add an AI message to memory properly, ensuring both chat_memory and buffer are updated.
        This preserves ConversationSummaryBufferMemory functionality.
        
        Args:
            ai_message (str): The AI's message to add
        """
        # Clean up any existing duplicates and empty messages first
        self._remove_duplicate_messages()
        self._clean_empty_messages()
        
        # For ConversationSummaryBufferMemory, we need to add the message to the buffer as well
        # We use an empty user input as we're just adding the AI response
        self.memory.save_context({"input": ""}, {"output": ai_message})
        
        # Clean up any empty messages that might have been introduced
        self._clean_empty_messages()
        
        # print(f"Added AI message to memory: '{ai_message[:50]}...'")
        
        # Debug buffer state
        if hasattr(self.memory, 'buffer'):
            # print(f"Buffer size after adding: {len(self.memory.buffer)}")
            pass
            
    def process_input_with_existing_message(self, user_input, timeout_seconds=60):
        """
        Process user input that's already been added to memory correctly.
        
        Args:
            user_input (str): The user's text input that's already been added to memory
            timeout_seconds (int): Maximum time in seconds to wait for a response
            
        Returns:
            str: The AI's response text
        """
        # Step 1: Check if the input is valid
        if not user_input:
            return "I couldn't hear you clearly. Could you please repeat that?"
        
        try:
            # Track the start time for timeout purposes
            start_time = time.time()
            
            # Remove any duplicates and empty messages that might exist in memory
            self._remove_duplicate_messages()
            self._clean_empty_messages()
            
            # Update the conversation prompt with current conversation_rounds
            updated_prompt = self.prompt_template(self.conversation_rounds)
            self.conversation.prompt = updated_prompt
            
            # Step 2: Get a response using the conversation chain
            try:
                # Set timeout if supported
                if hasattr(self.llm, 'request_timeout'):
                    original_timeout = self.llm.request_timeout
                    self.llm.request_timeout = timeout_seconds
                
                # Get the response using the conversation chain's LLM
                # We create a dummy empty message, so the chain doesn't add the input again
                # But we use the conversation predict method to properly handle memory
                response = self.conversation.predict(input="")
                
                # Clean up any empty messages immediately
                self._clean_empty_messages()
                
                # Restore timeout if needed
                if hasattr(self.llm, 'request_timeout'):
                    self.llm.request_timeout = original_timeout
                
                # Track and log response time
                elapsed_time = time.time() - start_time
                # print(f"Response generated in {elapsed_time:.2f} seconds")
                
            except Exception as timeout_error:
                elapsed_time = time.time() - start_time
                # print(f"API call failed after {elapsed_time:.2f} seconds: {timeout_error}")
                
                # Try a fallback approach
                try:
                    print("Attempting fallback response generation...")
                    formatted_fallback_prompt = FALLBACK_PROMPT.format(user_input=user_input)
                    fallback_response = self.llm.predict(formatted_fallback_prompt)
                    
                    # Manually add the response to memory
                    self.memory.chat_memory.add_ai_message(fallback_response)
                    
                    # Cleanup after adding the message
                    self._clean_empty_messages()
                    
                    # Increment conversation round counter even when using fallback
                    self.conversation_rounds += 1
                    # print(f"Conversation round incremented to {self.conversation_rounds} (via fallback in existing_message)")
                    
                    return fallback_response
                except Exception as fallback_error:
                    print(f"Fallback approach also failed: {fallback_error}")
                    raise timeout_error
            
            # After getting a response, log the exchange
            self._log_exchange(user_input, response)
            
            # Increment conversation round counter after successful completion
            self.conversation_rounds += 1
            # print(f"Conversation round incremented to {self.conversation_rounds} (via existing_message)")
            
            # Step 3: Return the response
            return response
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error in conversation processing: {error_msg}")
            
            if "timeout" in error_msg.lower():
                return "I'm taking too long to respond. Let's try a different approach."
                
            return "I'm having trouble processing that request. Let's try again." 

    def debug_messages(self):
        """
        Debug the messages in the conversation memory to ensure there are no empty messages.
        This method checks for and removes any empty messages, and reports on the state of the conversation.
        
        Returns:
            dict: Information about the conversation state
        """
        # Clean up first
        cleaned = self._clean_empty_messages()
        
        # Get the cleaned messages
        messages = self.memory.chat_memory.messages
        
        # Check for any remaining empty messages
        empty_messages = [i for i, msg in enumerate(messages) if msg.content == ""]
        
        # Count messages by type
        human_messages = sum(1 for msg in messages if msg.type == "human")
        ai_messages = sum(1 for msg in messages if msg.type == "ai")
        
        # Check for alternating pattern (should be human, ai, human, ai...)
        alternating = True
        for i in range(1, len(messages)):
            if messages[i].type == messages[i-1].type:
                alternating = False
                break
                
        # Prepare report
        report = {
            "total_messages": len(messages),
            "human_messages": human_messages,
            "ai_messages": ai_messages,
            "empty_messages_found": len(empty_messages) > 0,
            "empty_message_indices": empty_messages,
            "alternating_pattern": alternating,
            "cleaned_performed": cleaned,
            "first_message_type": messages[0].type if messages else None,
            "last_message_type": messages[-1].type if messages else None
        }
        
        # print("\nCONVERSATION MEMORY DEBUG:")
        # for key, value in report.items():
        #     print(f"  {key}: {value}")
        # print("")
        
        return report 