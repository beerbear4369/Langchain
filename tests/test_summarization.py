"""
Script to directly test the summarization functionality.

This provides a simple, focused test of just the summarization mechanism.
"""

import sys
import os

# Add parent directory to path so we can import the conversation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation import Conversation, safe_print
import time

def main():
    """Test summarization functionality directly."""
    safe_print("Testing summarization functionality...")
    
    # Create a conversation instance
    conversation = Conversation()
    
    # Initial state
    summary_info = conversation.get_conversation_summary()
    safe_print(f"Initial summary: {summary_info['summary']}")
    safe_print(f"Initial buffer length: {summary_info['buffer_length']}")
    
    # Generate a series of long messages to force summarization
    safe_print("\nSending long messages to force summarization...")
    
    for i in range(1, 11):
        # Create a long message
        message = f"This is test message {i}. " * 50
        
        # Process the message
        safe_print(f"\nProcessing message {i}...")
        response = conversation.process_input(message)
        safe_print(f"Response received ({len(response)} chars)")
        
        # Get updated summary info
        summary_info = conversation.get_conversation_summary()
        safe_print(f"Summary length: {len(summary_info['summary'])}")
        safe_print(f"Buffer length: {summary_info['buffer_length']}")
        safe_print(f"Summarization status: {summary_info['summarization_status']}")
        
        # Pause briefly
        time.sleep(1)
    
    # Final check - force summarization
    safe_print("\n\nFinal check - explicitly testing summarization...")
    debug_results = conversation.debug_summarization()
    
    # Final report
    if debug_results['success'] or summary_info['summary']:
        safe_print("\n✅ SUMMARIZATION TEST PASSED!")
        safe_print(f"Final summary length: {len(summary_info['summary']) if summary_info['summary'] else 0}")
    else:
        safe_print("\n❌ SUMMARIZATION TEST FAILED!")
        safe_print("No summary was generated.")
    
    # Show log locations
    safe_print(f"\nSummary log file: {conversation.summary_log_file}")
    safe_print("Check this file to see the summarization details.")

if __name__ == "__main__":
    main() 