from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class SentimentLevel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class EngagementLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ConversionProbability(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ObjectionCategory(str, Enum):
    PRICING = "pricing"
    TIMING = "timing"
    NEED = "need"
    COMPETITION = "competition"
    AUTHORITY = "authority"
    OTHER = "other"

class Objection(BaseModel):
    category: ObjectionCategory
    text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    position: int  # Position in transcript where objection was detected

class CallUpload(BaseModel):
    filename: str
    file_format: str
    file_size: int
    duration: Optional[float] = None  # Duration in seconds

class CallRecord(BaseModel):
    call_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    upload_date: datetime = Field(default_factory=datetime.now)
    file_path: str
    file_format: str
    file_size: int  # Size in bytes
    duration: Optional[float] = None  # Duration in seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processed: bool = False

class TranscriptionResult(BaseModel):
    call_id: str
    transcript: str
    processed_transcript: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = None
    processing_time: float  # Time taken to transcribe in seconds
    is_valid: bool = True  # Whether the transcript contains valid speech content
    validation_message: str = "Valid speech transcript"  # Message describing the validation result

class AnalysisResult(BaseModel):
    call_id: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sentiment_level: SentimentLevel
    customer_satisfaction_score: float = Field(..., ge=1.0, le=10.0)
    engagement_score: float = Field(..., ge=0.0, le=1.0)
    engagement_level: EngagementLevel
    objections: List[Objection] = Field(default_factory=list)
    conversion_probability_score: float = Field(..., ge=0.0, le=1.0)
    conversion_probability_level: ConversionProbability
    key_insights: List[str] = Field(default_factory=list)
    analysis_date: datetime = Field(default_factory=datetime.now)

class CompleteCallAnalysis(BaseModel):
    call: CallRecord
    transcription: TranscriptionResult
    analysis: AnalysisResult 