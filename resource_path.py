import os
import sys

def resource_path(relative_path):
    """
    Get the correct path to resources whether running as a script or in a PyInstaller bundle.
    
    Args:
        relative_path: The path relative to the script or executable
        
    Returns:
        The absolute path to the resource
    """
    # If we're frozen (PyInstaller), the path is relative to _MEIPASS
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # Otherwise, use the script's directory
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path) 