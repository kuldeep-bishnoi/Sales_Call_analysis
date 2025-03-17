import re
import logging
import time
from typing import Tuple, List, Dict
import nltk
from nltk.tokenize import sent_tokenize
from ..config.settings import ENGAGEMENT_THRESHOLD_HIGH, ENGAGEMENT_THRESHOLD_LOW
from ..models.schemas import EngagementLevel

logger = logging.getLogger(__name__)

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class EngagementAnalyzer:
    """Service for analyzing customer engagement in sales call transcripts"""
    
    # Affirmation words indicating engagement
    AFFIRMATION_WORDS = [
        "yes", "yeah", "sure", "absolutely", "definitely", "certainly",
        "agree", "agreed", "correct", "right", "exactly", "makes sense",
        "good point", "interesting", "tell me more", "go on"
    ]
    
    # Question patterns indicating engagement
    QUESTION_PATTERNS = [
        r'\?',
        r'\bhow\b.*?\?',
        r'\bwhat\b.*?\?',
        r'\bwhen\b.*?\?',
        r'\bwhere\b.*?\?',
        r'\bwhy\b.*?\?',
        r'\bcan\b.*?\?',
        r'\bcould\b.*?\?',
        r'\bwould\b.*?\?',
        r'\bshould\b.*?\?'
    ]
    
    @staticmethod
    async def analyze_engagement(transcript: str) -> Tuple[float, EngagementLevel]:
        """Analyze customer engagement in the transcript and return score and level"""
        logger.info("Starting engagement analysis")
        start_time = time.time()
        
        try:
            # Break transcript into sentences
            sentences = sent_tokenize(transcript.lower())
            
            # Analyze engagement metrics
            engagement_metrics = EngagementAnalyzer._calculate_engagement_metrics(sentences)
            
            # Calculate overall engagement score (0 to 1)
            engagement_score = EngagementAnalyzer._calculate_engagement_score(engagement_metrics)
            
            # Determine engagement level based on thresholds
            engagement_level = EngagementAnalyzer._get_engagement_level(engagement_score)
            
            processing_time = time.time() - start_time
            logger.info(f"Engagement analysis completed in {processing_time:.2f} seconds")
            
            return engagement_score, engagement_level
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return 0.5, EngagementLevel.MEDIUM
    
    @staticmethod
    def _calculate_engagement_metrics(sentences: List[str]) -> Dict[str, float]:
        """Calculate various engagement metrics from the sentences"""
        total_sentences = len(sentences)
        if total_sentences == 0:
            return {
                "affirmation_ratio": 0.0,
                "question_ratio": 0.0,
                "avg_response_length": 0.0,
                "engagement_ratio": 0.0
            }
        
        # Count affirmation sentences
        affirmation_count = sum(
            1 for s in sentences if any(word in s.split() for word in EngagementAnalyzer.AFFIRMATION_WORDS)
        )
        
        # Count question sentences
        question_count = 0
        for s in sentences:
            if any(re.search(pattern, s) for pattern in EngagementAnalyzer.QUESTION_PATTERNS):
                question_count += 1
        
        # Calculate average sentence length (as a proxy for response length)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / total_sentences
        
        # Normalize average sentence length (consider 15 words as a good engagement)
        normalized_length = min(avg_sentence_length / 15.0, 1.0)
        
        # Calculate affirmation and question ratios
        affirmation_ratio = affirmation_count / total_sentences
        question_ratio = question_count / total_sentences
        
        # Calculate overall engagement ratio (weighted sum)
        engagement_ratio = (
            0.4 * affirmation_ratio + 
            0.3 * question_ratio + 
            0.3 * normalized_length
        )
        
        return {
            "affirmation_ratio": affirmation_ratio,
            "question_ratio": question_ratio,
            "avg_response_length": normalized_length,
            "engagement_ratio": engagement_ratio
        }
    
    @staticmethod
    def _calculate_engagement_score(metrics: Dict[str, float]) -> float:
        """Calculate an overall engagement score from the metrics"""
        # Scale engagement ratio to a 0-1 score
        return metrics["engagement_ratio"]
    
    @staticmethod
    def _get_engagement_level(score: float) -> EngagementLevel:
        """Convert an engagement score to an engagement level"""
        if score >= ENGAGEMENT_THRESHOLD_HIGH:
            return EngagementLevel.HIGH
        elif score <= ENGAGEMENT_THRESHOLD_LOW:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.MEDIUM 