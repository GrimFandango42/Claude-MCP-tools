import os
import subprocess
import sys
import time

def start_api_server():
    """Start the FastAPI server in a separate process"""
    print("Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    # Give the server time to start
    time.sleep(2)
    return api_process

def start_streamlit_ui():
    """Start the Streamlit UI in a separate process"""
    print("Starting Streamlit UI...")
    ui_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/ui/streamlit_app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return ui_process

def main():
    # Set environment variables
    os.environ["API_URL"] = os.getenv("API_URL", "http://localhost:8000/api")
    
    # Start API server
    api_process = start_api_server()
    
    try:
        # Start Streamlit UI
        ui_process = start_streamlit_ui()
        
        print("\nClaude Desktop Bridge is running!")
        print("API server: http://localhost:8000")
        print("Streamlit UI: http://localhost:8501")
        print("\nPress Ctrl+C to stop all services.")
        
        # Keep the script running
        ui_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up processes
        if 'api_process' in locals():
            api_process.terminate()
        if 'ui_process' in locals():
            ui_process.terminate()
        
        print("Claude Desktop Bridge has been stopped.")

if __name__ == "__main__":
    main()
