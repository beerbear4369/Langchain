"""
Fix for imports in PyInstaller frozen applications.
This module adds the application directory to sys.path to ensure 
local modules can be imported correctly.
"""
import os
import sys

def setup_import_paths():
    """
    Add the executable directory to Python's import path
    to fix issues with local module imports.
    """
    # Get the directory containing the executable
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        # Running as a normal Python script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # If running from build_scripts directory, go up one level
        if os.path.basename(base_dir) == 'build_scripts':
            base_dir = os.path.dirname(base_dir)
    
    # Add to path if not already there
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
        print(f"Added {base_dir} to Python path")
    
    return base_dir 