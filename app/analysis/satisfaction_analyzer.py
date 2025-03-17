import logging
import time
from typing import Tuple
from ..models.schemas import SentimentLevel, EngagementLevel, Objection, ConversionProbability

logger = logging.getLogger(__name__)

class SatisfactionAnalyzer:
    """Service for analyzing customer satisfaction and conversion probability"""
    
    @staticmethod
    async def calculate_satisfaction_score(
        sentiment_score: float, 
        engagement_score: float
    ) -> float:
        """Calculate customer satisfaction score (1-10) based on sentiment and engagement"""
        logger.info("Calculating customer satisfaction score")
        
        # Base satisfaction calculation
        # Convert sentiment from [-1,1] to [0,1] scale
        normalized_sentiment = (sentiment_score + 1) / 2
        
        # Weighted combination of sentiment and engagement
        satisfaction_raw = (normalized_sentiment * 0.7) + (engagement_score * 0.3)
        
        # Scale to 1-10 range
        satisfaction_score = 1 + (satisfaction_raw * 9)
        
        # Ensure within bounds
        satisfaction_score = max(1.0, min(10.0, satisfaction_score))
        
        logger.info(f"Calculated satisfaction score: {satisfaction_score:.2f}")
        return satisfaction_score
    
    @staticmethod
    async def calculate_conversion_probability(
        sentiment_level: SentimentLevel,
        engagement_level: EngagementLevel,
        objections: list[Objection]
    ) -> Tuple[float, ConversionProbability]:
        """Calculate probability of conversion based on sentiment, engagement, and objections"""
        logger.info("Calculating conversion probability")
        
        # Base conversion probability scores for each factor
        sentiment_prob = SatisfactionAnalyzer._sentiment_to_probability(sentiment_level)
        engagement_prob = SatisfactionAnalyzer._engagement_to_probability(engagement_level)
        
        # Calculate objection impact (decreases probability)
        objection_impact = SatisfactionAnalyzer._calculate_objection_impact(objections)
        
        # Weighted combination of factors
        conversion_probability = (
            (sentiment_prob * 0.4) + 
            (engagement_prob * 0.4) - 
            (objection_impact * 0.2)
        )
        
        # Ensure probability is within [0,1] range
        conversion_probability = max(0.0, min(1.0, conversion_probability))
        
        # Determine probability level
        probability_level = SatisfactionAnalyzer._get_probability_level(conversion_probability)
        
        logger.info(f"Calculated conversion probability: {conversion_probability:.2f}, level: {probability_level}")
        return conversion_probability, probability_level
    
    @staticmethod
    def _sentiment_to_probability(sentiment_level: SentimentLevel) -> float:
        """Convert sentiment level to a probability value"""
        if sentiment_level == SentimentLevel.POSITIVE:
            return 0.8  # 80% probability for positive sentiment
        elif sentiment_level == SentimentLevel.NEUTRAL:
            return 0.5  # 50% probability for neutral sentiment
        else:  # NEGATIVE
            return 0.2  # 20% probability for negative sentiment
    
    @staticmethod
    def _engagement_to_probability(engagement_level: EngagementLevel) -> float:
        """Convert engagement level to a probability value"""
        if engagement_level == EngagementLevel.HIGH:
            return 0.8  # 80% probability for high engagement
        elif engagement_level == EngagementLevel.MEDIUM:
            return 0.5  # 50% probability for medium engagement
        else:  # LOW
            return 0.2  # 20% probability for low engagement
    
    @staticmethod
    def _calculate_objection_impact(objections: list[Objection]) -> float:
        """Calculate the impact of objections on conversion probability"""
        if not objections:
            return 0.0  # No objections means no negative impact
        
        # Weight objections by their confidence and category severity
        total_impact = 0.0
        
        for objection in objections:
            # Determine severity of objection category
            category_severity = {
                "pricing": 0.8,     # Pricing objections are severe
                "need": 0.9,        # Need objections are most severe
                "competition": 0.7, # Competition objections are moderately severe
                "timing": 0.5,      # Timing objections are less severe
                "authority": 0.6,   # Authority objections are moderately severe
                "other": 0.5        # Other objections have average severity
            }.get(objection.category, 0.5)
            
            # Impact is product of confidence and severity
            impact = objection.confidence * category_severity
            total_impact += impact
        
        # Scale total impact based on number of objections
        # More objections have diminishing returns on impact
        scaled_impact = min(1.0, total_impact / (1 + 0.5 * (len(objections) - 1)))
        
        return scaled_impact
    
    @staticmethod
    def _get_probability_level(probability: float) -> ConversionProbability:
        """Convert a probability score to a probability level"""
        if probability >= 0.7:
            return ConversionProbability.HIGH
        elif probability >= 0.4:
            return ConversionProbability.MEDIUM
        else:
            return ConversionProbability.LOW 