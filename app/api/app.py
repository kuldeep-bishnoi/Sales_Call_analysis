from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from datetime import datetime

from .routes import router as api_router
from ..database.connection import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sales Call Analysis API",
    description="API for transcribing and analyzing sales call recordings",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("Starting Sales Call Analysis API")
    await Database.connect()
    logger.info("Database connection established")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    logger.info("Shutting down Sales Call Analysis API")
    await Database.close()
    logger.info("Database connection closed")

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Uncaught exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Sales Call Analysis API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
    } 