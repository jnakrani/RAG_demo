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

def setup_logging() -> logging.Logger:
    """
    Configure and initialize the logging system.

    Sets up logging with the following configuration:
    - Log Level: INFO
    - Format: timestamp - module - level - message
    - Handlers: 
        1. StreamHandler (console output)
        2. FileHandler (file output to 'qa_system.log')

    Returns:
        logging.Logger: Configured logger instance for the calling module
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('qa_system.log')
        ]
    )

    return logging.getLogger(__name__)