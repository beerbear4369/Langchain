# AI Coaching Tools 
================== 
 
This package contains two applications for AI coaching and feedback: 
 
## 1. Coaching Assistant 
 
The Coaching Assistant is an AI-powered tool that helps generate conversation dialogs. 
 
**Usage:** 
1. Double-click `Coaching_Assistant.exe` to launch the application 
2. Interact with the AI coach to generate conversations 
3. Your conversations will be saved in the `conversation_logs` folder 
 
## 2. RLHF Annotator 
 
The RLHF Annotator allows you to annotate conversation logs for Reinforcement Learning from Human Feedback. 
 
**Usage:** 
1. First, use the Coaching Assistant to generate conversations 
2. After you have conversation logs, launch `RLHF_Annotator.exe` 
3. Click "Open Log File" to select a conversation log from the `conversation_logs` folder 
4. Navigate through conversations using the Previous/Next buttons 
5. Rate each assistant response as: 
   - Yes (Good Response) 
   - Neutral (Acceptable) 
   - No (Needs Improvement) - Provide a better alternative when selecting this 
6. Click "Export Data" to save your annotations to the `rlhf_exports` folder 
 
## Complete Workflow 
 
1. Generate conversations using the Coaching Assistant 
2. Annotate those conversations with the RLHF Annotator 
3. Use the exported annotations for training and improving AI models 
 
Created on Tue 11/03/2025 at  1:47:08.63 
