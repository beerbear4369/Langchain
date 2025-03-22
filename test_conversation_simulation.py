from conversation import Conversation, safe_print
import time
import re

def simulate_conversation():
    print("Creating conversation instance...")
    conv = Conversation()
    
    # Decrease the token limit to force summarization sooner
    conv.memory.max_token_limit = 800
    
    # Real conversation messages from a founder discussing AI chatbot progress
    messages = [
        "Hello, I want to talk about my progress of building an AI chatbot.",
        "wow I would like to explore the you know like actually I'm not so sure about it",
        "I feel the progress. It's like when I zoom in, the whole day working on it, I feel it is fast, because the feedback is really in real time, so I can feel the progress. But I do feel that maybe I'm just rewinding the wheel, because sometimes it's like I'm not an expert in this, and I could be just making so many obvious mistakes, I don't know. It's like previously, the big jump from previous progress is that when I start to see the output of the code to the LLM, and I feel the format is somehow wrong. And just with identifying that issue, I can fix it. It will improve the performance quite a lot. And honestly saying, the effort before that could be stupid. We also tried many things, working with different models, and getting more data. So in that perspective, the progress is slow. For myself, it's like a learning journey. As far as I'm able to learn, I'm quite happy. I can feel the progress. But to the absolute scale, maybe it's actually progress quite slow.",
        "Okay, I would rate the progress of five, because I need to keep distracted from the other business. So it's not that fast, we haven't been able to build more team to work on it. The people I work with also do it like a set hassle, so once there is something more urgent, everyone will put this aside.",
        "I guess the fundamental reason is that we are doing this at part-time, so if you consider the progress versus the amount of energy and time you invest in, it's fast. But if you see the entire progress, I think it's slow. After one or two months, I started to think about this from last year, and I met my partner for the AI coaching assistant for more than a month, and from there to now, we haven't yet published the MVP, so it's not that fast, actually, if you consider it against a full-time team.",
        "Well, if I can work full-time on this, it will definitely be faster because I'll be fully indulged in it, and I won't get distracted. You know, it's like sometimes, being distracted, getting back to this topic, I cannot find the files. I forget where I put those information, and it's taken me a while to get back, you know. There's like scientifically results that if you're shifting from topic, you need to mentally reconstruct to go back to the, I don't know how to describe, the stage, okay? And having a full-time team working on it, of course, is even better, but it's like even me as a founder is working part-time on this, right? So how could I get a full-time team working on it unless I take the lead to really step out of my business, which I don't look easy as of now, because like next week I need to go to Vietnam to meet some customers as well. Yeah, so it's really like a sad hustle project now.",
        "I will rate it as 5 and you have asked this question already.",
        "Okay, that's a good question. I guess I would like to prioritize the AIChat project, the AIChatbot, because I'm really interested in doing it, but I'm saying this is much more uncertainty, right? I still need the cash flow, I still need money. So when there is a project from the other business, the construction business, I'll be more prioritized to doing that. But when there's no business, when there's basically a free time, the time that's available for me to decide on what to do, I'm actually fully dedicated to the AIChatbot. Right now, what I'm doing right now, yeah.",
        "I guess it's like 50-50 when in Singapore I have fully control of my time I do more on air transport but when I'm in Vietnam, when I'm on business trip, I'm mainly doing that business things yeah so I feel it's about 50-50 at the moment but sometimes the consulting business have a higher priority because that is earning cash right like AI business is more like interest and there's totally no cash flow at the moment it's just like a interest project so when there is a request from the main business, I will drop my progress for AI transport and doing the consulting business yeah so a good priority to that",
        "Well, that's a good question. Ideally, I just like to do one meeting on Monday and all the necessary things finish on Monday. Then the rest six days on the AI chatbot project. Yeah, that's the ideal way. Then it would be like six out of seven. If we convert it by percentage, how much is the percentage?",
        "Yeah, so around 85%.",
        "I don't understand the question. Can you expand it?",
        "If I'm able to work 85% of the time, I think it goes much faster and it's much better continuity. Like keep iterating, release new features, and I'll be more in the mood to talk to everyone, to get results, to move things faster. Like move things faster, I think it's like a motivation, it's like make you feel it's moving forward and you become more active, like it's like a positive feedback loop and make it even better because it feels good, you work more, you see progress, and because you see progress, you work even more, it's like a rewarding loop. And if you work less, if progress is slow, then you'll be lazy to work because you don't see the real progress and there's no feedback, so this is like a punishment.",
        "I don't understand",
        "I still don't understand, what would you mean, would you read, you mean to read my current progress and assume that I have spent 85% of the energy?",
        "If let's say the real physical progress is basically I, for example, I train three models these two days, right? If I spend 85% of the time, it would be too slow, I'm saying it would be too slow because basically I do only two days' work, it's like two days of work, diluting to maybe like six days, right? So it would be really slow.",
        "Correct. You're wrong. I guess it's like a scale from zero to ten, right? So currently I'm rating it as five, I would say if I can work full time, it would be seven or eight, because I still think it would be too slow, you know?",
        "I guess it is the commitment that I have to contribute to my construction business, like things that I have to work on."
    ]
    
    # Process each message and get responses
    print("\nSimulating conversation...\n")
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
    
    # Force a final summarization to make sure everything is processed
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
    
    print("\nSimulation completed!")

if __name__ == "__main__":
    simulate_conversation()