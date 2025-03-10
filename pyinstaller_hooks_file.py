from pathlib import Path 
import pydantic 
import sys 
# This will be used as a hook for PyInstaller to find pydantic modules 
def get_pydantic_paths(): 
    base_path = Path(pydantic.__file__).parent 
    files = [] 
    for p in base_path.rglob('*.py'): 
        files.append(str(p)) 
    return files 
if __name__ == "__main__": 
    print("\\n".join(get_pydantic_paths())) 
