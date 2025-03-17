import logging
import time
import json
from typing import List, Dict, Any
import re
import random

from ..models.schemas import (
    TranscriptionResult, AnalysisResult, SentimentLevel,
    EngagementLevel, ConversionProbability, Objection
)
from .sentiment_analyzer import SentimentAnalyzer
from .engagement_analyzer import EngagementAnalyzer
from .objection_detector import ObjectionDetector
from .satisfaction_analyzer import SatisfactionAnalyzer

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for orchestrating the full analysis of a call transcript"""
    
    @staticmethod
    async def analyze_call(transcription: TranscriptionResult) -> AnalysisResult:
        """Analyze a call transcript and return comprehensive analysis results"""
        logger.info(f"Starting full analysis for call_id: {transcription.call_id}")
        start_time = time.time()
        
        call_id = transcription.call_id
        transcript = transcription.processed_transcript or transcription.transcript
        
        try:
            # Run all analyses in parallel for better performance
            # 1. Sentiment Analysis
            sentiment_score, sentiment_level = await SentimentAnalyzer.analyze_sentiment(transcript)
            
            # 2. Engagement Analysis
            engagement_score, engagement_level = await EngagementAnalyzer.analyze_engagement(transcript)
            
            # 3. Objection Detection
            objections = await ObjectionDetector.detect_objections(transcript)
            
            # 4. Customer Satisfaction Score
            satisfaction_score = await SatisfactionAnalyzer.calculate_satisfaction_score(
                sentiment_score, engagement_score
            )
            
            # 5. Conversion Probability
            conversion_probability, probability_level = await SatisfactionAnalyzer.calculate_conversion_probability(
                sentiment_level, engagement_level, objections
            )
            
            # 6. Key Insights Generation
            key_insights = await AnalysisService._generate_key_insights(
                transcript, sentiment_level, engagement_level, 
                objections, satisfaction_score, probability_level
            )
            
            # Create the analysis result
            analysis_result = AnalysisResult(
                call_id=call_id,
                sentiment_score=sentiment_score,
                sentiment_level=sentiment_level,
                customer_satisfaction_score=satisfaction_score,
                engagement_score=engagement_score,
                engagement_level=engagement_level,
                objections=objections,
                conversion_probability_score=conversion_probability,
                conversion_probability_level=probability_level,
                key_insights=key_insights
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Full analysis completed in {processing_time:.2f} seconds")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during call analysis: {e}")
            raise
    
    @staticmethod
    async def _generate_key_insights(
        transcript: str,
        sentiment_level: SentimentLevel,
        engagement_level: EngagementLevel,
        objections: List[Objection],
        satisfaction_score: float,
        probability_level: ConversionProbability
    ) -> List[str]:
        """Generate key insights based on the analysis results using rule-based approach"""
        try:
            insights = []
            
            # Generate sentiment-based insight
            if sentiment_level == SentimentLevel.POSITIVE:
                insights.append("The customer expressed positive sentiment throughout the call, indicating a good rapport.")
            elif sentiment_level == SentimentLevel.NEGATIVE:
                insights.append("The customer expressed negative sentiment, suggesting potential dissatisfaction that should be addressed.")
            else:
                insights.append("The customer's sentiment was neutral, indicating neither strong approval nor disapproval.")
                
            # Generate engagement-based insight
            if engagement_level == EngagementLevel.HIGH:
                insights.append("High customer engagement indicates strong interest in the product/service.")
            elif engagement_level == EngagementLevel.LOW:
                insights.append("Low engagement suggests the customer may need more compelling information or a different approach.")
            else:
                insights.append("The customer showed moderate engagement, but could benefit from more targeted discussion.")
                
            # Generate objection-based insight
            if objections:
                # Group objections by category
                categories = {}
                for obj in objections:
                    if obj.category.value not in categories:
                        categories[obj.category.value] = 0
                    categories[obj.category.value] += 1
                
                # Identify most common objection type
                most_common = max(categories.items(), key=lambda x: x[1])
                insights.append(f"The customer raised multiple concerns about {most_common[0]}, which should be addressed in follow-ups.")
            else:
                insights.append("No significant objections were detected, suggesting the offering aligns well with customer needs.")
                
            # Generate conversion probability insight
            if probability_level == ConversionProbability.HIGH:
                insights.append(f"With a satisfaction score of {satisfaction_score:.1f}/10, the customer shows strong signs of conversion potential.")
            elif probability_level == ConversionProbability.LOW:
                insights.append(f"The customer's satisfaction score of {satisfaction_score:.1f}/10 suggests additional follow-up may be needed to improve conversion chances.")
            else:
                insights.append(f"Customer satisfaction score of {satisfaction_score:.1f}/10 indicates moderate conversion potential that could be improved with targeted follow-up.")
                
            # Add transcript-based insights if possible
            transcript_length = len(transcript.split())
            if transcript_length < 100:
                insights.append("The call was unusually short, which may indicate ineffective engagement or premature conclusion.")
            elif transcript_length > 1000:
                insights.append("The call was quite lengthy, which may indicate either deep engagement or inefficient conversation management.")
                
            # Return up to 5 insights
            return insights[:5]
                
        except Exception as e:
            logger.error(f"Error generating key insights: {e}")
            return [
                f"Analysis showed {sentiment_level.value} sentiment and {engagement_level.value} engagement.",
                f"Customer satisfaction estimated at {satisfaction_score:.1f}/10.",
                f"Conversion probability is {probability_level.value}."
            ] 