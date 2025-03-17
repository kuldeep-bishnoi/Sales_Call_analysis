#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    return True

def create_directories():
    """Create required directories"""
    directories = [
        "data",
        "data/uploads",
        "data/transcripts",
        "data/temp",
        "data/results"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_env_file():
    """Set up the environment file"""
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("Created .env file from .env.example. Please edit it with your actual API keys and settings.")

def install_dependencies():
    """Install dependencies from requirements.txt"""
    if os.path.exists("requirements.txt"):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError:
            print("Error installing dependencies. Please try manually: pip install -r requirements.txt")
    else:
        print("Error: requirements.txt not found.")

def create_default_config():
    """Create default configuration for Streamlit"""
    streamlit_dir = ".streamlit"
    os.makedirs(streamlit_dir, exist_ok=True)
    
    config_file = os.path.join(streamlit_dir, "config.toml")
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write("""[theme]
primaryColor="#1E88E5"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F5F5F5"
textColor="#424242"
font="sans serif"

[server]
port = 8501
headless = true
""")
        print("Created default Streamlit configuration.")

def main():
    """Main setup function"""
    print("Setting up Sales Call Analysis System...")
    
    if not check_python_version():
        return
    
    create_directories()
    setup_env_file()
    install_dependencies()
    create_default_config()
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Make sure MongoDB is running")
    print("3. Start the API server: python main.py")
    print("4. Start the dashboard: python run_streamlit.py")

if __name__ == "__main__":
    main() 