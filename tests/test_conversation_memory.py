"""
Test script for verifying the ConversationSummaryBufferMemory implementation.

This script:
1. Creates a Conversation instance
2. Simulates a lengthy conversation
3. Periodically checks the conversation summary status
4. Verifies that summarization is working correctly
"""

import sys
import os

# Add parent directory to path so we can import the conversation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation import Conversation, safe_print
import time

def main():
    """Run a test of the conversation memory system."""
    
    # Create a conversation instance
    safe_print("Initializing conversation...")
    conversation = Conversation()
    
    # List of test messages to simulate a conversation
    # These are designed to create enough content to trigger summarization
    test_messages = [
        "Hello, I'm feeling quite anxious about my startup. Can you help?",
        "I've been working on this tech startup for about 6 months now, and I'm not sure if we're making progress.",
        "We're building a platform for remote team collaboration, focused on mental health tracking.",
        "Our team consists of 5 people - 3 developers including myself, a designer, and a marketing person.",
        "We've secured some initial funding, about $200,000, but I'm worried it's not enough.",
        "The main challenge is that our user acquisition is slower than expected.",
        "We launched a beta version two months ago and only have about 100 active users.",
        "I'm not sleeping well, constantly thinking about what might go wrong.",
        "My co-founder and I are disagreeing about the direction - they want to pivot to a different market.",
        "I'm worried that I'm letting everyone down, including our investors.",
        "Some days I'm excited and motivated, but other days I feel completely overwhelmed.",
        "I've started having these moments of panic where I can't focus on coding at all.",
        "My family is supportive but they don't really understand the startup world.",
        "I used to enjoy hiking on weekends but haven't done that in months now.",
        "One of our developers is thinking about leaving for a more stable job.",
        "Our competitors just announced a new feature set that overlaps with our roadmap.",
        "I'm considering bringing on another co-founder but worry about diluting equity further.",
        "Sometimes I wonder if I should just quit and get a normal job again.",
        "The stress is affecting my relationships - I barely see my friends anymore.",
        "I've been thinking about talking to a therapist but haven't made time for it.",
        "Our runway is about 10 months at current burn rate, which keeps me up at night.",
        "I'm not sure if I should be transparent with the team about our financial situation.",
        "The board is expecting a growth update next month and I'm dreading it.",
        "I feel like I'm constantly context-switching between coding and management.",
        "Most days I work from 7am until midnight, but I'm not sure if it's productive time.",
        "I've gained weight and stopped exercising regularly since founding the company.",
        "Sometimes I wonder if our product is even solving a real problem.",
        "I'm worried about making payroll in a few months if we don't raise more money.",
        "The tech stack choices we made early on are causing scaling issues now.",
        "I can't remember the last time I took a full day off without checking email.",
    ]
    
    # Separator for readability
    separator = "\n" + "=" * 80 + "\n"
    
    # Initial state
    safe_print(f"{separator}INITIAL STATE")
    summary_info = conversation.get_conversation_summary()
    safe_print(f"Summary: {summary_info['summary']}")
    safe_print(f"Buffer length: {summary_info['buffer_length']}")
    safe_print(f"Total messages: {summary_info['total_messages']}")
    
    # Process each message with checks after certain points
    check_points = [5, 10, 15, 20, 25, 30]
    
    for i, message in enumerate(test_messages, 1):
        safe_print(f"\nProcessing message {i}/{len(test_messages)}: {message[:50]}...")
        
        # Process the message
        response = conversation.process_input(message)
        safe_print(f"Response: {response[:100]}...")
        
        # Pause briefly to simulate realistic timing
        time.sleep(0.5)
        
        # Check at predetermined points
        if i in check_points:
            safe_print(f"{separator}CHECK POINT: After {i} messages")
            summary_info = conversation.get_conversation_summary()
            safe_print(f"Summary: {summary_info['summary']}")
            safe_print(f"Buffer length: {summary_info['buffer_length']}")
            safe_print(f"Total messages: {summary_info['total_messages']}")
            safe_print(f"Summarization status: {summary_info['summarization_status']}")
            
            # If we have a summary, it indicates summarization is working
            if summary_info['summary']:
                safe_print("✅ Summarization is working correctly!")
            else:
                if i > 10:  # We should have a summary after 10+ messages
                    safe_print("❌ No summary generated yet - this might be an issue.")
                else:
                    safe_print("⚠️ No summary yet, but this is expected with few messages.")
            
            # Check for summarization failures
            if summary_info['summarization_status'] != 'ok':
                safe_print(f"⚠️ Summarization issue detected: {summary_info['summarization_status']}")
                
                # If in fallback mode, note this
                if hasattr(conversation, '_fallback_memory'):
                    safe_print("🔄 Using fallback memory mechanism")
    
    # Final state
    safe_print(f"{separator}FINAL STATE")
    summary_info = conversation.get_conversation_summary()
    safe_print(f"Summary: {summary_info['summary']}")
    safe_print(f"Buffer length: {summary_info['buffer_length']}")
    safe_print(f"Total messages: {summary_info['total_messages']}")
    safe_print(f"Summarization status: {summary_info['summarization_status']}")
    
    # Report on overall test results
    if summary_info['summarization_status'] == 'ok' and summary_info['summary']:
        safe_print("\n✅ TEST PASSED: Summarization is working correctly!")
    elif summary_info['summary'] and summary_info['summarization_status'] != 'ok':
        safe_print("\n⚠️ TEST PARTIALLY PASSED: Summarization working but with issues.")
    elif hasattr(conversation, '_fallback_memory'):
        safe_print("\n⚠️ TEST PARTIALLY PASSED: Using fallback memory mechanism.")
    else:
        safe_print("\n❌ TEST FAILED: Summarization not working properly.")
    
    # Check the logs
    safe_print(f"{separator}CHECKING LOGS")
    safe_print(f"Conversation log: {conversation.log_file}")
    safe_print(f"Summary log: {conversation.summary_log_file}")
    
    # Tell the user how to examine the logs
    safe_print(f"\nTo examine the logs, check the files in the 'conversation_logs' directory.")
    safe_print("The summary log will show when and how the conversation was summarized.")

if __name__ == "__main__":
    main() 