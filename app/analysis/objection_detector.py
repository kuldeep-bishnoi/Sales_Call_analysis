import re
import logging
import time
from typing import List, Dict, Any, Tuple
from ..models.schemas import Objection, ObjectionCategory

logger = logging.getLogger(__name__)

class ObjectionDetector:
    """Service for detecting customer objections in sales call transcripts"""
    
    # Common objection patterns by category
    OBJECTION_PATTERNS = {
        ObjectionCategory.PRICING: [
            r"too expensive", r"too (?:much|costly|pricey)", r"can't afford", 
            r"not in (?:budget|our budget)", r"price is (?:high|steep)", 
            r"cheaper alternative", r"discount", r"not worth"
        ],
        ObjectionCategory.TIMING: [
            r"not (?:now|right now)", r"bad time", r"busy right now", 
            r"call (?:back|later|again)", r"next (?:quarter|year|month)", 
            r"not ready", r"too soon"
        ],
        ObjectionCategory.NEED: [
            r"don't need", r"no need", r"already have", r"not interested", 
            r"not looking", r"doesn't fit", r"no use"
        ],
        ObjectionCategory.COMPETITION: [
            r"already use", r"competitor", r"another vendor", r"working with", 
            r"using (?:another|different)"
        ],
        ObjectionCategory.AUTHORITY: [
            r"need to (?:talk|discuss|consult)", r"(?:boss|manager|team) will", 
            r"not my decision", r"(?:committee|board) decides", r"approval"
        ],
    }
    
    # Extended keyword lists for more robust detection
    OBJECTION_KEYWORDS = {
        ObjectionCategory.PRICING: [
            "price", "cost", "expensive", "budget", "money", "afford", 
            "discount", "cheaper", "value", "investment", "roi", "return", 
            "fee", "charge", "payment", "billing"
        ],
        ObjectionCategory.TIMING: [
            "time", "now", "later", "soon", "delay", "wait", "year", "month", 
            "quarter", "busy", "schedule", "agenda", "calendar", "postpone"
        ],
        ObjectionCategory.NEED: [
            "need", "want", "require", "interested", "benefit", "value", 
            "useful", "helpful", "necessary", "must", "should", "could", 
            "would", "relevant", "applicable"
        ],
        ObjectionCategory.COMPETITION: [
            "competitor", "alternative", "option", "other", "already", 
            "using", "current", "solution", "provider", "vendor", "company", 
            "partner", "relationship"
        ],
        ObjectionCategory.AUTHORITY: [
            "decision", "authority", "approve", "permission", "boss", "manager", 
            "director", "team", "committee", "board", "executives", "leadership", 
            "stakeholder", "consult", "discuss"
        ],
    }
    
    @staticmethod
    async def detect_objections(transcript: str) -> List[Objection]:
        """Detect objections in the transcript and return them with categories"""
        logger.info("Starting objection detection")
        start_time = time.time()
        
        objections = []
        
        try:
            # First pass: Use regex patterns to detect common objections
            pattern_objections = ObjectionDetector._detect_with_patterns(transcript)
            objections.extend(pattern_objections)
            
            # Second pass: Use keyword analysis for more robust detection
            keyword_objections = ObjectionDetector._detect_with_keywords(transcript)
            
            # Merge objections, avoiding duplicates
            all_objections = ObjectionDetector._merge_objections(objections, keyword_objections)
            
            processing_time = time.time() - start_time
            logger.info(f"Objection detection completed in {processing_time:.2f} seconds, found {len(all_objections)} objections")
            
            return all_objections
            
        except Exception as e:
            logger.error(f"Error detecting objections: {e}")
            return objections
    
    @staticmethod
    def _detect_with_patterns(transcript: str) -> List[Objection]:
        """Detect objections using regex patterns"""
        objections = []
        
        # Convert transcript to lowercase for case-insensitive matching
        transcript_lower = transcript.lower()
        sentences = re.split(r'[.!?]+', transcript_lower)
        
        # Check each sentence for objection patterns
        for position, sentence in enumerate(sentences):
            for category, patterns in ObjectionDetector.OBJECTION_PATTERNS.items():
                for pattern in patterns:
                    matches = re.search(r'\b' + pattern + r'\b', sentence)
                    if matches:
                        # Found an objection
                        objections.append(Objection(
                            category=category,
                            text=sentence.strip(),
                            confidence=0.7,  # Default confidence for pattern matching
                            position=position
                        ))
                        # Move to next sentence once we find an objection
                        break
        
        return objections
    
    @staticmethod
    def _detect_with_keywords(transcript: str) -> List[Objection]:
        """Detect objections using keyword analysis"""
        objections = []
        
        # Split transcript into sentences
        transcript_lower = transcript.lower()
        sentences = re.split(r'[.!?]+', transcript_lower)
        
        # Flags to track objection-related keywords
        negative_indicators = ["no", "not", "don't", "doesn't", "can't", "won't", "wouldn't", "couldn't", "shouldn't", "never"]
        hesitation_indicators = ["but", "however", "though", "although", "yet", "still", "concerned", "worry", "issue", "problem"]
        question_indicators = ["?", "how", "what", "why", "when", "who", "where", "which", "can", "will", "would", "could", "should"]
        
        # Check each sentence for objection keywords
        for position, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence.split()) < 3:
                continue
                
            # Check if sentence has negative or hesitant tone
            has_negative = any(re.search(r'\b' + word + r'\b', sentence) for word in negative_indicators)
            has_hesitation = any(re.search(r'\b' + word + r'\b', sentence) for word in hesitation_indicators)
            is_question = any(word in sentence for word in question_indicators)
            
            # Score each category based on keyword matches
            category_scores = {}
            
            for category, keywords in ObjectionDetector.OBJECTION_KEYWORDS.items():
                # Count keyword matches
                matches = sum(1 for word in keywords if re.search(r'\b' + word + r'\b', sentence))
                if matches > 0:
                    # Calculate confidence based on keyword density and presence of objection indicators
                    word_count = len(sentence.split())
                    base_confidence = min(0.5 + (matches / word_count) * 2, 0.9)
                    
                    # Adjust confidence based on indicators
                    if has_negative:
                        base_confidence += 0.15
                    if has_hesitation:
                        base_confidence += 0.1
                    if is_question:
                        base_confidence += 0.05
                        
                    # Cap confidence at 0.95
                    confidence = min(base_confidence, 0.95)
                    
                    # Only consider it an objection if confidence exceeds threshold
                    if confidence >= 0.6:
                        category_scores[category] = confidence
            
            # If we found at least one category with high confidence
            if category_scores:
                # Choose the category with highest confidence
                best_category = max(category_scores.items(), key=lambda x: x[1])
                objections.append(Objection(
                    category=best_category[0],
                    text=sentence.strip(),
                    confidence=best_category[1],
                    position=position
                ))
        
        return objections
    
    @staticmethod
    def _merge_objections(pattern_objections: List[Objection], keyword_objections: List[Objection]) -> List[Objection]:
        """Merge objections from pattern matching and keyword detection, avoiding duplicates"""
        # Use a simple text similarity metric to detect duplicates
        unique_objections = list(pattern_objections)  # Start with pattern objections
        
        for keyword_obj in keyword_objections:
            # Check if this objection is similar to any existing one
            is_duplicate = False
            for existing_obj in unique_objections:
                # Simple similarity check - if the texts are similar
                if ObjectionDetector._text_similarity(keyword_obj.text, existing_obj.text) > 0.7:
                    # Keep the one with higher confidence
                    if keyword_obj.confidence > existing_obj.confidence:
                        existing_obj.confidence = keyword_obj.confidence
                        existing_obj.text = keyword_obj.text  # Use keyword text which might be more precise
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_objections.append(keyword_obj)
        
        return unique_objections
    
    @staticmethod
    def _text_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two text strings (0-1)"""
        # Simple Jaccard similarity for word sets
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) 