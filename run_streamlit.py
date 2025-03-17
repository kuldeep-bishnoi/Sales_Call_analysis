import subprocess
import sys
import os
import warnings

# Suppress urllib3 warnings about OpenSSL
warnings.filterwarnings("ignore", category=Warning, module="urllib3")

def main():
    """Run the Streamlit frontend application"""
    streamlit_file = os.path.join("app", "frontend", "streamlit_app.py")
    
    if not os.path.exists(streamlit_file):
        print(f"Error: Streamlit app file not found at {streamlit_file}")
        return
    
    try:
        # Run the Streamlit application using python module invocation
        # This is more reliable than depending on streamlit being in PATH
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            streamlit_file,
            "--server.port", "8501",
            "--browser.serverAddress", "localhost",
            "--server.headless", "true"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit application: {e}")
    except KeyboardInterrupt:
        print("\nShutting down Streamlit application...")

if __name__ == "__main__":
    main()