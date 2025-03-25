"""
Script to extract the cl100k_base encoding file from tiktoken packages.
This ensures we can properly include it in our PyInstaller build.
"""

import os
import site
import shutil
import tiktoken
import glob
from pathlib import Path
import importlib.resources
import sys

def extract_cl100k_encoding():
    """Extract the cl100k_base encoding file to the current directory."""
    # Determine if we're run from build_scripts directory or root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    is_in_build_scripts = os.path.basename(script_dir) == 'build_scripts'
    
    # Set the target directory (where to save the encoding files)
    # If we're in build_scripts, use that directory, otherwise use current directory
    target_dir = script_dir
    
    # Try to create encoding first to force it to be downloaded/generated
    encoding = None
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        print(f"Successfully loaded cl100k_base encoding with {len(encoding._mergeable_ranks)} tokens")
    except Exception as e:
        print(f"Warning: Failed to load cl100k_base encoding: {e}")
    
    # Find all potential locations for the encoding file
    tiktoken_dir = os.path.dirname(tiktoken.__file__)
    site_packages = site.getsitepackages()[0]
    
    # Get more paths from sys.path
    additional_paths = [path for path in sys.path if 'site-packages' in path or 'dist-packages' in path]
    
    # Look for tiktoken_ext in all potential site-packages locations
    tiktoken_ext_paths = []
    for path in [site_packages] + additional_paths:
        ext_path = os.path.join(path, "tiktoken_ext")
        if os.path.exists(ext_path):
            tiktoken_ext_paths.append(ext_path)
            # Also add openai_public subdirectory if it exists
            openai_public = os.path.join(ext_path, "openai_public")
            if os.path.exists(openai_public):
                tiktoken_ext_paths.append(openai_public)
    
    # Combine all search paths
    search_paths = [tiktoken_dir] + tiktoken_ext_paths
    print(f"Searching in these paths:")
    for path in search_paths:
        print(f"  - {path}")
    
    # List to store found encoding files
    found_encodings = []
    
    # Search for cl100k_base.tiktoken files
    for path in search_paths:
        if os.path.exists(path):
            pattern = os.path.join(path, "*cl100k*")
            found_files = glob.glob(pattern)
            found_encodings.extend(found_files)
            
            if found_files:
                print(f"Found cl100k files in {path}:")
                for file in found_files:
                    print(f"  - {os.path.basename(file)}")
    
    # If no files found, try to manually create the encoding files
    if not found_encodings and encoding is not None:
        print("No encoding files found, manually creating them.")
        try:
            # Create tiktoken_ext directory in the target directory
            tiktoken_ext_dir = os.path.join(target_dir, "tiktoken_ext")
            if not os.path.exists(tiktoken_ext_dir):
                os.makedirs(tiktoken_ext_dir)
                print(f"Created directory: {tiktoken_ext_dir}")
            
            # Save the encoding to files
            cl100k_file = os.path.join(target_dir, "cl100k_base.tiktoken")
            print(f"Saving encoding to {cl100k_file}")
            with open(cl100k_file, "wb") as f:
                # Write a simple header to identify as tiktoken file
                f.write(b"tiktoken encoding file for cl100k_base\n")
                # Write the tokenizer mapping
                for token, rank in encoding._mergeable_ranks.items():
                    f.write(token + b" " + str(rank).encode() + b"\n")
            
            # Copy to tiktoken_ext as well
            ext_file = os.path.join(tiktoken_ext_dir, "cl100k_base.tiktoken")
            shutil.copy2(cl100k_file, ext_file)
            
            # Add files to found_encodings
            found_encodings.append(cl100k_file)
            return True
        except Exception as e:
            print(f"Error creating encoding file: {e}")
            return False
    
    # Copy all found encoding files to target directory
    for src_file in found_encodings:
        filename = os.path.basename(src_file)
        dest_file = os.path.join(target_dir, filename)
        shutil.copy2(src_file, dest_file)
        print(f"Copied {filename} to {target_dir}")
    
    # Check if we found any encoding files
    if not found_encodings:
        print("ERROR: No cl100k_base encoding files found!")
        return False
    
    # Create tiktoken_ext directory if needed
    tiktoken_ext_dir = os.path.join(target_dir, "tiktoken_ext")
    if not os.path.exists(tiktoken_ext_dir):
        os.makedirs(tiktoken_ext_dir)
        print(f"Created directory: {tiktoken_ext_dir}")
    
    # Create tiktoken_ext/openai_public directory if needed
    openai_public_dir = os.path.join(tiktoken_ext_dir, "openai_public")
    if not os.path.exists(openai_public_dir):
        os.makedirs(openai_public_dir)
        print(f"Created directory: {openai_public_dir}")
    
    # Copy encodings to tiktoken_ext and tiktoken_ext/openai_public directories
    for src_file in found_encodings:
        filename = os.path.basename(src_file)
        dest_file = os.path.join(tiktoken_ext_dir, filename)
        shutil.copy2(src_file, dest_file)
        print(f"Copied {filename} to {tiktoken_ext_dir}")
        
        # Also copy to openai_public
        dest_file = os.path.join(openai_public_dir, filename)
        shutil.copy2(src_file, dest_file)
        print(f"Copied {filename} to {openai_public_dir}")
    
    return True

if __name__ == "__main__":
    print("Extracting cl100k_base encoding file...")
    success = extract_cl100k_encoding()
    if success:
        print("Extraction completed successfully!")
    else:
        print("Extraction failed!") 