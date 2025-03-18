@echo off
echo Creating AI Coaching Tools distribution package...

rem Directory for distribution
set DIST_DIR=AI_Coaching_Tools

rem Remove previous distribution if exists
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%

rem Create distribution directory structure
mkdir %DIST_DIR%
mkdir %DIST_DIR%\conversation_logs
mkdir %DIST_DIR%\checkpoints
mkdir %DIST_DIR%\rlhf_exports

rem Copy executables to distribution directory
copy dist\RLHF_Annotator.exe %DIST_DIR%\
copy dist\Coaching_Assistant.exe %DIST_DIR%\

rem Copy sample data if available
if exist conversation_logs\*.* copy conversation_logs\*.* %DIST_DIR%\conversation_logs\

rem Create a sample conversation log if none exists
if not exist conversation_logs\*.* (
    echo Creating sample conversation log...
    echo {"role": "system", "content": "You are a helpful assistant."} > %DIST_DIR%\conversation_logs\sample_conversation.json
    echo {"role": "user", "content": "Hello, can you help me with a programming question?"} >> %DIST_DIR%\conversation_logs\sample_conversation.json
    echo {"role": "assistant", "content": "Of course! I'd be happy to help with your programming question. What would you like to know?"} >> %DIST_DIR%\conversation_logs\sample_conversation.json
)

rem Create a detailed README file
echo Creating detailed README...
(
echo # AI Coaching Tools
echo ==================
echo.
echo This package contains two applications for AI coaching and feedback:
echo.
echo ## 1. Coaching Assistant
echo.
echo The Coaching Assistant is an AI-powered tool that helps generate conversation dialogs.
echo.
echo **Usage:**
echo 1. Double-click `Coaching_Assistant.exe` to launch the application
echo 2. Interact with the AI coach to generate conversations
echo 3. Your conversations will be saved in the `conversation_logs` folder
echo.
echo ## 2. RLHF Annotator
echo.
echo The RLHF Annotator allows you to annotate conversation logs for Reinforcement Learning from Human Feedback.
echo.
echo **Usage:**
echo 1. First, use the Coaching Assistant to generate conversations
echo 2. After you have conversation logs, launch `RLHF_Annotator.exe`
echo 3. Click "Open Log File" to select a conversation log from the `conversation_logs` folder
echo 4. Navigate through conversations using the Previous/Next buttons
echo 5. Rate each assistant response as:
echo    - Yes (Good Response)
echo    - Neutral (Acceptable)
echo    - No (Needs Improvement) - Provide a better alternative when selecting this
echo 6. Click "Export Data" to save your annotations to the `rlhf_exports` folder
echo.
echo ## Complete Workflow
echo.
echo 1. Generate conversations using the Coaching Assistant
echo 2. Annotate those conversations with the RLHF Annotator
echo 3. Use the exported annotations for training and improving AI models
echo.
echo Created on %date% at %time%
) > %DIST_DIR%\README.md

rem Create a ZIP file of the distribution
echo Creating ZIP archive...
powershell Compress-Archive -Path %DIST_DIR% -DestinationPath %DIST_DIR%.zip -Force

echo.
echo Distribution package created successfully!
echo The package is available in the %DIST_DIR% folder and as %DIST_DIR%.zip
echo.

pause 