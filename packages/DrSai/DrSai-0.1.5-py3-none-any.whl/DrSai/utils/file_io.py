import os, sys
from pathlib import Path

def read_file(file_path):
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")
    with open(file_path, 'r') as f:
        content = f.read()
    return content
    

