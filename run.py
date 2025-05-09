#!/usr/bin/env python3
# FortiPass - Launcher Script

"""
Simple launcher script for FortiPass.
Run this script to start the FortiPass application.
"""

import sys
from fortipass.main import main

if __name__ == "__main__":
    sys.exit(main()) 