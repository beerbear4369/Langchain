@echo off
echo Creating README file for AI Coaching Tools...

rem Directory for the README
set DIST_DIR=AI_Coaching_Tools

rem Create the README file
echo # AI Coaching Tools > %DIST_DIR%\README.md
echo ================== >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo This package contains two applications for AI coaching and feedback: >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo ## 1. Coaching Assistant >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo The Coaching Assistant is an AI-powered tool that helps generate conversation dialogs. >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo **Usage:** >> %DIST_DIR%\README.md
echo 1. Double-click `Coaching_Assistant.exe` to launch the application >> %DIST_DIR%\README.md
echo 2. Interact with the AI coach to generate conversations >> %DIST_DIR%\README.md
echo 3. Your conversations will be saved in the `conversation_logs` folder >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo ## 2. RLHF Annotator >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo The RLHF Annotator allows you to annotate conversation logs for Reinforcement Learning from Human Feedback. >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo **Usage:** >> %DIST_DIR%\README.md
echo 1. First, use the Coaching Assistant to generate conversations >> %DIST_DIR%\README.md
echo 2. After you have conversation logs, launch `RLHF_Annotator.exe` >> %DIST_DIR%\README.md
echo 3. Click "Open Log File" to select a conversation log from the `conversation_logs` folder >> %DIST_DIR%\README.md
echo 4. Navigate through conversations using the Previous/Next buttons >> %DIST_DIR%\README.md
echo 5. Rate each assistant response as: >> %DIST_DIR%\README.md
echo    - Yes (Good Response) >> %DIST_DIR%\README.md
echo    - Neutral (Acceptable) >> %DIST_DIR%\README.md
echo    - No (Needs Improvement) - Provide a better alternative when selecting this >> %DIST_DIR%\README.md
echo 6. Click "Export Data" to save your annotations to the `rlhf_exports` folder >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo ## Complete Workflow >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo 1. Generate conversations using the Coaching Assistant >> %DIST_DIR%\README.md
echo 2. Annotate those conversations with the RLHF Annotator >> %DIST_DIR%\README.md
echo 3. Use the exported annotations for training and improving AI models >> %DIST_DIR%\README.md
echo. >> %DIST_DIR%\README.md
echo Created on %date% at %time% >> %DIST_DIR%\README.md

echo README created successfully in %DIST_DIR% folder. 