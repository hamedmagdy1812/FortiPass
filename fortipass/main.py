#!/usr/bin/env python3
# FortiPass - Professional Password Strength Visualizer
# Main application entry point

import sys
from fortipass.ui.app import FortiPassApp

def main():
    """Main entry point for the FortiPass application."""
    app = FortiPassApp()
    app.run()

if __name__ == "__main__":
    sys.exit(main()) 