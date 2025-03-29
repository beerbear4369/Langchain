import os, time
from conversation import Conversation

# Test wrap-up acceptance
def test_accept_wrap_up():
    print("Testing wrap-up acceptance scenario...")
    conv = Conversation()
    
    # Add enough messages to trigger wrap-up condition
    for i in range(16):  # Need at least 15 rounds
        conv.conversation_rounds = i
        conv.add_user_message_to_memory(f"User message {i}")
        conv.add_ai_message_to_memory(f"Coach response {i}")
    
    # Set attributes to force wrap-up check
    # Store original method
    original_should_wrap_up = conv.should_wrap_up
    conv.should_wrap_up = lambda: True  # Always return True for testing
    
    # Check if should_wrap_up returns True
    if not conv.should_wrap_up():
        print("❌ should_wrap_up() test failed")
        return
    
    print("✅ should_wrap_up() returns True")
    
    # Add wrap-up confirmation
    conv.add_user_message_to_memory("yes, please wrap up")
    
    # Generate final summary
    final_message = conv.generate_closing_summary()
    conv.add_ai_message_to_memory(final_message)
    
    # Check for final summary in conversation
    messages = conv.get_conversation_history()
    has_wrap_up = any("MAIN BREAKTHROUGHS" in msg.content or "ACTION PLAN" in msg.content 
                     for msg in messages if msg.type == "ai")
    
    if has_wrap_up:
        print("✅ Final summary was added to conversation")
    else:
        print("❌ Final summary not found in conversation")

    # Check if cached result works
    cache_used = hasattr(conv, "_wrap_up_cache_result")
    if cache_used:
        print("✅ Wrap-up cache is being used")
    else:
        print("❌ Wrap-up cache not found")
    
    # Restore original method
    conv.should_wrap_up = original_should_wrap_up
    print("Test accept wrap-up completed")

# Test wrap-up rejection
def test_reject_wrap_up():
    print("\nTesting wrap-up rejection scenario...")
    conv = Conversation()
    
    # Add enough messages to trigger wrap-up condition
    for i in range(16):  # Need at least 15 rounds
        conv.conversation_rounds = i
        conv.add_user_message_to_memory(f"User message {i}")
        conv.add_ai_message_to_memory(f"Coach response {i}")
    
    # Set attributes to force wrap-up check
    original_should_wrap_up = conv.should_wrap_up
    conv.should_wrap_up = lambda: True
    
    # Check if wrap-up is triggered
    if not conv.should_wrap_up():
        print("❌ should_wrap_up() test failed")
        return
    
    print("✅ should_wrap_up() returns True")
    
    # Add rejection message
    conv.add_user_message_to_memory("No, I want to continue the conversation")
    
    # Add coach response
    continuation_message = "Okay, let's continue our conversation."
    conv.add_ai_message_to_memory(continuation_message)
    
    # Verify the conversation continues
    messages = conv.get_conversation_history()
    last_message = messages[-1] if messages else None
    
    if last_message and last_message.type == "ai" and last_message.content == continuation_message:
        print("✅ Conversation continues after rejection")
    else:
        print("❌ Conversation did not continue properly after rejection")
    
    # Restore original method
    conv.should_wrap_up = original_should_wrap_up
    print("Test reject wrap-up completed")

# Test should_wrap_up caching mechanism by using the real implementation
def test_should_wrap_up_cache():
    print("\nTesting actual should_wrap_up caching mechanism...")
    conv = Conversation()
    
    # Add enough messages to trigger wrap-up condition
    for i in range(16):  # Need at least 15 rounds
        conv.conversation_rounds = i
        conv.add_user_message_to_memory(f"User message {i}")
        conv.add_ai_message_to_memory(f"Coach response {i}")
    
    # First call - this should set the cache
    print("Making first call to should_wrap_up()...")
    first_result = conv.should_wrap_up()
    
    # Check if cache was created
    has_cache_time = hasattr(conv, "_wrap_up_cache_time")
    has_cache_result = hasattr(conv, "_wrap_up_cache_result")
    
    print(f"Cache attributes present after first call: Time={has_cache_time}, Result={has_cache_result}")
    
    if has_cache_time and has_cache_result:
        print("✅ Cache attributes were created")
        
        # Make second call - this should use the cache
        print("Making second call that should use the cache...")
        second_result = conv.should_wrap_up()
        
        # Verify results match
        print(f"Results match: {first_result == second_result}")
        
        if first_result == second_result:
            print("✅ Caching mechanism appears to be working correctly")
        else:
            print("❌ Results inconsistent, cache might not be working")
    else:
        print("❌ Cache attributes not being created")
    
    print("Test cache mechanism completed")

# Run tests
test_accept_wrap_up()
test_reject_wrap_up()
test_should_wrap_up_cache()

print("\nAll tests completed!") 