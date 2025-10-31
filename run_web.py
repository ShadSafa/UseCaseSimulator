#!/usr/bin/env python3
"""
Use Case Simulator - Web UI Launcher
Run this script to start the web-based interface.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_ui.app import create_app

def main():
    """Main entry point for the web application."""
    print("Starting Use Case Simulator Web UI...")
    print("=" * 50)
    print("A business simulation game for learning strategic decision making")
    print("=" * 50)
    print()

    # Create Flask app
    app = create_app('development')

    # Print startup information
    print("Web Interface: http://localhost:5000")
    print("Analytics Dashboard: http://localhost:5000/dashboard")
    print("New Game: http://localhost:5000/new-game")
    print()
    print("Controls:")
    print("  - Ctrl+C to stop the server")
    print("  - Open browser to http://localhost:5000")
    print()

    try:
        # Start the development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Use Case Simulator Web UI...")
        print("Thank you for playing!")
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()