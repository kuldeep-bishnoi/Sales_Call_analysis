from typing import List, Optional, Dict, Any
from ..models.schemas import CallRecord, TranscriptionResult, AnalysisResult
from .connection import Database
import logging

logger = logging.getLogger(__name__)

class CallRepository:
    """Repository for call records in the database"""
    
    @staticmethod
    async def create(call: CallRecord) -> str:
        """Create a new call record in the database"""
        db = Database.get_db()
        result = await db.calls.insert_one(call.dict())
        logger.info(f"Created call record with ID: {call.call_id}")
        return call.call_id
    
    @staticmethod
    async def get_by_id(call_id: str) -> Optional[CallRecord]:
        """Get a call record by ID"""
        db = Database.get_db()
        call_data = await db.calls.find_one({"call_id": call_id})
        if not call_data:
            return None
        return CallRecord(**call_data)
    
    @staticmethod
    async def update(call_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a call record"""
        db = Database.get_db()
        result = await db.calls.update_one(
            {"call_id": call_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def list_calls(skip: int = 0, limit: int = 20) -> List[CallRecord]:
        """Get a list of call records with pagination"""
        db = Database.get_db()
        cursor = db.calls.find().sort("upload_date", -1).skip(skip).limit(limit)
        calls = [CallRecord(**call) for call in await cursor.to_list(length=limit)]
        return calls
    
    @staticmethod
    async def mark_as_processed(call_id: str) -> bool:
        """Mark a call as processed"""
        db = Database.get_db()
        result = await db.calls.update_one(
            {"call_id": call_id},
            {"$set": {"processed": True}}
        )
        return result.modified_count > 0

class TranscriptionRepository:
    """Repository for transcription results in the database"""
    
    @staticmethod
    async def create(transcription: TranscriptionResult) -> str:
        """Create a new transcription result in the database"""
        db = Database.get_db()
        result = await db.transcriptions.insert_one(transcription.dict())
        logger.info(f"Created transcription for call ID: {transcription.call_id}")
        return transcription.call_id
    
    @staticmethod
    async def get_by_call_id(call_id: str) -> Optional[TranscriptionResult]:
        """Get a transcription result by call ID"""
        db = Database.get_db()
        transcription_data = await db.transcriptions.find_one({"call_id": call_id})
        if not transcription_data:
            return None
        return TranscriptionResult(**transcription_data)
    
    @staticmethod
    async def update(call_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a transcription result"""
        db = Database.get_db()
        result = await db.transcriptions.update_one(
            {"call_id": call_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

class AnalysisRepository:
    """Repository for analysis results in the database"""
    
    @staticmethod
    async def create(analysis: AnalysisResult) -> str:
        """Create a new analysis result in the database"""
        db = Database.get_db()
        result = await db.analysis.insert_one(analysis.dict())
        logger.info(f"Created analysis for call ID: {analysis.call_id}")
        return analysis.call_id
    
    @staticmethod
    async def get_by_call_id(call_id: str) -> Optional[AnalysisResult]:
        """Get an analysis result by call ID"""
        db = Database.get_db()
        analysis_data = await db.analysis.find_one({"call_id": call_id})
        if not analysis_data:
            return None
        return AnalysisResult(**analysis_data)
    
    @staticmethod
    async def update(call_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an analysis result"""
        db = Database.get_db()
        result = await db.analysis.update_one(
            {"call_id": call_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def list_analysis(skip: int = 0, limit: int = 20) -> List[AnalysisResult]:
        """Get a list of analysis results with pagination"""
        db = Database.get_db()
        cursor = db.analysis.find().sort("analysis_date", -1).skip(skip).limit(limit)
        analyses = [AnalysisResult(**analysis) for analysis in await cursor.to_list(length=limit)]
        return analyses 