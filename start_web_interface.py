"""
Launch script for AI Workflow Orchestrator Web Interface

This script starts the web application and opens it in the default browser.
Run this file to launch the complete web-based AI content creation system.
"""

import sys
import os
import time
import webbrowser
import threading

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def open_browser():
    """Open the web application in the default browser after a delay."""
    time.sleep(2)  # Wait for Flask to start
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to launch the web application."""
    print("🚀 Starting AI Workflow Orchestrator Web Interface")
    print("=" * 60)
    
    try:
        # Import and run the Flask app
        from frontend.app import app, socketio, initialize_workflow_manager
        
        print("📋 Initializing workflow manager...")
        initialize_workflow_manager()
        
        print("🌐 Starting web server...")
        print("📍 Application will be available at: http://localhost:5000")
        print("🔧 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Open browser in a separate thread
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the Flask-SocketIO server
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Workflow Orchestrator...")
        print("Thank you for using our system!")
        
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that port 5000 is available")
        print("3. Verify the project structure is correct")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()