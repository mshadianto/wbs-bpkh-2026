"""
Pytest configuration
Sets up the Python path for tests
"""

import sys
from pathlib import Path

# IMPORTANT: Add src to Python path FIRST (index 0) to prioritize over root modules
src_path = Path(__file__).parent.parent / "src"
src_path_str = str(src_path)

# Remove if exists and re-add at position 0
if src_path_str in sys.path:
    sys.path.remove(src_path_str)
sys.path.insert(0, src_path_str)

# Set test environment BEFORE any imports
import os
os.environ['DB_MODE'] = 'sqlite'
os.environ['DB_PATH'] = ':memory:'
