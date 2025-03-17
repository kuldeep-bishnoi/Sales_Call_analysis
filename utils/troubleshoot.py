#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import platform
import requests
import time

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    print(f"Checking Python version:")
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"   Current version: {current_version[0]}.{current_version[1]}")
        return False
    else:
        print(f"✅ Using Python {current_version[0]}.{current_version[1]}.{current_version[2]}")
    return True

def check_directories():
    """Check if required directories exist and are writable"""
    directories = [
        "data",
        "data/uploads",
        "data/transcripts",
        "data/temp",
        "data/results"
    ]
    
    print("\nChecking required directories:")
    missing_dirs = []
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"❌ Missing directory: {directory}")
            missing_dirs.append(directory)
        elif not os.access(directory, os.W_OK):
            print(f"❌ No write permission for directory: {directory}")
        else:
            print(f"✅ Directory {directory} exists and is writable")
    
    if missing_dirs:
        print("\nCreating missing directories...")
        for directory in missing_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"  Created directory: {directory}")

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\nChecking environment file:")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("  Created .env file from .env.example. Please edit it with your actual API keys and settings.")
        else:
            print("  Cannot create .env file: .env.example not found.")
        return
    
    print("✅ .env file exists")
    
    # Check for required variables
    required_vars = ["MONGODB_URL"]
    missing_vars = []
    
    with open(".env", "r") as f:
        env_content = f.read()
        
    for var in required_vars:
        if var + "=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
    else:
        print("✅ All required environment variables are present")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\nChecking dependencies:")
    
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "openai", "streamlit",
        "librosa", "numpy", "pandas", "scikit-learn", "pymongo",
        "plotly", "tqdm", "nltk"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nSome dependencies are missing. Install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        
        # Offer to install them
        if input("\nDo you want to install missing dependencies now? (y/n): ").lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("Dependencies installed.")

def check_mongodb():
    """Check if MongoDB is running"""
    print("\nChecking MongoDB connection:")
    
    try:
        # Try to import pymongo first
        import pymongo
        
        # Try to connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()  # Will raise an exception if cannot connect
        
        print("✅ MongoDB is running and accessible")
    except ImportError:
        print("❌ pymongo module not installed")
    except Exception as e:
        print("❌ MongoDB is not running or not accessible")
        print(f"  Error: {str(e)}")
        print("  Make sure MongoDB is installed and running.")
        
        # Provide installation instructions based on platform
        system = platform.system()
        if system == "Windows":
            print("\nTo install MongoDB on Windows:")
            print("1. Download from https://www.mongodb.com/try/download/community")
            print("2. Run the installer and follow the instructions")
            print("3. Start MongoDB service: 'net start MongoDB'")
        elif system == "Darwin":  # macOS
            print("\nTo install MongoDB on macOS:")
            print("1. Using Homebrew: brew tap mongodb/brew")
            print("2. brew install mongodb-community")
            print("3. Start MongoDB service: brew services start mongodb-community")
        else:  # Linux
            print("\nTo install MongoDB on Linux:")
            print("1. Follow instructions at https://docs.mongodb.com/manual/administration/install-on-linux/")
            print("2. Start MongoDB service: sudo systemctl start mongod")

def check_api_server():
    """Check if the API server is running"""
    print("\nChecking API server:")
    
    try:
        # Try to connect to the API
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print(f"❓ API server returned status code {response.status_code}")
    except requests.ConnectionError:
        print("❌ API server is not running")
        print("  Start it with: python main.py")

def main():
    """Main troubleshooting function"""
    print("=" * 50)
    print("Sales Call Analysis System - Troubleshooting Tool")
    print("=" * 50)
    
    # Run all checks
    check_python_version()
    check_directories()
    check_env_file()
    check_dependencies()
    check_mongodb()
    check_api_server()
    
    print("\nTroubleshooting completed!")
    print("\nIf there were issues, fix them according to the suggestions above.")
    print("If you need further help, please check the README.md file.")

if __name__ == "__main__":
    main() 