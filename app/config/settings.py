import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = DATA_DIR / "temp"
UPLOADS_DIR = DATA_DIR / "uploads"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
RESULTS_DIR = DATA_DIR / "results"
MODELS_DIR = DATA_DIR / "models"

# Create necessary directories
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Whisper model settings
WHISPER_MODEL_TYPE = os.getenv("WHISPER_MODEL_TYPE", "base")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")

# Database settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sales_call_analytics")

# Audio processing settings
ALLOWED_AUDIO_FORMATS = [".mp3", ".wav", ".flac", ".m4a"]
MAX_AUDIO_SIZE_MB = 50  # Maximum file size in MB

# Analysis settings
SENTIMENT_THRESHOLD_POSITIVE = 0.5
SENTIMENT_THRESHOLD_NEGATIVE = -0.5
ENGAGEMENT_THRESHOLD_HIGH = 0.7
ENGAGEMENT_THRESHOLD_LOW = 0.3 