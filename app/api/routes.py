from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
import logging
from datetime import datetime
import uuid

from ..config.settings import UPLOADS_DIR, ALLOWED_AUDIO_FORMATS, MAX_AUDIO_SIZE_MB
from ..models.schemas import CallRecord, TranscriptionResult, AnalysisResult, CompleteCallAnalysis
from ..database.repositories import CallRepository, TranscriptionRepository, AnalysisRepository
from ..preprocessing.audio_processor import AudioProcessor
from ..core.transcription_service import TranscriptionService
from ..analysis.analysis_service import AnalysisService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=CallRecord)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    auto_process: bool = Query(True, description="Automatically process the file after upload")
):
    """Upload an audio file and optionally start processing"""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_AUDIO_FORMATS)}"
        )
    
    # Generate a unique ID for this call
    call_id = str(uuid.uuid4())
    
    # Create file path with original name
    file_path = os.path.join(UPLOADS_DIR, f"{call_id}{file_ext}")
    
    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Check file size
        if file_size > MAX_AUDIO_SIZE_MB * 1024 * 1024:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds the {MAX_AUDIO_SIZE_MB} MB limit"
            )
        
        # Create audio processor to get duration
        audio_processor = AudioProcessor(file_path)
        duration = audio_processor.get_audio_duration()
        
        # Create call record
        call_record = CallRecord(
            call_id=call_id,
            filename=file.filename,
            file_path=file_path,
            file_format=file_ext,
            file_size=file_size,
            duration=duration,
            upload_date=datetime.now(),
            processed=False
        )
        
        # Save to database
        await CallRepository.create(call_record)
        
        # If auto process is enabled, start processing in background
        if auto_process:
            background_tasks.add_task(process_call, call_id)
        
        return call_record
        
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/process/{call_id}", response_model=dict)
async def start_processing(call_id: str, background_tasks: BackgroundTasks):
    """Start processing a previously uploaded call"""
    # Check if call exists
    call = await CallRepository.get_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # If already processed, return error
    if call.processed:
        raise HTTPException(status_code=400, detail="Call already processed")
    
    # Start processing in background
    background_tasks.add_task(process_call, call_id)
    
    return {"status": "processing", "call_id": call_id}

@router.get("/calls", response_model=List[CallRecord])
async def list_calls(skip: int = 0, limit: int = 20):
    """Get a list of all call records"""
    calls = await CallRepository.list_calls(skip, limit)
    return calls

@router.get("/calls/{call_id}", response_model=CompleteCallAnalysis)
async def get_call_analysis(call_id: str):
    """Get the complete analysis for a specific call"""
    # Get call record
    call = await CallRepository.get_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Get transcription
    transcription = await TranscriptionRepository.get_by_call_id(call_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    # Get analysis
    analysis = await AnalysisRepository.get_by_call_id(call_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Return complete analysis
    return CompleteCallAnalysis(
        call=call,
        transcription=transcription,
        analysis=analysis
    )

@router.get("/analysis", response_model=List[AnalysisResult])
async def list_analysis(skip: int = 0, limit: int = 20):
    """Get a list of all analysis results"""
    analyses = await AnalysisRepository.list_analysis(skip, limit)
    return analyses

# Background task for processing a call
async def process_call(call_id: str):
    """Process a call in the background"""
    logger.info(f"Starting background processing for call_id: {call_id}")
    
    try:
        # Get call record
        call = await CallRepository.get_by_id(call_id)
        if not call:
            logger.error(f"Call not found: {call_id}")
            return
        
        # Step 1: Preprocess the audio
        audio_processor = AudioProcessor(call.file_path)
        processed_audio_path = audio_processor.preprocess()
        
        # Step 2: Transcribe the audio
        transcription = await TranscriptionService.transcribe(processed_audio_path, call_id)
        
        # Save transcription to database
        await TranscriptionRepository.create(transcription)
        
        # Check if the transcript is valid speech before proceeding with analysis
        if not transcription.is_valid:
            logger.warning(f"Skipping analysis for call_id {call_id}: {transcription.validation_message}")
            
            # Create a "null" analysis result with error message
            analysis = AnalysisResult(
                call_id=call_id,
                sentiment_score=0.0,
                sentiment_level=SentimentLevel.NEUTRAL,
                customer_satisfaction_score=5.0,
                engagement_score=0.0,
                engagement_level=EngagementLevel.LOW,
                conversion_probability_score=0.0,
                conversion_probability_level=ConversionProbability.LOW,
                key_insights=[
                    f"Analysis skipped: {transcription.validation_message}",
                    "Please upload a different audio file with speech content."
                ]
            )
            
            # Save the null analysis result
            await AnalysisRepository.create(analysis)
            
            # Mark call as processed
            await CallRepository.mark_as_processed(call_id)
            
            # Clean up
            if processed_audio_path != call.file_path and os.path.exists(processed_audio_path):
                os.remove(processed_audio_path)
            
            return
        
        # Step 3: Analyze the transcript
        analysis = await AnalysisService.analyze_call(transcription)
        
        # Save analysis to database
        await AnalysisRepository.create(analysis)
        
        # Mark call as processed
        await CallRepository.mark_as_processed(call_id)
        
        # Clean up temporary processed audio file if it's different from original
        if processed_audio_path != call.file_path and os.path.exists(processed_audio_path):
            os.remove(processed_audio_path)
            
        logger.info(f"Completed processing for call_id: {call_id}")
        
    except Exception as e:
        logger.error(f"Error processing call {call_id}: {e}") 