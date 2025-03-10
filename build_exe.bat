@echo off
echo Building Coaching Assistant executable...

:: Ensure we're in the virtual environment
call venv\Scripts\activate.bat

:: Clean up previous builds
echo Cleaning up previous builds...
rmdir /s /q build dist __pycache__ 2>nul

:: Show Python and package versions for debugging
echo Python environment information:
python --version
pip list | findstr "pyinstaller openai langchain pydantic"

:: Build the executable directly without a spec file first
echo Building executable...
pyinstaller --name="Coaching_Assistant" ^
    --onefile ^
    --add-data="config.json;." ^
    --add-data="icon.ico;." ^
    --hidden-import=langchain ^
    --hidden-import=langchain.memory ^
    --hidden-import=langchain.chains.conversation.base ^
    --hidden-import=langchain_openai ^
    --hidden-import=langchain.prompts ^
    --hidden-import=langchain_core ^
    --hidden-import=openai ^
    --hidden-import=pyaudio ^
    --hidden-import=sounddevice ^
    --hidden-import=soundfile ^
    --hidden-import=wave ^
    --hidden-import=tempfile ^
    --hidden-import=dotenv ^
    --hidden-import=python-dotenv ^
    --hidden-import=numpy ^
    --hidden-import=pydantic ^
    --hidden-import=pydantic_core ^
    --hidden-import=typing_extensions ^
    --icon=icon.ico ^
    main.py

:: Check if build succeeded
if exist "dist\Coaching_Assistant.exe" (
    echo Build successful! Executable created at dist\Coaching_Assistant.exe
) else (
    echo Build failed. Check the logs for errors.
)

echo Done.
pause