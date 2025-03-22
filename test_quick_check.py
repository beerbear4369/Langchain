from conversation import Conversation, safe_print
import time
import re

def quick_check():
    print("Creating conversation instance...")
    conv = Conversation()
    
    # Decrease the token limit to force summarization sooner
    conv.memory.max_token_limit = 600  # Even smaller to ensure summarization happens
    
    # First few messages from the real conversation
    messages = [
        "Hello, I want to talk about my progress of building an AI chatbot.",
        "wow I would like to explore the you know like actually I'm not so sure about it",
        "I feel the progress. It's like when I zoom in, the whole day working on it, I feel it is fast, because the feedback is really in real time, so I can feel the progress. But I do feel that maybe I'm just rewinding the wheel, because sometimes it's like I'm not an expert in this, and I could be just making so many obvious mistakes, I don't know. It's like previously, the big jump from previous progress is that when I start to see the output of the code to the LLM, and I feel the format is somehow wrong. And just with identifying that issue, I can fix it. It will improve the performance quite a lot.",
        "Okay, I would rate the progress of five, because I need to keep distracted from the other business. So it's not that fast, we haven't been able to build more team to work on it. The people I work with also do it like a set hassle, so once there is something more urgent, everyone will put this aside.",
        "I guess the fundamental reason is that we are doing this at part-time, so if you consider the progress versus the amount of energy and time you invest in, it's fast."
    ]
    
    # Process each message and get responses
    print("\nProcessing messages...\n")
    for i, message in enumerate(messages):
        print(f"Message {i+1}: {message[:50]}..." if len(message) > 50 else f"Message {i+1}: {message}")
        
        # Process the message
        response = conv.process_input(message)
        
        # Print shortened response
        short_response = response[:100] + "..." if len(response) > 100 else response
        print(f"Response: {short_response}")
        
        # Check for summary updates after each exchange
        summary_info = conv.get_conversation_summary()
        print(f"Buffer length: {summary_info['buffer_length']}")
        print(f"Summary length: {len(summary_info['summary'])}")
        print("---")
        
        # Short pause between messages
        time.sleep(1)
    
    # Force a final summarization
    print("\nForcing final summarization...")
    conv.debug_summarization()
    
    # Get final conversation analysis
    print("\nFinal conversation analysis:")
    progression = conv.analyze_conversation_progression()
    
    print("\nFinal summary (raw):")
    print("=" * 80)
    print(progression['summary'])
    print("=" * 80)
    
    # Print formatted summary with XML tags
    print("\nFinal summary (formatted):")
    summary = progression['summary']
    
    # Define sections to look for
    sections = ['TOPIC', 'GOAL', 'REALITY', 'OPTIONS', 'WAY_FORWARD', 'PROGRESS']
    
    # Extract and print each section
    for section in sections:
        pattern = f"<{section}>(.*?)</{section}>"
        match = re.search(pattern, summary, re.DOTALL)
        if match:
            content = match.group(1).strip()
            print(f"\n{section}:")
            print("-" * 40)
            print(content)
    
    print("\nProgression analysis:")
    print("-" * 80)
    print(progression['progression_analysis'])
    print("-" * 80)
    
    print("\nQuick check completed!")

if __name__ == "__main__":
    quick_check() 