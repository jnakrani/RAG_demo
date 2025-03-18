import logging
import sys
import os
import traceback
from logging.handlers import RotatingFileHandler

def setup_logging(debug=True):
    """Setup logging configuration with detailed debug information"""
    # Ensure logs directory exists
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, "app.log")

    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO

    # Log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s' if debug else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create formatters
    formatter = logging.Formatter(log_format)
    uvicorn_formatter = logging.Formatter('%(levelprefix)s %(message)s')  # Uvicorn compatible

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Create and configure logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Configure uvicorn logging properly
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(logging.INFO)  # Avoid excessive debugging
    uvicorn_access_logger.propagate = False  # Prevent duplicate logs

    return logger

def log_error_with_context(logger, error_msg, exc_info=None, context=None):
    """Log error with additional context information"""
    if context is None:
        context = {}

    error_details = {
        'error_message': str(error_msg),
        'context': context
    }

    logger.error(f"Error occurred: {error_details}", exc_info=exc_info)
