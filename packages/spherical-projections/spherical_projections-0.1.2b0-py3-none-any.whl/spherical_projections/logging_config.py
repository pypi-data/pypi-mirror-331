import logging
import sys
import os

def setup_logging():
    """
    Set up logging configuration based on the DEBUG environment variable.
    """
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'  # Check if DEBUG is set to "true"

    logger = logging.getLogger('spherical_projections')

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    if debug_mode:
        logger.setLevel(logging.DEBUG)  # Enable detailed logging

        # Create handlers
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Console logs at INFO level

        file_handler = logging.FileHandler('spherical_projections.log')
        file_handler.setLevel(logging.DEBUG)  # File logs at DEBUG level

        # Create formatters and add them to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the main logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Ensure submodules propagate logs up
        logger.propagate = True

    else:
        logging.disable(logging.CRITICAL)  # Silence all logging

    return logger