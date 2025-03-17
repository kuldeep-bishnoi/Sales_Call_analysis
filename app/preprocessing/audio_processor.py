import librosa
import soundfile as sf
import numpy as np
import os
import logging
from pathlib import Path
import time
from ..config.settings import TEMP_DIR

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Class for preprocessing audio files before transcription"""
    
    def __init__(self, input_file: str):
        """Initialize with input file path"""
        self.input_file = input_file
        self.file_name = Path(input_file).stem
        self.output_file = None
    
    def preprocess(self) -> str:
        """Process the audio file and return the path to the processed file"""
        logger.info(f"Preprocessing audio file: {self.input_file}")
        start_time = time.time()
        
        # Create output file path
        self.output_file = os.path.join(TEMP_DIR, f"{self.file_name}_processed.wav")
        
        try:
            # Load the audio file
            y, sr = librosa.load(self.input_file, sr=None)
            
            # Apply noise reduction
            y_denoised = self._reduce_noise(y, sr)
            
            # Apply volume normalization
            y_normalized = self._normalize_volume(y_denoised)
            
            # Remove silence
            y_no_silence = self._remove_silence(y_normalized, sr)
            
            # Save the processed audio
            sf.write(self.output_file, y_no_silence, sr)
            
            processing_time = time.time() - start_time
            logger.info(f"Audio preprocessing completed in {processing_time:.2f} seconds")
            
            return self.output_file
        
        except Exception as e:
            logger.error(f"Error preprocessing audio file: {e}")
            # If preprocessing fails, return the original file
            return self.input_file
    
    def _reduce_noise(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction to the audio signal"""
        # Simple noise reduction: high-pass filter to remove low-frequency noise
        b, a = librosa.filters.high_pass(sr, 150)
        y_filtered = librosa.filtfilt(b, a, y)
        
        return y_filtered
    
    def _normalize_volume(self, y: np.ndarray) -> np.ndarray:
        """Normalize the volume of the audio signal"""
        # Peak normalization to 0.95 to avoid clipping
        if np.max(np.abs(y)) > 0:
            y_normalized = 0.95 * y / np.max(np.abs(y))
        else:
            y_normalized = y
        
        return y_normalized
    
    def _remove_silence(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Remove long silence periods from audio"""
        # Detect non-silent intervals
        intervals = librosa.effects.split(
            y,
            top_db=30,  # Threshold in dB for silence detection
            frame_length=2048,
            hop_length=512
        )
        
        # If no intervals were found, return the original audio
        if len(intervals) == 0:
            return y
        
        # Concatenate non-silent intervals
        y_no_silence = np.concatenate([y[start:end] for start, end in intervals])
        
        return y_no_silence
    
    def get_audio_duration(self) -> float:
        """Get the duration of the audio file in seconds"""
        try:
            y, sr = librosa.load(self.input_file, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0 