#!/usr/bin/env python3
"""
Main entry point for UseCaseSimulator console application.
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.ui.console_ui import ConsoleUI


def main():
    """Main application entry point."""
    try:
        # Create and start the console UI
        ui = ConsoleUI()
        ui.start()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please check your installation and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()