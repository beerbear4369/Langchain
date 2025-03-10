@echo off
echo Building Coaching Assistant executable (Fixed Version)...

:: Ensure we're in the virtual environment
call venv\Scripts\activate.bat

:: Clean up previous builds
echo Cleaning up previous builds...
rmdir /s /q build dist __pycache__ 2>nul

:: Show Python and package versions for debugging
echo Python environment information:
python --version
pip list | findstr "pyinstaller openai langchain pydantic"

:: Create a custom helper file to ensure pydantic modules are included
echo Creating PyInstaller helper file...
echo from pathlib import Path > pyinstaller_hooks_file.py
echo import pydantic >> pyinstaller_hooks_file.py
echo import sys >> pyinstaller_hooks_file.py
echo # This will be used as a hook for PyInstaller to find pydantic modules >> pyinstaller_hooks_file.py
echo def get_pydantic_paths(): >> pyinstaller_hooks_file.py
echo     base_path = Path(pydantic.__file__).parent >> pyinstaller_hooks_file.py
echo     files = [] >> pyinstaller_hooks_file.py
echo     for p in base_path.rglob('*.py'): >> pyinstaller_hooks_file.py
echo         files.append(str(p)) >> pyinstaller_hooks_file.py
echo     return files >> pyinstaller_hooks_file.py
echo if __name__ == "__main__": >> pyinstaller_hooks_file.py
echo     print("\\n".join(get_pydantic_paths())) >> pyinstaller_hooks_file.py

:: Generate list of pydantic modules to include
echo Generating list of pydantic files to include...
python pyinstaller_hooks_file.py > pydantic_files.txt

:: Build the executable with additional options for pydantic
echo Building executable with special handling for pydantic...
pyinstaller ^
    --name="Coaching_Assistant" ^
    --onefile ^
    --clean ^
    --add-data="config.json;." ^
    --add-data="icon.ico;." ^
    --collect-all pydantic ^
    --collect-all pydantic_core ^
    --collect-all langchain ^
    --collect-all langchain_core ^
    --collect-all langchain_openai ^
    --collect-all openai ^
    --collect-all typing_extensions ^
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
    --hidden-import=numpy ^
    --hidden-import=pydantic ^
    --hidden-import=pydantic.deprecated ^
    --hidden-import=pydantic.deprecated.decorator ^
    --hidden-import=pydantic_core ^
    --hidden-import=typing_extensions ^
    --hidden-import=json ^
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