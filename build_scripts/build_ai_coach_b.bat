@echo off
echo Building AI coach B executable with tiktoken fix...

:: Since we're in the build_scripts directory, we need to build from the parent directory
cd ..

:: Ensure we're in the virtual environment
call venv\Scripts\activate.bat

:: Clean up previous builds
echo Cleaning up previous builds...
rmdir /s /q build dist __pycache__ 2>nul

:: Show Python and package versions for debugging
echo Python environment information:
python --version
pip list | findstr "pyinstaller openai langchain pydantic tiktoken"

:: Create hooks directory in the root if it doesn't exist
if not exist hooks mkdir hooks

:: Copy our tiktoken hook from build_scripts\hooks to the root hooks directory
copy build_scripts\hooks\hook-tiktoken.py hooks\ /Y

:: Run the extraction script to get cl100k_base encoding
echo Extracting cl100k_base encoding files...
python build_scripts\extract_cl100k.py

:: Build using the spec file
echo Building executable using AI_coach_B.spec...
pyinstaller build_scripts\AI_coach_B.spec

:: Create necessary directories in dist
if exist "dist\AI coach B.exe" (
    if not exist "dist\tiktoken" mkdir "dist\tiktoken"
    if not exist "dist\tiktoken_ext" mkdir "dist\tiktoken_ext"
    if not exist "dist\tiktoken_ext\openai_public" mkdir "dist\tiktoken_ext\openai_public"
    
    if exist build_scripts\cl100k_base*.tiktoken (
        echo Copying tiktoken files to dist directory...
        for %%f in (build_scripts\cl100k_base*.tiktoken) do (
            copy "%%f" "dist\" /Y
            copy "%%f" "dist\tiktoken\" /Y
            copy "%%f" "dist\tiktoken_ext\" /Y
            copy "%%f" "dist\tiktoken_ext\openai_public\" /Y
            echo Copied %%f to multiple locations in dist directory
        )
    )
)

:: Create a simple batch file to run the exe with Python path
if exist "dist\AI coach B.exe" (
    echo @echo off > "dist\run_ai_coach_b.bat"
    echo set PYTHONPATH=%%~dp0 >> "dist\run_ai_coach_b.bat"
    echo "AI coach B.exe" >> "dist\run_ai_coach_b.bat"
    echo Created run_ai_coach_b.bat in dist directory
)

:: Check if build succeeded
if exist "dist\AI coach B.exe" (
    echo Build successful! Executable created at dist\AI coach B.exe
) else (
    echo Build failed. Check the logs for errors.
)

echo Done.
pause 