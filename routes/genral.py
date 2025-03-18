from utils.logging_utils import setup_logging
from fastapi import APIRouter

logger = setup_logging()

router = APIRouter(tags=["general"])

@router.get("/")
async def root():
    """Root endpoint - no authentication required"""
    return {
        "message": "PDF Question Answering API",
        "status": "running",
        "version": "1.0.0"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint - no authentication required"""
    return {"status": "healthy"}