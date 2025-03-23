import os
import sys
import re

# Add parent directory to Python path to allow imports from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_wrap_up_prompt_logic():
    """Test the wrap-up prompt logic in main.py"""
    
    # Path to main.py in parent directory
    main_py_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    
    # Read the content of main.py
    with open(main_py_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Check for the content-based wrap-up prompt
    content_based_prompt = "It looks like we've made good progress on your issue. Shall we wrap up today's session with a quick summary and an action plan? If yes, please say wrap up and summarize."
    has_content_prompt = content_based_prompt in main_content
    
    # Check for the time/count-based wrap-up prompt
    time_based_prompt = "I think we have covered a lot today and it is about the end of our session today. Would you like to wrap up our session with a final summary and action plan? If yes, please say wrap up and summarize."
    has_time_prompt = time_based_prompt in main_content
    
    # Check for the explicit commands list
    explicit_commands_pattern = r'explicit_commands\s*=\s*\[(.*?)\]'
    match = re.search(explicit_commands_pattern, main_content, re.DOTALL)
    explicit_commands_str = match.group(1) if match else ""
    
    has_wrap_up_cmd = '"wrap up"' in explicit_commands_str
    has_summarize_cmd = '"summarize"' in explicit_commands_str
    has_end_session_cmd = '"end session"' in explicit_commands_str
    
    # Check for affirmative and context keywords directly in the main.py content
    # This is more reliable than trying to extract the specific code block
    has_yes_check = 'yes" in confirmation_lower' in main_content
    has_yeah_check = 'yeah" in confirmation_lower' in main_content
    has_sure_check = 'sure" in confirmation_lower' in main_content
    
    has_summary_check = 'summary" in confirmation_lower' in main_content
    has_wrap_check = 'wrap" in confirmation_lower' in main_content 
    has_end_check = 'end" in confirmation_lower' in main_content
    
    # Check if the combined affirmative with context logic is present
    has_combined_check = 'affirmative_with_context = (' in main_content
    
    # Print results
    print("=== Testing Wrap-Up Prompt Logic ===")
    print(f"Content-based prompt present: {has_content_prompt}")
    print(f"Time/count-based prompt present: {has_time_prompt}")
    print("\nExplicit wrap-up commands:")
    print(f"- 'wrap up' command: {has_wrap_up_cmd}")
    print(f"- 'summarize' command: {has_summarize_cmd}")
    print(f"- 'end session' command: {has_end_session_cmd}")
    print("\nAffirmative with context checks:")
    print(f"- 'yes' check: {has_yes_check}")
    print(f"- 'yeah' check: {has_yeah_check}")
    print(f"- 'sure' check: {has_sure_check}")
    print(f"- 'summary' keyword check: {has_summary_check}")
    print(f"- 'wrap' keyword check: {has_wrap_check}")
    print(f"- 'end' keyword check: {has_end_check}")
    print(f"- Combined affirmative with context: {has_combined_check}")
    
    # Summary (updated to include all checks)
    tests_passed = sum([
        has_content_prompt, 
        has_time_prompt,
        has_wrap_up_cmd,
        has_summarize_cmd, 
        has_end_session_cmd,
        has_yes_check,
        has_yeah_check,
        has_sure_check,
        has_summary_check,
        has_wrap_check,
        has_end_check,
        has_combined_check
    ])
    
    total_tests = 12
    print(f"\nPassed {tests_passed}/{total_tests} tests")
    
    if tests_passed == total_tests:
        print("All tests PASSED! The wrap-up prompt logic has been correctly implemented.")
    else:
        print("Some tests FAILED. Please check the implementation of the wrap-up prompt logic.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    test_result = test_wrap_up_prompt_logic()
    print(f"\nTest result: {'PASS' if test_result else 'FAIL'}") 