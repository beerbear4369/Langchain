@echo off
echo Building RLHF Annotator executable...

rem Kill any running instances of the app
echo Terminating any running instances...
taskkill /F /IM RLHF_Annotator.exe 2>nul
if %errorlevel% equ 0 (
    echo Application terminated successfully.
    rem Give Windows time to release file handles
    timeout /t 2 /nobreak > nul
) else (
    echo No running instances found.
)

rem Clean previous build artifacts
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

rem Ensure required directories exist
echo Ensuring required directories exist...
if not exist checkpoints mkdir checkpoints
if not exist conversation_logs mkdir conversation_logs
if not exist rlhf_exports mkdir rlhf_exports

rem Create executable with PyInstaller
echo Building executable with PyInstaller...
pyinstaller --name "RLHF_Annotator" ^
    --onefile ^
    --windowed ^
    --add-data "checkpoints;checkpoints" ^
    --add-data "conversation_logs;conversation_logs" ^
    --add-data "rlhf_exports;rlhf_exports" ^
    rlhf_annotator.py

if errorlevel 1 (
    echo Build failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo Build completed! The executable is in the dist folder.
echo.

rem Create a readme file in the dist folder
echo Creating distribution README...
echo RLHF Annotator > dist\README.txt
echo ================ >> dist\README.txt
echo. >> dist\README.txt
echo This executable is a standalone application for annotating conversation logs for RLHF training. >> dist\README.txt
echo. >> dist\README.txt
echo Instructions: >> dist\README.txt
echo 1. Double-click RLHF_Annotator.exe to launch the application >> dist\README.txt
echo 2. Use "Open Log File" to select a conversation log to annotate >> dist\README.txt
echo 3. Navigate through conversations and provide feedback >> dist\README.txt
echo 4. Use "Export Data" to save your annotations >> dist\README.txt
echo. >> dist\README.txt
echo Created on %date% at %time% >> dist\README.txt

echo.
echo Testing executable (starting in background)...
start "" "dist\RLHF_Annotator.exe"
echo If a window opened, the executable is working correctly.
echo.

pause 