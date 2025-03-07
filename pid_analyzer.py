#!/usr/bin/env python3
"""
Legacy entry point for backward compatibility.
This script has been refactored into a proper Python package.
"""
import sys
from betaflight_log_analyzer.main import main

if __name__ == "__main__":
    print("Note: This script has been refactored. Consider using the new 'betaflight-log-analyzer' command.")
    sys.argv[0] = "betaflight-log-analyzer"  # Replace script name for better help text
    main() 