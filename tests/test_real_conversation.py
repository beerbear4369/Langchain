"""
Test script for verifying the ConversationSummaryBufferMemory with real conversation data.

This script:
1. Creates a Conversation instance
2. Replays a real coaching conversation from logs
3. Periodically checks the conversation summary status
4. Verifies that summarization is working correctly with realistic content
"""

import sys
import os

# Add parent directory to path so we can import the conversation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation import Conversation, safe_print
import time

def main():
    """Run a test of the conversation memory system using real conversation data."""
    
    # Create a conversation instance
    safe_print("Initializing conversation...")
    conversation = Conversation()
    
    # Real conversation data extracted from logs
    real_conversation = [
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
        "I guess it is the commitment that I have to contribute to my construction business, like things that I have to work on.",
        "If I fully commit to the AI chatbot project, I will be really fast here, but there is uncertainty because I also don't know whether this can work or not, but it will be more agile and I can learn faster and probably spot the interesting things faster because AI project is basically competing with people on speed. So I actually have a concern if I move like a sad hassle and do it quite slow, I won't be able to win the game. So essentially there is a really low chance for us to succeed because we are slow. But if I totally don't commit to the other work, other business, it's quite dangerous. Like my team is also not in the same country with me, they feel this is a fake company and there is no support. Actually I already feel that because I'm away for six months because I just don't want to go to Vietnam to do that business. I don't like it at all. And I'm also afraid if I just let the team do everything, basically then they have too much power and information, then they can cheat me of money as well, and they know the entire P&L and they know how much percent they are earning, which is some information I want to hide from them. So it will become like I need to be in the loop to watch out to make sure the information is processed correctly and to also know that they are good, they are having some, then I need to watch out and manage them and they need to work hard because they need to drive the business. And I cannot risk don't have any income because I have a family to raise. In the end of the day, I also want to have enough cash to buy what I want, change a new car, renovate the house, go traveling where I like.",
        "Yeah, I think you're right. If say I have a passive cash flow, that's what I was thinking about, right? Turn that business into a passive cash flow generator. If I have sufficient cash flow, I don't need to do anything, then yeah, I'm just dedicated to what I'm interested in, like doing the AI chatbot.",
        "It will be really fast, because I will dedicate all my time to it, and I would say it's like 10, and it becomes 10.",
        "the difference is like from the fully commit version I still need to work on the business right, still need to drag some of my energy and time and also like man energy because when you do project there's risk you'll be worried that okay this project can earn money or will be a loss actually so this is the thing pull you back you will be tied to the project so so now I feel like small projects better because the risk is less whether it's success or not it doesn't really matter that much so it's the comfortable risk range but big project although you can earn a lot of money after close one but you need to really pay a lot of attention and energy to it because you afraid if you screw up you cannot get your money back you actually you lose a lot of money there is a become a disaster yeah so that is the reason right a complete passive income means I don't need to do anything like a fully commit to this I still need to do something and worry about some things so then difference between seven to ten",
        "Hmm, good question. I think a good incentive would be like the AI project really start to come true, right? Having a team also trying to do it and there is progress. For example, we have launched, if say we have launched a product and we will receive by the market and start getting cash flow and we think that, oh, this really gonna work. We could like even earn more, you know, we can even become a bigger company, the business can become bigger and in a better mode than the other business. If we can see those incentives, I think not only me, everyone will take this more serious and dedicate more time and energy to the AI project. It's like nature, right? So having a team, proper team, really focus on it, working on it and real good solid progress and good feedback from the market and we are winning and we are able to see the potential that we are making something really substantial and making something really loved by the user have a big potential, you know, become like a high-tech company. If we are able to sense that and feel that, yeah, then I will totally switch to that because that's the reason, right?",
        "Failed criteria, for example, we have some investment that they feel, okay, this team, this project is really good, they want to put energy into it. Second, so if say we have launched the app and there are users using it, love it, paying for it, this all showing it is working, right? And like if we have more team, teammate just come out and working on it day and night like crazy, it's also a sign of success, right? So right now, we are in the pathway to getting there, but we may get there, we may not get there. I don't know, there's uncertainty.",
        "The biggest uncertainty is that we don't know whether this direction is right or not. Like after I build it, I think I'm able to build a basic version of it, but I'm not sure will there be any user at all, and will they pay for it? From competitive analysis, I feel there should be some, but that is just like a small application, like a small toy, you know? But make this real substantial business have tens of thousands of users, right? I'm not sure if that can work, are we able to create something that people really need, and are we able to win the competition from the competitor? Because I think this idea is not really hard to think of. There's no moat, and no one can do that actually, so are we able to win over them? I don't know that.",
        "Yeah, I mean like, if say this can generate cash flow and enough cash flow, it means some things. Yeah. Like, for example, we sell advertisement or we sell user's data, but I don't like that model because I really want to benefit the user, not to use the user, you know. But I mean, as far as we can get cash flow from it, then, yeah, it means endorse the investment of time, right? And we should all switch to this to become, to make this become the main business.",
        "Well, I guess we provide a real good service to users, like good consultation, and our AI coach is able to help users solve their problems, you know. And users like the project, they really love it, they talk to it every day, and they are willing to pay for the usage. Maybe it's based on donation, you know, like they just think, oh, this is really so good, it helps me a lot, and just I want to donate. Another model we think of could be after people know this, they may feel, oh, actually coaching is really something previously not so accessible, but now I can access it with AI. And come on, I should talk to a real good guy that really knows this domain, and I can achieve much faster, I can become much better, and then we can refer them to the right people to make the right linkage, and just earn a little bit commission fee for that. I think that's a quite healthy model, yeah. Basically, my belief is that I will do this in a non-evil way, I don't want to create some rubbish, I don't want to become, because we need to have the cash flow, we need to have money, so we need to do something dirty and don't like, like steal users' time, that's toxic. I don't totally want to fall into that route, but controversially, generating cash flow is the most important sign that this is successful as well, so that's the dilemma, I guess.",
        "Oh, it's like, I don't know what you mean by difference, it's totally two different topics, but I genuinely feel that basically I want to earn clean cash, helping people and also earn a reasonable profit, that's the ideal way. Because I'm contributing, I'm creating something really good, I should get reward for it. It's just I don't want to fall into some case that because it is so bad, the competition is so bad, so people start to do dirty things.",
        "That's a good question, to me success project means number one it's generating a sustainable cash flow so it's self-sustained, people are able to earn money from it, second is creating value to the user, users are really happy with it. Yeah that's it.",
        "If I need to sacrifice one and only choose one, I will choose create value for the user because I believe in the end of the day, value, like I'm doing this because I want to create value, I want to help other people, do something meaningful, not to earn money, right? So I won't sacrifice the value creation for the purpose of getting revenue, it will become just like even worse in the foreign project, right? In foreign business, we are creating value for the customer, solving the issue, if that's a good match, yeah, and we are doing that. To put me back, sometimes I feel we are not able to solve the problem, our product is not good enough for that circumstance, but we still need to earn money to have a living, so I have to do it, even though it's not the best for the user. So I don't want to get anything like that for this AI startup, so I will prefer to create value for the user over the sustainable cash flow.",
        "You have asked this question just now, what is the answer?",
        "The missing piece is unable to generate enough cash flow for me to commit full-time on it.",
        "Number one, we launch it, we build it and launch it, and there's user happy with it, willing to pay for it. Number two, they pay enough to cover our cost, and we are able to earn some money from it. Number three, there are more serious teammates working on it together."
    ]
    
    # Separator for readability
    separator = "\n" + "=" * 80 + "\n"
    
    # Initial state
    safe_print(f"{separator}INITIAL STATE")
    summary_info = conversation.get_conversation_summary()
    safe_print(f"Summary: {summary_info['summary']}")
    safe_print(f"Buffer length: {summary_info['buffer_length']}")
    safe_print(f"Total messages: {summary_info['total_messages']}")
    safe_print(f"Summarization status: {summary_info['summarization_status']}")
    
    # Process each message with checks after certain points
    # Since this is a real conversation, let's check more frequently
    check_points = [5, 10, 15, 20, 25, 30]
    
    for i, message in enumerate(real_conversation, 1):
        safe_print(f"\nProcessing message {i}/{len(real_conversation)}: {message[:50]}...")
        
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
    
    # Explicitly check if the summary log exists and has content
    if os.path.exists(conversation.summary_log_file):
        try:
            with open(conversation.summary_log_file, 'r', encoding='utf-8') as f:
                summary_log_content = f.read()
                
            if summary_log_content:
                summary_log_size = len(summary_log_content)
                summary_updates = summary_log_content.count("=== Summary Update at ")
                safe_print(f"\n✅ SUCCESS: Summary log exists with {summary_updates} updates ({summary_log_size} bytes)")
                
                # Print a preview of the content
                safe_print("\nSummary log preview:")
                safe_print(summary_log_content[:500] + "..." if len(summary_log_content) > 500 else summary_log_content)
            else:
                safe_print("\n⚠️ WARNING: Summary log file exists but is empty!")
        except Exception as e:
            safe_print(f"\n⚠️ ERROR reading summary log: {e}")
    else:
        safe_print("\n❌ FAILURE: Summary log file doesn't exist!")
    
    # Look for flag files indicating summarization occurred
    flag_files = [f for f in os.listdir(conversation.log_dir) if f.startswith('summarization_occurred_')]
    if flag_files:
        safe_print(f"\n✅ Found {len(flag_files)} flag files indicating summarization occurred")
        for flag_file in flag_files:
            try:
                with open(os.path.join(conversation.log_dir, flag_file), 'r') as f:
                    safe_print(f"- {flag_file}: {f.read().strip()}")
            except Exception as e:
                safe_print(f"- {flag_file}: Error reading file - {e}")
    else:
        safe_print("\n⚠️ No flag files found - summarization may not have occurred")
    
    # Force summarization to debug it
    safe_print(f"{separator}FORCE SUMMARIZATION TEST")
    safe_print("Running explicit summarization test to verify functionality...")
    debug_results = conversation.debug_summarization()
    
    if debug_results['success']:
        safe_print("\n✅ FORCED SUMMARIZATION TEST PASSED!")
        if not flag_files:
            safe_print("Note: Normal conversation didn't trigger summarization, but forced test worked.")
            safe_print("This suggests your token limit might be too high for the test conversation.")
    else:
        safe_print("\n❌ FORCED SUMMARIZATION TEST FAILED!")
        if debug_results['error']:
            safe_print(f"Error: {debug_results['error']}")
        safe_print("Consider checking your LLM API key, model availability, and network connection.")
    
    # Tell the user how to examine the logs
    safe_print(f"\nTo examine the logs, check the files in the 'conversation_logs' directory.")
    safe_print("The summary log will show when and how the conversation was summarized.")

if __name__ == "__main__":
    main() 