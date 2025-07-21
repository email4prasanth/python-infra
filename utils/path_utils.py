# utils/path_utils.py
import sys
import os
from pathlib import Path

def setup_paths():
    """Add project root to Python path"""
    # Get the path to the current file
    current_file = Path(__file__).resolve()
    
    # Project root is two levels up from utils directory
    project_root = current_file.parent.parent
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))