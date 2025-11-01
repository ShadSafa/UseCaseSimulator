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

    # Start the development server
    import os
    os.environ['FLASK_ENV'] = 'development'
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=False
    )

if __name__ == '__main__':
    main()