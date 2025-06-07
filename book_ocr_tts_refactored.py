#!/usr/bin/env python3
"""
Book OCR to TTS Pipeline - Refactored Version Entry Point

This is the new entry point for the refactored Book OCR to TTS Pipeline.
Simply executes the main.py module.
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(script_dir, "main.py")
    
    # Execute main.py with the same arguments
    cmd = [sys.executable, main_py_path] + sys.argv[1:]
    exit_code = subprocess.run(cmd).returncode
    sys.exit(exit_code)
