import time
import logging
import re
from typing import Tuple, Dict, List
from ..config.settings import SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE
from ..models.schemas import SentimentLevel

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Service for analyzing the sentiment of transcribed text"""
    
    # Define sentiment dictionaries
    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic", "terrific",
        "outstanding", "superb", "brilliant", "awesome", "impressive", "extraordinary",
        "exceptional", "remarkable", "splendid", "marvelous", "fabulous", "perfect",
        "happy", "glad", "pleased", "satisfied", "delighted", "content", "thankful",
        "grateful", "appreciate", "excited", "thrilled", "enthusiastic", "interested",
        "yes", "definitely", "absolutely", "certainly", "agreed", "love", "like",
        "enjoy", "helpful", "useful", "valuable", "beneficial", "advantage", "benefit",
        "improvement", "solution", "success", "effective", "efficient"
    }
    
    NEGATIVE_WORDS = {
        "bad", "poor", "terrible", "horrible", "awful", "dreadful", "unacceptable",
        "disappointing", "frustrating", "annoying", "irritating", "unsatisfactory",
        "inadequate", "inferior", "deficient", "substandard", "mediocre", "appalling",
        "unhappy", "sad", "upset", "disappointed", "dissatisfied", "displeased", "angry",
        "furious", "mad", "outraged", "irritated", "annoyed", "frustrated", "no", "not",
        "never", "impossible", "cannot", "won't", "wouldn't", "shouldn't", "hate", "dislike",
        "loathe", "detest", "despise", "expensive", "costly", "pricey", "overpriced",
        "complicated", "confusing", "difficult", "complex", "problem", "issue", "concern",
        "complaint", "mistake", "error", "fault", "defect", "failure", "malfunction"
    }
    
    INTENSIFIERS = {
        "very", "extremely", "incredibly", "exceptionally", "remarkably", "particularly",
        "especially", "notably", "decidedly", "unusually", "absolutely", "totally",
        "completely", "entirely", "utterly", "thoroughly", "highly", "strongly", "deeply",
        "profoundly", "immensely", "vastly", "greatly", "really", "truly", "so", "too"
    }
    
    @staticmethod
    async def analyze_sentiment(transcript: str) -> Tuple[float, SentimentLevel]:
        """Analyze the sentiment of the transcript and return score and level"""
        logger.info("Starting sentiment analysis")
        start_time = time.time()
        
        try:
            # Convert to lowercase and split into words
            words = re.findall(r'\b\w+\b', transcript.lower())
            
            # Count positive and negative words
            positive_count = 0
            negative_count = 0
            
            # Track the previous word to check for negations and intensifiers
            prev_word = ""
            
            for word in words:
                # Check if the previous word is a negation
                is_negated = prev_word in {"not", "no", "never", "don't", "doesn't", "didn't", "won't", "can't", "couldn't"}
                
                # Check if the previous word is an intensifier
                is_intensified = prev_word in SentimentAnalyzer.INTENSIFIERS
                
                # Count positive words
                if word in SentimentAnalyzer.POSITIVE_WORDS:
                    if is_negated:
                        negative_count += 1
                    else:
                        positive_count += (1.5 if is_intensified else 1)
                
                # Count negative words
                elif word in SentimentAnalyzer.NEGATIVE_WORDS:
                    if is_negated:
                        positive_count += 0.5  # Double negation is less positive than a direct positive
                    else:
                        negative_count += (1.5 if is_intensified else 1)
                
                # Update previous word
                prev_word = word
            
            # Consider the total number of words for normalization
            total_words = len(words)
            if total_words < 10:
                # Not enough words for reliable analysis
                sentiment_score = 0.0
            else:
                # Calculate sentiment score with normalization for transcript length
                sentiment_score = (positive_count - negative_count) / (total_words ** 0.5)
                
                # Limit score to range [-1.0, 1.0]
                sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            # Determine sentiment level based on thresholds
            sentiment_level = SentimentAnalyzer._get_sentiment_level(sentiment_score)
            
            processing_time = time.time() - start_time
            logger.info(f"Sentiment analysis completed in {processing_time:.2f} seconds: score={sentiment_score:.2f}, level={sentiment_level}")
            
            return sentiment_score, sentiment_level
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0, SentimentLevel.NEUTRAL
    
    @staticmethod
    def _get_sentiment_level(score: float) -> SentimentLevel:
        """Convert a sentiment score to a sentiment level"""
        if score >= SENTIMENT_THRESHOLD_POSITIVE:
            return SentimentLevel.POSITIVE
        elif score <= SENTIMENT_THRESHOLD_NEGATIVE:
            return SentimentLevel.NEGATIVE
        else:
            return SentimentLevel.NEUTRAL 