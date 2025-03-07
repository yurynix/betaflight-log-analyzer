#!/usr/bin/env python3
"""
Simple test script to verify the refactored package
"""
import sys
import os
from betaflight_log_analyzer.main import main

if __name__ == "__main__":
    # If no arguments are provided, show usage
    if len(sys.argv) == 1:
        print("Usage: python test_analyzer.py /path/to/your/LOG00001.BFL")
        sys.exit(1)
    
    # Pass the command line arguments to the main function
    sys.argv[0] = "betaflight-log-analyzer"  # Replace script name for better help text
    main() 