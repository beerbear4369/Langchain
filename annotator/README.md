# RLHF Annotator

This directory contains the RLHF (Reinforcement Learning from Human Feedback) Annotator application and related files.

## Contents

- `rlhf_annotator.py` - Main application script
- `resource_path.py` - Helper module for resource path management
- `build_rlhf_annotator.bat` - Build script for creating the executable
- `RLHF_Annotator.spec` - PyInstaller specification file
- `create_distribution.bat` - Script for creating a distribution package
- `rlhf_annotations_*.json` - Example annotation files
- `checkpoints/` - Directory for saving and loading annotation checkpoints
- `rlhf_exports/` - Directory for exporting annotation data
- `RLHF_Annotator_Distribution/` - Distribution package
- `RLHF_Annotator_Distribution.zip` - Zipped distribution package

## Usage

1. Run `rlhf_annotator.py` directly for development
2. Use `build_rlhf_annotator.bat` to build the standalone executable
3. Use `create_distribution.bat` to create a distribution package

## Building the Executable

To build the RLHF Annotator executable:

1. Ensure PyInstaller is installed (`pip install pyinstaller`)
2. Run the build script: `build_rlhf_annotator.bat`
3. The executable will be created in the `dist` folder 