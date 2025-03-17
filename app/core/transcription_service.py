import time
import logging
import json
import os
import re
from pathlib import Path
from faster_whisper import WhisperModel
from ..config.settings import TRANSCRIPTS_DIR, WHISPER_MODEL_TYPE, WHISPER_LANGUAGE
from ..models.schemas import TranscriptionResult

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for transcribing audio using faster-whisper, a local implementation of OpenAI's Whisper model"""
    
    # Patterns to detect non-speech audio content
    MUSIC_PATTERN = r'^[♪\s]+$'
    EMPTY_PATTERN = r'^\s*$'
    
    _model = None
    
    @classmethod
    def _get_model(cls):
        """Get or initialize the Whisper model"""
        if cls._model is None:
            try:
                logger.info(f"Loading Whisper model: {WHISPER_MODEL_TYPE}")
                # Initialize the model with the specified type
                # Use CPU computation to avoid CUDA/GPU requirements
                cls._model = WhisperModel(WHISPER_MODEL_TYPE, device="cpu", compute_type="int8")
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise
        return cls._model
    
    @classmethod
    async def transcribe(cls, audio_file_path: str, call_id: str) -> TranscriptionResult:
        """Transcribe the audio file and return the result"""
        logger.info(f"Starting transcription for call_id: {call_id}")
        start_time = time.time()
        
        try:
            # Get the Whisper model
            model = cls._get_model()
            
            # Transcribe the audio file
            logger.info(f"Transcribing audio file: {audio_file_path}")
            segments, info = model.transcribe(audio_file_path, language=WHISPER_LANGUAGE)
            
            # Convert segments to a list and build the full transcript
            segments_list = list(segments)
            transcript = " ".join(segment.text for segment in segments_list)
            
            # Convert segments to a format similar to OpenAI's API
            formatted_segments = []
            for i, segment in enumerate(segments_list):
                formatted_segments.append({
                    "id": i,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "tokens": [],  # No token info in faster-whisper
                    "confidence": segment.avg_logprob  # Use average log probability as confidence
                })
            
            # Get the detected language
            language = info.language
            
            # Validate the transcript to check if it's actual speech
            is_valid, validation_message = cls._validate_transcript(transcript)
            if not is_valid:
                logger.warning(f"Invalid transcript detected: {validation_message}")
                
                # Return a special TranscriptionResult that indicates invalid audio
                processing_time = time.time() - start_time
                return TranscriptionResult(
                    call_id=call_id,
                    transcript=transcript,
                    processed_transcript=validation_message,
                    segments=formatted_segments,
                    language=language,
                    processing_time=processing_time,
                    is_valid=False,
                    validation_message=validation_message
                )
            
            # Create a clean version of the transcript (removing fillers)
            processed_transcript = cls._clean_transcript(transcript)
            
            # Save transcript to file
            transcript_data = {
                "text": transcript,
                "segments": formatted_segments,
                "language": language
            }
            transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{call_id}.json")
            with open(transcript_path, "w") as f:
                json.dump(transcript_data, f, indent=2)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            logger.info(f"Transcription completed in {processing_time:.2f} seconds")
            
            # Create and return the transcription result
            return TranscriptionResult(
                call_id=call_id,
                transcript=transcript,
                processed_transcript=processed_transcript,
                segments=formatted_segments,
                language=language,
                processing_time=processing_time,
                is_valid=True,
                validation_message="Valid speech transcript"
            )
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    @staticmethod
    def _validate_transcript(transcript: str) -> tuple[bool, str]:
        """Validate if the transcript contains actual speech content
        
        Returns:
            tuple[bool, str]: (is_valid, validation_message)
        """
        clean_transcript = transcript.strip()
        
        # Check if the transcript is primarily music notes
        if re.match(TranscriptionService.MUSIC_PATTERN, clean_transcript):
            return False, "The audio appears to contain music without speech"
        
        # Check if the transcript is empty
        if re.match(TranscriptionService.EMPTY_PATTERN, clean_transcript):
            return False, "The audio does not contain any detectable speech"
        
        # Check if transcript is too short (less than 10 characters)
        if len(clean_transcript) < 10:
            return False, "The audio contains very little speech content"
        
        # Check if the transcript is primarily non-speech sounds
        if "[" in clean_transcript and "]" in clean_transcript and len(clean_transcript) < 30:
            # Check for descriptive brackets like [laughing], [background noise]
            return False, "The audio primarily contains non-speech sounds"
        
        # Split into words for further analysis
        words = clean_transcript.split()
        total_words = len(words)
        
        if total_words == 0:
            return False, "No words detected in the transcript"
            
        # Check for extremely low word diversity (repeated words)
        unique_words = set(w.lower() for w in words)
        unique_word_count = len(unique_words)
        
        # Calculate word diversity ratio
        diversity_ratio = unique_word_count / total_words if total_words > 0 else 0
        
        # If more than 6 words but very low diversity (mostly repeating)
        if total_words >= 6 and unique_word_count <= 2:
            return False, "The audio appears to contain repetitive sounds (possibly music)"
            
        # Check for low diversity in longer transcripts
        if total_words >= 10 and diversity_ratio < 0.3:  # Less than 30% unique words
            return False, "The transcript contains unusually repetitive content"
        
        # Check for consecutive repetitions of the same word
        word_str = " ".join(words).lower()
        for word in unique_words:
            # Find any word that repeats 3+ times consecutively
            if re.search(r'\b' + re.escape(word) + r'\b(?:\s+\b' + re.escape(word) + r'\b){2,}', word_str):
                return False, "The audio contains repetitive patterns and likely isn't speech"
        
        # Check for uppercase-only content (often indicates noise interpreted as shouting)
        if clean_transcript.isupper() and len(clean_transcript) > 15:
            return False, "The transcript appears to be all uppercase, which often indicates noise misinterpreted as speech"
        
        # Check for random character sequences (gibberish)
        # Count words that don't appear in common vocabulary
        common_words = {"the", "be", "to", "of", "and", "a", "in", "that", "have", "i", 
                       "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
                       "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
                       "or", "an", "will", "my", "one", "all", "would", "there", "their", "what"}
        
        # Count words with unusual patterns (like random character sequences)
        unusual_word_count = 0
        for word in unique_words:
            # Check if word contains unusual character patterns
            if (re.search(r'[a-zA-Z]{12,}', word)  # Very long words
                or re.search(r'(.)\1{2,}', word)   # Characters repeating 3+ times
                or re.search(r'[^a-zA-Z0-9\s.,!?\'"-]', word)):  # Unusual characters
                unusual_word_count += 1
        
        # If more than 40% of unique words are unusual/gibberish
        if unique_word_count > 3 and unusual_word_count / unique_word_count > 0.4:
            return False, "The transcript contains unusually formatted words that may not be real speech"
            
        # Check for nonexistent words in all-caps (common in music misinterpretation)
        all_caps_non_words = 0
        for word in unique_words:
            if word.isupper() and len(word) > 3 and word.lower() not in common_words:
                all_caps_non_words += 1
                
        if all_caps_non_words >= 3 and all_caps_non_words / unique_word_count > 0.5:
            return False, "The transcript contains multiple uppercase non-dictionary words, likely noise or music"
        
        return True, "Valid speech content"
    
    @staticmethod
    def _clean_transcript(transcript: str) -> str:
        """Clean the transcript by removing filler words and normalizing text"""
        # List of common filler words to remove
        filler_words = [
            " um ", " uh ", " er ", " ah ", " like ", " you know ", 
            " I mean ", " so ", " actually ", " basically ", " literally ",
            " right "
        ]
        
        # Clean the transcript
        cleaned = transcript.lower()
        
        # Remove filler words
        for filler in filler_words:
            cleaned = cleaned.replace(filler, " ")
        
        # Replace multiple spaces with a single space
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned 