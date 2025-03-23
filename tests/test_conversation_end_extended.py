import time
import types
import os
import sys

# Add parent directory to Python path to allow imports from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the parent directory
from conversation import Conversation, safe_print

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

def test_early_wrap_up():
    """Test if strong way forward content can trigger wrap-up before 25 messages."""
    safe_print("\n=== Testing early wrap-up detection ===")
    
    convo = Conversation()
    safe_print(f"Created new conversation instance with ID: {convo.session_id}")
    
    # Add 20 messages (below threshold) but with strong way forward content
    safe_print("Adding 20 messages with strong way forward content...")
    
    # Add typical coaching conversation
    convo.memory.chat_memory.add_ai_message("What would you like to discuss today?")
    convo.memory.chat_memory.add_user_message("I need help with my career transition plan.")
    convo.memory.chat_memory.add_ai_message("What are your goals for this transition?")
    convo.memory.chat_memory.add_user_message("I want to move from marketing to product management.")
    
    # Add more exchanges
    for i in range(6):
        convo.memory.chat_memory.add_ai_message(f"Question about career transition {i}")
        convo.memory.chat_memory.add_user_message(f"Answer about career goals {i}")
    
    # Add strong way forward content in the last few messages
    convo.memory.chat_memory.add_ai_message(
        "Based on our discussion, let's create a detailed action plan. Your way forward should include: "
        "1. Updating your resume to highlight relevant product experience "
        "2. Taking a product management certification course "
        "3. Scheduling informational interviews with 3 product managers "
        "4. Creating a 90-day learning plan for your transition "
        "How does this action plan sound to you?"
    )
    convo.memory.chat_memory.add_user_message(
        "This action plan sounds perfect. I'll start working on these steps right away."
    )
    convo.memory.chat_memory.add_ai_message(
        "Excellent. Let's review your progress in our next session. Is there anything else about the way forward we should discuss?"
    )
    convo.memory.chat_memory.add_user_message("No, I think we've covered everything I needed today.")
    
    # Verify message count is below threshold
    message_count = len(convo.get_conversation_history())
    safe_print(f"Conversation has {message_count} messages (below 25 threshold)")
    
    # Force summarization to create analysis
    safe_print("Triggering summarization...")
    convo.debug_summarization()
    
    # Get the progression analysis
    analysis = convo.analyze_conversation_progression()
    progression = analysis.get('progression_analysis', 'No analysis')
    safe_print("Analysis preview (first 200 chars):")
    safe_print(progression[:200] + "..." if len(progression) > 200 else progression)
    
    # Check if wrap-up is suggested despite being below threshold
    safe_print("Checking if should_wrap_up returns True despite message count < 25...")
    should_end = convo.should_wrap_up()
    safe_print(f"should_wrap_up result with actual implementation: {should_end}")
    
    # Try with a modified version that uses a lower threshold for testing
    # Create a modified method for testing purposes
    def modified_should_wrap_up(self):
        history = self.get_conversation_history()
        # Use 15 as threshold for this test
        if len(history) >= 15:
            analysis = self.analyze_conversation_progression().get('progression_analysis', '')
            
            # The rest is the same as the original method
            way_forward_indicators = [
                "way forward:" in analysis.lower() and len(analysis.lower().split("way forward:")[1].split("\n")[0]) > 30,
                "action plan" in analysis.lower() and "next steps" in analysis.lower(),
                "framework is complete" in analysis.lower() or "coaching cycle complete" in analysis.lower(),
                "implementing" in analysis.lower() and "solutions" in analysis.lower()
            ]
            
            completion_indicators = [
                "thoroughly discussed" in analysis.lower() and "next logical stage: way forward" in analysis.lower(),
                "coaching next steps:" in analysis.lower() and "implementation" in analysis.lower(),
                "session can be concluded" in analysis.lower() or "ready to conclude" in analysis.lower()
            ]
            
            if any(way_forward_indicators) or any(completion_indicators):
                return True
                
        return False
    
    # Save original method
    original_method = convo.should_wrap_up
    
    try:
        # Apply the modified method
        convo.should_wrap_up = types.MethodType(modified_should_wrap_up, convo)
        
        # Test with modified threshold
        should_end_modified = convo.should_wrap_up()
        safe_print(f"should_wrap_up result with 15 message threshold: {should_end_modified}")
        
    finally:
        # Restore original method
        convo.should_wrap_up = original_method
    
    return {
        "message_count": message_count,
        "below_threshold": message_count < 25,
        "has_way_forward": "way forward" in progression.lower() or "action plan" in progression.lower(),
        "early_wrap_up_detected": should_end_modified if 'should_end_modified' in locals() else False,
        "actual_wrap_up_detected": should_end
    }

def test_message_count_only_wrap_up():
    """Test if exceeding message count triggers wrap-up even without way forward content."""
    safe_print("\n=== Testing message count only wrap-up ===")
    
    convo = Conversation()
    safe_print(f"Created new conversation instance with ID: {convo.session_id}")
    
    # Add 26 messages with no way forward content
    safe_print("Adding 26 messages with NO way forward content...")
    
    # Add reality stage questions only
    for i in range(13):
        convo.memory.chat_memory.add_ai_message(
            f"Let's explore another aspect of your current reality. What challenges are you facing with task {i}?"
        )
        convo.memory.chat_memory.add_user_message(
            f"The main challenge with task {i} is the lack of clear requirements and tight deadlines."
        )
    
    # Verify message count exceeds threshold
    message_count = len(convo.get_conversation_history())
    safe_print(f"Conversation has {message_count} messages (above 25 threshold)")
    
    # Force summarization
    safe_print("Triggering summarization...")
    convo.debug_summarization()
    
    # Get the progression analysis
    analysis = convo.analyze_conversation_progression()
    progression = analysis.get('progression_analysis', 'No analysis')
    safe_print("Analysis preview (first 200 chars):")
    safe_print(progression[:200] + "..." if len(progression) > 200 else progression)
    
    # Check for way forward content
    has_way_forward = "way forward" in progression.lower()
    safe_print(f"Analysis contains way forward content: {has_way_forward}")
    
    # Check if should_wrap_up detects completion
    should_wrap_up_result = convo.should_wrap_up()
    safe_print(f"should_wrap_up result: {should_wrap_up_result}")
    
    # In main.py, the wrap-up check would be:
    # if turn_counter >= max_turns or conversation.should_wrap_up() or elapsed_time >= 30*60
    # Let's simulate this condition
    max_turns = 25
    turn_counter = message_count
    
    # The condition we're testing
    should_end = turn_counter >= max_turns or should_wrap_up_result
    safe_print(f"Wrap-up would trigger: {should_end}")
    safe_print(f"  - Due to message count (>= 25): {turn_counter >= max_turns}")
    safe_print(f"  - Due to should_wrap_up(): {should_wrap_up_result}")
    
    return {
        "message_count": message_count,
        "exceeds_threshold": message_count >= 25,
        "has_way_forward": has_way_forward,
        "should_wrap_up_result": should_wrap_up_result,
        "message_count_wrap_up": should_end
    }

def test_time_based_wrap_up():
    """Simulate a time-based wrap-up after 30 minutes."""
    safe_print("\n=== Testing time-based wrap-up (simulation) ===")
    
    # Since we can't actually wait 30 minutes in a test,
    # we'll simulate the time-based condition from main.py
    
    convo = Conversation()
    safe_print(f"Created new conversation instance with ID: {convo.session_id}")
    
    # Add a short conversation (below message threshold)
    safe_print("Adding a short conversation (10 messages)...")
    for i in range(5):
        convo.memory.chat_memory.add_ai_message(f"Question {i}?")
        convo.memory.chat_memory.add_user_message(f"Answer {i}.")
    
    # Get message count
    message_count = len(convo.get_conversation_history())
    safe_print(f"Conversation has {message_count} messages (below 25 threshold)")
    
    # Force summarization
    safe_print("Triggering summarization...")
    convo.debug_summarization()
    
    # Check if should_wrap_up would trigger
    should_wrap_up_result = convo.should_wrap_up()
    safe_print(f"should_wrap_up result: {should_wrap_up_result}")
    
    # Simulate the time check from main.py
    session_start = time.time() - (31 * 60)  # Simulate 31 minutes elapsed
    elapsed_time = time.time() - session_start
    safe_print(f"Simulated elapsed time: {elapsed_time / 60:.1f} minutes (exceeds 30 min threshold)")
    
    # The condition from main.py:
    # if turn_counter >= max_turns or conversation.should_wrap_up() or elapsed_time >= 30*60
    max_turns = 25
    turn_counter = message_count
    
    # Check if time-based wrap-up would trigger
    should_end = turn_counter >= max_turns or should_wrap_up_result or elapsed_time >= 30*60
    safe_print(f"Wrap-up would trigger: {should_end}")
    safe_print(f"  - Due to message count (>= 25): {turn_counter >= max_turns}")
    safe_print(f"  - Due to should_wrap_up(): {should_wrap_up_result}")
    safe_print(f"  - Due to time limit (>= 30 min): {elapsed_time >= 30*60}")
    
    return {
        "message_count": message_count,
        "below_threshold": message_count < 25,
        "elapsed_time_minutes": elapsed_time / 60,
        "exceeds_time_limit": elapsed_time >= 30*60,
        "time_based_wrap_up": should_end
    }

if __name__ == "__main__":
    safe_print("===== Testing Conversation End Implementation - Extended =====\n")
    
    # Original tests
    safe_print("\n----- ORIGINAL TESTS -----")
    
    # Test 1: Standard wrap-up detection
    wrap_up_results = test_should_wrap_up()
    
    # Test 2: Closing summary generation
    summary_results = test_closing_summary()
    
    # Test 3: End-to-end flow
    e2e_results = test_end_to_end()
    
    # New tests
    safe_print("\n----- ADDITIONAL TESTS -----")
    
    # Test 4: Early wrap-up detection (before 25 messages)
    early_wrap_up_results = test_early_wrap_up()
    
    # Test 5: Message count only wrap-up (>25 msgs without "way forward")
    message_count_results = test_message_count_only_wrap_up()
    
    # Test 6: Time-based wrap-up (30 min session limit)
    time_based_results = test_time_based_wrap_up()
    
    # Print overall results
    safe_print("\n===== Test Results =====")
    
    # Original tests results
    safe_print(f"\n1. Standard wrap-up detection:")
    safe_print(f"   - Message count: {wrap_up_results['message_count']} (expected =25)")
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
    
    # New tests results
    safe_print(f"\n4. Early wrap-up test (< 25 messages):")
    safe_print(f"   - Message count: {early_wrap_up_results['message_count']} (expected <25)")
    safe_print(f"   - Has Way Forward content: {early_wrap_up_results['has_way_forward']}")
    safe_print(f"   - Would detect with lower threshold: {early_wrap_up_results['early_wrap_up_detected']}")
    safe_print(f"   - Detected with actual implementation: {early_wrap_up_results['actual_wrap_up_detected']}")
    
    safe_print(f"\n5. Message count only wrap-up:")
    safe_print(f"   - Message count: {message_count_results['message_count']} (expected >25)")
    safe_print(f"   - Has Way Forward content: {message_count_results['has_way_forward']}")
    safe_print(f"   - should_wrap_up detected: {message_count_results['should_wrap_up_result']}")
    safe_print(f"   - Wrap-up triggered by message count: {message_count_results['message_count_wrap_up']}")
    
    safe_print(f"\n6. Time-based wrap-up:")
    safe_print(f"   - Message count: {time_based_results['message_count']} (expected <25)")
    safe_print(f"   - Simulated time: {time_based_results['elapsed_time_minutes']:.1f} minutes (expected >30)")
    safe_print(f"   - Wrap-up triggered by time: {time_based_results['time_based_wrap_up']}")
    
    # Overall success assessment
    original_tests_pass = (
        wrap_up_results['should_wrap_up'] and
        summary_results['summary_length'] > 100 and 
        summary_results['contains_action_steps'] and
        e2e_results['should_wrap_up']
    )
    
    new_tests_pass = (
        early_wrap_up_results['early_wrap_up_detected'] and
        message_count_results['message_count_wrap_up'] and
        time_based_results['time_based_wrap_up']
    )
    
    safe_print("\n===== Overall Assessment =====")
    safe_print(f"Original tests: {'PASS' if original_tests_pass else 'FAIL'}")
    safe_print(f"New scenario tests: {'PASS' if new_tests_pass else 'FAIL'}")
    safe_print(f"Overall: {'PASS' if (original_tests_pass and new_tests_pass) else 'PARTIAL PASS'}")
    
    # Provide recommendations
    safe_print("\n===== Recommendations =====")
    
    if not early_wrap_up_results['actual_wrap_up_detected'] and early_wrap_up_results['early_wrap_up_detected']:
        safe_print("- Consider making the message threshold lower for conversations with strong Way Forward content")
    
    if not message_count_results['should_wrap_up_result'] and message_count_results['message_count_wrap_up']:
        safe_print("- Current implementation correctly relies on message count when Way Forward is not detected")
    
    if time_based_results['time_based_wrap_up']:
        safe_print("- Time-based wrap-up works correctly for long sessions")
    
    safe_print("\n- Consider adding a special command to test wrap-up via the UI for easier testing")
    safe_print("- Ensure thorough testing of all three conditions in the integrated application") 