"""
Helper script to run the Streamlit app with proper error handling
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_streamlit_installed():
    """Check if streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Install streamlit package"""
    print("Streamlit is not installed. Installing now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        return True
    except subprocess.CalledProcessError:
        print("Failed to install Streamlit. Please install it manually with: pip install streamlit")
        return False

def check_lmstudio_running():
    """Check if LM Studio server is running"""
    try:
        import requests
        response = requests.get("http://localhost:1234/", timeout=2)
        return True
    except:
        return False

def main():
    """Run the Streamlit app"""
    # Display banner
    print("\n" + "="*60)
    print("       🤖 AutoGen Coding Agent - Streamlit UI")
    print("="*60)
    
    # Check if streamlit is installed
    if not check_streamlit_installed():
        if not install_streamlit():
            input("Press Enter to exit...")
            return
    
    # Check if LM Studio is running
    if not check_lmstudio_running():
        print("\n⚠️ LM Studio server not detected at http://localhost:1234/")
        print("Make sure LM Studio is running with the server enabled before using the agent.")
        print("1. Open LM Studio")
        print("2. Go to the Server tab")
        print("3. Click 'Start Server'")
        print("\nThe Streamlit UI will launch anyway, but you'll need to start LM Studio")
        print("for the agent to work properly.")
    else:
        print("\n✅ LM Studio server detected! The agent is ready to use.")
    
    # Launch browser automatically after a short delay
    print("\nLaunching Streamlit UI in your default browser...")
    
    # Start streamlit in a new process
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Give streamlit time to start up before opening the browser
    sleep(2)
    webbrowser.open("http://localhost:8501")
    
    try:
        # Print streamlit output until process terminates
        for line in streamlit_process.stdout:
            if "You can now view your Streamlit app in your browser." in line:
                # Already opened browser so skip this line
                continue
            print(line, end="")
    except KeyboardInterrupt:
        print("\nShutting down Streamlit...")
        streamlit_process.terminate()
    
    print("\nThank you for using AutoGen Coding Agent!")

if __name__ == "__main__":
    main()
