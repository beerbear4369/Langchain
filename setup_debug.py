import sys
import importlib.util
from pathlib import Path
import pydantic
import langchain
import langchain_openai
import openai

# Print module information
def print_module_info(module_name, module):
    print(f"\n--- {module_name} Module Info ---")
    print(f"Module path: {module.__file__}")
    print(f"Module version: {getattr(module, '__version__', 'Unknown')}")
    
    # Print submodule directory
    if hasattr(module, '__path__'):
        module_dir = Path(module.__file__).parent
        print(f"Submodules in {module_dir}:")
        for item in module_dir.glob('*'):
            if item.is_dir() and not item.name.startswith('__'):
                print(f"  - Directory: {item.name}")
            elif item.is_file() and item.suffix == '.py' and not item.name.startswith('__'):
                print(f"  - File: {item.name}")
    
    # Check for specific modules
    if module_name == 'pydantic':
        check_import('pydantic.deprecated.decorator')
        if hasattr(pydantic, 'deprecated'):
            print(f"pydantic.deprecated exists and is at {pydantic.deprecated}")
            print(f"pydantic.deprecated contents: {dir(pydantic.deprecated)}")

# Try importing a module and print result
def check_import(module_name):
    try:
        module = importlib.import_module(module_name)
        print(f"Successfully imported {module_name}: {module.__file__}")
        return True
    except ImportError as e:
        print(f"Failed to import {module_name}: {e}")
        return False

# Main information
print("\n=== Python Environment ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Sys.path:")
for path in sys.path:
    print(f"  - {path}")

# Module info
print_module_info('pydantic', pydantic)
print_module_info('langchain', langchain)
print_module_info('langchain_openai', langchain_openai)
print_module_info('openai', openai)

# Try importing directly
print("\n=== Direct Import Tests ===")
check_import('pydantic.deprecated')
check_import('pydantic.deprecated.decorator') 