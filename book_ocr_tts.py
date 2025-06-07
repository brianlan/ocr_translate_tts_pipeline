#!/usr/bin/env python3
"""
DEPRECATION NOTICE:
This file has been refactored into a modular architecture.
Please use the new refactored version: book_ocr_tts_refactored.py

The new architecture provides:
- Better separation of concerns
- Improved testability
- Cleaner code organization
- Enhanced maintainability

For backward compatibility, this file will redirect to the new implementation.
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    # Show deprecation notice
    print("⚠️  DEPRECATION NOTICE: This script has been refactored.")
    print("🔄 Redirecting to the new modular implementation...")
    print("📝 Please consider using 'book_ocr_tts_refactored.py' directly in the future.\n")
    
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(script_dir, "main.py")
    
    # Execute main.py with the same arguments
    cmd = [sys.executable, main_py_path] + sys.argv[1:]
    exit_code = subprocess.run(cmd).returncode
    sys.exit(exit_code)