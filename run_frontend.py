#!/usr/bin/env python
"""Quick launcher for the web frontend"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.app import app, socketio, initialize_workflow_manager

if __name__ == '__main__':
    print("🚀 Starting AI Content Orchestrator Web Interface")
    print("=" * 60)
    initialize_workflow_manager()
    print("🌐 Starting web server on http://localhost:5001")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 60)
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
