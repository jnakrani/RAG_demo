"""
Logging Configuration Module

This module provides logging setup functionality for the QA system.
It configures logging with both console and file output, setting up
a standardized format for log messages across the application.

The logging configuration includes:
- Console output for immediate feedback
- File output for persistent logging
- Timestamp and log level information
- Module name tracking
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os
import traceback

def setup_logging(debug=True):
    """Setup logging configuration with detailed debug information"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s' if debug else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create formatters
    formatter = logging.Formatter(log_format)
    uvicorn_formatter = logging.Formatter('%(levelprefix)s %(message)s')  # Compatible format

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Configure root logger
    logging.basicConfig(level=log_level, handlers=[console_handler, file_handler])

    # Get logger
    logger = logging.getLogger(__name__)

    # Adjust logging for uvicorn
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = [console_handler, file_handler]
    uvicorn_access_logger.setLevel(logging.INFO)  # Avoid excessive debugging

    return logger

def log_error_with_context(logger, error_msg, exc_info=None, context=None):
    """Log error with additional context information"""
    if context is None:
        context = {}
    
    error_details = {
        'error_message': str(error_msg),
        'context': context
    }
    
    if exc_info:
        error_details['traceback'] = traceback.format_exc()
    
    logger.error(f"Error occurred: {error_details}", exc_info=exc_info)