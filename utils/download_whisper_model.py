#!/usr/bin/env python3
import os
import sys
import argparse
from huggingface_hub import snapshot_download

# Import the settings from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config.settings import MODELS_DIR, WHISPER_MODEL_TYPE

# Available model types for faster-whisper (each corresponds to a HuggingFace model)
WHISPER_MODELS = {
    "tiny": "guillaumekln/faster-whisper-tiny",
    "tiny.en": "guillaumekln/faster-whisper-tiny.en",
    "base": "guillaumekln/faster-whisper-base",
    "base.en": "guillaumekln/faster-whisper-base.en",
    "small": "guillaumekln/faster-whisper-small",
    "small.en": "guillaumekln/faster-whisper-small.en",
    "medium": "guillaumekln/faster-whisper-medium",
    "medium.en": "guillaumekln/faster-whisper-medium.en",
    "large-v1": "guillaumekln/faster-whisper-large-v1",
    "large-v2": "guillaumekln/faster-whisper-large-v2",
    "large-v3": "guillaumekln/faster-whisper-large-v3",
    "large": "guillaumekln/faster-whisper-large-v3"  # Default large to v3
}

def main():
    """Download Whisper model from HuggingFace Hub"""
    parser = argparse.ArgumentParser(description="Download Whisper model")
    parser.add_argument(
        "--model", 
        type=str, 
        default=WHISPER_MODEL_TYPE,
        choices=list(WHISPER_MODELS.keys()),
        help=f"Model type to download (default: {WHISPER_MODEL_TYPE})"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default=str(MODELS_DIR),
        help=f"Directory to save the model (default: {MODELS_DIR})"
    )
    
    args = parser.parse_args()
    model = args.model
    output_dir = args.output_dir
    
    # Check if the model is available
    if model not in WHISPER_MODELS:
        print(f"Error: Model {model} not found. Available models: {', '.join(WHISPER_MODELS.keys())}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the model
    try:
        print(f"Downloading model '{model}' from {WHISPER_MODELS[model]}...")
        model_path = snapshot_download(
            repo_id=WHISPER_MODELS[model],
            local_dir=os.path.join(output_dir, model),
            local_dir_use_symlinks=False
        )
        print(f"Model downloaded successfully to {model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")

if __name__ == "__main__":
    main() 