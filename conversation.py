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
    CLOSING_PROMPT
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
            max_token_limit=3000,  # Increased to retain more context
            return_messages=True,
            prompt=custom_summary_template,
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
            safe_print(f"Warning: Could not log summary update: {e}")

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
        Determine if the session should be wrapped up based on conversation progression.
        Uses:
          - Total message count (e.g., > 25 messages)
          - Analysis of "Way Forward" content in the progression analysis
          - Detection of concluding statements or action plans
        Returns:
          bool: True if session should be wrapped up.
        """
        history = self.get_conversation_history()
        # Only check for wrap-up if we have enough conversation history
        if len(history) >= 25:
            analysis = self.analyze_conversation_progression().get('progression_analysis', '')
            
            # Check for meaningful "Way Forward" content
            way_forward_indicators = [
                # Look for "Way Forward:" followed by substantive content
                "way forward:" in analysis.lower() and len(analysis.lower().split("way forward:")[1].split("\n")[0]) > 30,
                # Look for action plans or next steps being described
                "action plan" in analysis.lower() and "next steps" in analysis.lower(),
                # Check if the coaching framework is described as complete
                "framework is complete" in analysis.lower() or "coaching cycle complete" in analysis.lower(),
                # Check for discussion about implementing solutions
                "implementing" in analysis.lower() and "solutions" in analysis.lower()
            ]
            
            # Check for completion indicators in the entire analysis
            completion_indicators = [
                "thoroughly discussed" in analysis.lower() and "next logical stage: way forward" in analysis.lower(),
                "coaching next steps:" in analysis.lower() and "implementation" in analysis.lower(),
                "session can be concluded" in analysis.lower() or "ready to conclude" in analysis.lower()
            ]
            
            # If we have either clear Way Forward content or completion indicators, suggest wrap-up
            if any(way_forward_indicators) or any(completion_indicators):
                return True
                
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
                
                # Track and log response time
                elapsed_time = time.time() - start_time
                safe_print(f"Response generated in {elapsed_time:.2f} seconds")
                
            except Exception as timeout_error:
                elapsed_time = time.time() - start_time
                safe_print(f"API call failed after {elapsed_time:.2f} seconds: {timeout_error}")
                
                # Try a fallback approach - simpler and more reliable
                try:
                    # Let the user know we're trying again
                    safe_print("Attempting fallback response generation...")
                    
                    # Use a simpler prompt with the same model but direct call
                    formatted_fallback_prompt = FALLBACK_PROMPT.format(user_input=user_input)
                    fallback_response = self.llm.predict(formatted_fallback_prompt)
                    
                    # Since we're bypassing the conversation chain, manually add to memory
                    self.memory.chat_memory.add_user_message(user_input)
                    self.memory.chat_memory.add_ai_message(fallback_response)
                    
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
            dummy_message = "This is a test message to trigger summarization. Let's discuss our progress on the project goals, particularly focusing on topic continuity and development. We need to make sure we maintain focus on the main topics we've been discussing." * 5
            safe_print(f"Adding dummy message of length {len(dummy_message)}")
            
            # Add directly to memory
            self.memory.save_context(
                {"input": dummy_message}, 
                {"output": "I understand the importance of maintaining topic continuity and development in our conversation. Let's ensure we stay focused on our key goals while making progress in our discussion." * 3}
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
        
    def generate_closing_summary(self):
        """
        Generate a final summary and action plan for the coaching session.
        
        Uses a dedicated LLM instance with the CLOSING_PROMPT to create
        a structured summary with actionable next steps based on the
        conversation history.
        
        Returns:
            str: The final summary and action plan
        """
        try:
            # Get the current conversation summary
            summary_data = self.get_conversation_summary()
            summary = summary_data.get('summary', 'No summary available.')
            
            # If summary is empty, create a basic one from the conversation history
            if not summary or summary == "":
                messages = self.get_conversation_history()
                # Format a basic summary from the last 10 messages
                recent_messages = messages[-min(10, len(messages)):]
                
                summary = "Recent conversation summary:\n\n"
                for msg in recent_messages:
                    if msg.type == "human":
                        summary += f"Client: {msg.content[:100]}...\n"
                    else:
                        summary += f"Coach: {msg.content[:100]}...\n"
                
                safe_print("No existing summary found, generated basic summary from recent messages.")
            
            # Create a dedicated LLM instance for the closing summary
            closing_llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            # Create the closing chain with the explicitly formatted prompt
            formatted_closing_prompt = CLOSING_PROMPT.format(summary=summary)
            safe_print(f"Passing summary to closing prompt (first 100 chars): {summary[:100]}...")
            
            # Use direct LLM prediction instead of chain to ensure proper formatting
            final_message = closing_llm.predict(formatted_closing_prompt)
            
            # Log the final summary
            try:
                with open(os.path.join(self.log_dir, f"final_summary_{self.session_id}.txt"), "w", encoding="utf-8") as f:
                    f.write("FINAL SUMMARY AND ACTION PLAN\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(final_message)
            except Exception as log_error:
                safe_print(f"Warning: Could not log final summary: {log_error}")
                
            return final_message
        except Exception as e:
            safe_print(f"Error generating closing summary: {e}")
            return "I'm unable to generate a final summary at this time. Let's continue our conversation." 