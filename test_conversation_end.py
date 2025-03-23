import time
from conversation import Conversation, safe_print
import os

def test_should_wrap_up():
    """Test the should_wrap_up logic by simulating a conversation with way forward keywords."""
    safe_print("\n=== Testing should_wrap_up detection ===")
    
    convo = Conversation()
    safe_print(f"Created new conversation instance with ID: {convo.session_id}")
    
    # Add sufficient messages to trigger the message count threshold
    safe_print("Adding 25 messages to the conversation history...")
    for i in range(25):
        if i % 2 == 0:
            convo.memory.chat_memory.add_user_message(f"Test user message {i}")
        else:
            # Add coach messages that gradually lead to a Way Forward stage
            if i > 15:
                convo.memory.chat_memory.add_ai_message(
                    f"Let's discuss next steps. For your way forward, I suggest taking action on the items we discussed. "
                    f"We should create an action plan with specific steps to implement these solutions."
                )
            else:
                convo.memory.chat_memory.add_ai_message(f"Test coach response {i}")
    
    # Get message count
    message_count = len(convo.get_conversation_history())
    safe_print(f"Conversation has {message_count} messages")
    
    # Get the progression analysis
    safe_print("Retrieving conversation progression analysis...")
    analysis = convo.analyze_conversation_progression()
    progression = analysis.get('progression_analysis', 'No analysis')
    
    # Print a truncated version of the progression analysis
    safe_print("Analysis preview (first 200 chars):")
    safe_print(progression[:200] + "..." if len(progression) > 200 else progression)
    
    # Check if wrap-up is suggested
    safe_print("Checking if should_wrap_up returns True...")
    should_end = convo.should_wrap_up()
    safe_print(f"should_wrap_up result: {should_end}")
    
    return {
        "message_count": message_count,
        "should_wrap_up": should_end,
        "has_analysis": len(progression) > 50
    }

def test_closing_summary():
    """Test that the closing summary generates appropriate content."""
    safe_print("\n=== Testing closing summary generation ===")
    
    convo = Conversation()
    safe_print(f"Created new conversation instance with ID: {convo.session_id}")
    
    # Simulate a coaching conversation about career development
    safe_print("Adding sample coaching conversation about career development...")
    convo.memory.chat_memory.add_user_message("I'm feeling stuck in my current job and want to make a change.")
    convo.memory.chat_memory.add_ai_message("I understand that feeling. What specifically makes you feel stuck?")
    convo.memory.chat_memory.add_user_message("I've been in the same role for 4 years with no growth opportunities.")
    convo.memory.chat_memory.add_ai_message("That's challenging. What kind of growth are you looking for?")
    convo.memory.chat_memory.add_user_message("I want to move into a leadership position but don't have the experience.")
    convo.memory.chat_memory.add_ai_message("What steps have you already taken to gain leadership experience?")
    convo.memory.chat_memory.add_user_message("I've asked for more responsibility but my manager says I need to wait.")
    convo.memory.chat_memory.add_ai_message(
        "I understand your frustration. Let's explore some options for developing leadership skills "
        "outside your current role. Have you considered volunteering for projects or community leadership?"
    )
    convo.memory.chat_memory.add_user_message(
        "That's a good idea. I could look for volunteer opportunities or maybe take some courses."
    )
    convo.memory.chat_memory.add_ai_message(
        "Excellent thinking. Taking initiative with courses and volunteering shows leadership qualities. "
        "What specific areas of leadership are you most interested in developing?"
    )
    
    # Force summarization to happen
    safe_print("Forcing summarization with debug method...")
    convo.debug_summarization()
    
    # Get current summary
    summary_data = convo.get_conversation_summary()
    summary = summary_data.get('summary', 'No summary available')
    safe_print(f"Current summary length: {len(summary)} characters")
    
    # Generate the closing summary
    safe_print("\nGenerating closing summary...")
    start_time = time.time()
    closing_summary = convo.generate_closing_summary()
    elapsed_time = time.time() - start_time
    safe_print(f"Summary generated in {elapsed_time:.2f} seconds")
    
    # Print a preview of the summary
    safe_print("\nClosing summary preview (first 300 chars):")
    safe_print(closing_summary[:300] + "..." if len(closing_summary) > 300 else closing_summary)
    
    # Check if the summary contains expected elements
    contains_action_steps = "step" in closing_summary.lower() or "action" in closing_summary.lower()
    contains_leadership = "leadership" in closing_summary.lower()
    
    # Verify the summary was saved to file
    log_dir = convo.log_dir
    summary_file = os.path.join(log_dir, f"final_summary_{convo.session_id}.txt")
    file_exists = os.path.exists(summary_file)
    safe_print(f"\nSummary file saved: {file_exists} - {summary_file}")
    
    return {
        "summary_length": len(closing_summary),
        "contains_action_steps": contains_action_steps,
        "contains_keywords": contains_leadership,
        "file_saved": file_exists,
        "generation_time": elapsed_time
    }

def test_end_to_end():
    """Simulates a complete conversation flow that should trigger wrap-up."""
    safe_print("\n=== Testing end-to-end conversation flow ===")
    
    convo = Conversation()
    safe_print(f"Created new conversation instance with ID: {convo.session_id}")
    
    # Add enough messages to exceed the threshold (26 messages)
    safe_print("Simulating a complete conversation with progression through T-GROW stages...")
    
    # Topic stage
    convo.memory.chat_memory.add_ai_message("Welcome to our coaching session. What would you like to discuss today?")
    convo.memory.chat_memory.add_user_message("I'd like to talk about improving my work-life balance.")
    
    # Goal stage
    convo.memory.chat_memory.add_ai_message("That's an important topic. What are your specific goals for work-life balance?")
    convo.memory.chat_memory.add_user_message("I want to reduce overtime hours and have more time for my family and hobbies.")
    convo.memory.chat_memory.add_ai_message("That's clear. By when would you like to achieve this balance?")
    convo.memory.chat_memory.add_user_message("Within the next two months ideally.")
    
    # Reality stage
    convo.memory.chat_memory.add_ai_message("Let's explore your current situation. How many hours are you typically working?")
    convo.memory.chat_memory.add_user_message("I'm working about 60 hours a week, including weekends sometimes.")
    convo.memory.chat_memory.add_ai_message("What's driving these long hours? Are there specific work demands or expectations?")
    convo.memory.chat_memory.add_user_message("Mostly tight deadlines and understaffing. I also have trouble saying no to requests.")
    
    # Options stage
    convo.memory.chat_memory.add_ai_message("What options do you see for reducing your hours while maintaining performance?")
    convo.memory.chat_memory.add_user_message("I could delegate more, set boundaries, and prioritize better.")
    convo.memory.chat_memory.add_ai_message("Good options. Which of these feels most impactful to start with?")
    convo.memory.chat_memory.add_user_message("Setting clear boundaries would make the biggest difference.")
    
    # Way Forward stage
    convo.memory.chat_memory.add_ai_message("Let's create an action plan for setting boundaries. What's your first step?")
    convo.memory.chat_memory.add_user_message("I'll start by blocking off non-work hours in my calendar and communicating my availability.")
    convo.memory.chat_memory.add_ai_message("Excellent. What support do you need to maintain these boundaries?")
    convo.memory.chat_memory.add_user_message("I need to practice saying no respectfully and maybe discuss workload with my manager.")
    
    # Additional Way Forward messages to ensure detection
    convo.memory.chat_memory.add_ai_message(
        "That sounds like a solid plan. Let's summarize the way forward: "
        "1. Block off non-work hours in your calendar "
        "2. Communicate your availability to colleagues "
        "3. Practice saying no respectfully "
        "4. Discuss workload management with your manager "
        "How committed do you feel to this plan?"
    )
    convo.memory.chat_memory.add_user_message("I'm very committed. These changes are important for my wellbeing.")
    convo.memory.chat_memory.add_ai_message(
        "I appreciate your commitment. What will be your measure of success for these changes?"
    )
    convo.memory.chat_memory.add_user_message("Reducing my weekly hours to 45 or less and having weekends free.")
    
    # Add additional exchanges to ensure we reach the 25 message threshold
    convo.memory.chat_memory.add_ai_message(
        "That's an excellent metric for success. How will you track your progress towards this goal?"
    )
    convo.memory.chat_memory.add_user_message("I'll keep a log of my hours each week and review it every Sunday.")
    convo.memory.chat_memory.add_ai_message(
        "Perfect. That regular check-in will help you stay accountable. Is there anyone who can support you in maintaining these boundaries?"
    )
    convo.memory.chat_memory.add_user_message("My spouse can help remind me when I'm working too much and encourage me to disconnect.")
    
    # Force summarization
    safe_print("Triggering summarization...")
    convo.debug_summarization()
    
    # Check if should_wrap_up detects the completion
    safe_print("Checking if conversation should wrap up...")
    should_end = convo.should_wrap_up()
    safe_print(f"should_wrap_up result: {should_end}")
    
    # If it should end, generate closing summary
    if should_end:
        safe_print("Generating closing summary...")
        closing_summary = convo.generate_closing_summary()
        safe_print("Closing summary preview (first 200 chars):")
        safe_print(closing_summary[:200] + "..." if len(closing_summary) > 200 else closing_summary)
    
    return {
        "message_count": len(convo.get_conversation_history()),
        "should_wrap_up": should_end,
        "has_way_forward": should_end  # If should_end is True, it detected Way Forward content
    }

if __name__ == "__main__":
    safe_print("===== Testing Conversation End Implementation =====\n")
    
    # Test wrap-up detection
    wrap_up_results = test_should_wrap_up()
    
    # Test closing summary generation
    summary_results = test_closing_summary()
    
    # Test end-to-end flow
    e2e_results = test_end_to_end()
    
    # Print overall results
    safe_print("\n===== Test Results =====")
    safe_print(f"1. Wrap-up detection test:")
    safe_print(f"   - Message count: {wrap_up_results['message_count']} (expected ≥25)")
    safe_print(f"   - Analysis generated: {wrap_up_results['has_analysis']}")
    safe_print(f"   - should_wrap_up returned: {wrap_up_results['should_wrap_up']}")
    
    safe_print(f"\n2. Closing summary test:")
    safe_print(f"   - Summary length: {summary_results['summary_length']} characters")
    safe_print(f"   - Contains action steps: {summary_results['contains_action_steps']}")
    safe_print(f"   - Contains expected keywords: {summary_results['contains_keywords']}")
    safe_print(f"   - Summary file saved: {summary_results['file_saved']}")
    safe_print(f"   - Generation time: {summary_results['generation_time']:.2f} seconds")
    
    safe_print(f"\n3. End-to-end test:")
    safe_print(f"   - Message count: {e2e_results['message_count']} (expected ≥25)")
    safe_print(f"   - should_wrap_up detected Way Forward: {e2e_results['should_wrap_up']}")
    
    # Overall success assessment
    wrap_up_success = wrap_up_results['should_wrap_up'] or wrap_up_results['message_count'] < 25
    summary_success = summary_results['summary_length'] > 100 and summary_results['contains_action_steps']
    e2e_success = e2e_results['should_wrap_up']
    
    safe_print("\n===== Overall Assessment =====")
    safe_print(f"Wrap-up detection: {'PASS' if wrap_up_success else 'FAIL'}")
    safe_print(f"Closing summary: {'PASS' if summary_success else 'FAIL'}")
    safe_print(f"End-to-end flow: {'PASS' if e2e_success else 'FAIL'}")
    safe_print(f"Overall: {'PASS' if (wrap_up_success and summary_success and e2e_success) else 'PARTIAL PASS' if any([wrap_up_success, summary_success, e2e_success]) else 'FAIL'}") 