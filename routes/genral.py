from utils.logging_utils import setup_logging

from fastapi import APIRouter

logger = setup_logging()

router = APIRouter(tags=["General"])

@router.get("/")
async def root():
    """
    Root endpoint to verify API status.

    Returns:
        dict: Welcome message
    """
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to QA API"}