# Build Scripts for AI Coach B

This folder contains all the necessary scripts to build the AI Coach B executable using PyInstaller.

## Files in this directory

- `build_ai_coach_b.bat` - The main build script that creates the executable
- `AI_coach_B.spec` - PyInstaller spec file with all configurations
- `extract_cl100k.py` - Helper script to extract tiktoken encoding files
- `hook-tiktoken.py` - PyInstaller hook for tiktoken library
- `cl100k_base.tiktoken` - Tiktoken encoding file (will be created during build)

## How to Build

1. Open a command prompt and navigate to this `build_scripts` directory
2. Run the build script:
   ```
   build_ai_coach_b.bat
   ```
3. The script will:
   - Activate the virtual environment
   - Clean up previous builds
   - Extract necessary encoding files
   - Run PyInstaller with the spec file
   - Copy encoding files to the distribution folder
   - Create a helper batch file for running the executable

4. When completed, the executable will be available in the `dist` directory at the project root

## Troubleshooting

If you encounter issues with tiktoken encodings:
- The build script includes fixes for the "Unknown encoding cl100k_base" error
- Encoding files are copied to multiple locations to ensure they can be found
- A run_ai_coach_b.bat file is created that sets PYTHONPATH to help locate resources

## Adding Features

When adding new features to the main application:
1. Update the main.py file with your new features
2. If you add new libraries, update the spec file to include them in the hiddenimports list
3. Run the build script again to create a new executable

## Creating a New Version

To create a new version with a different name:
1. Copy the AI_coach_B.spec file to a new file (e.g., AI_coach_C.spec)
2. Update the name parameter in the EXE section
3. Create a new build script based on build_ai_coach_b.bat 