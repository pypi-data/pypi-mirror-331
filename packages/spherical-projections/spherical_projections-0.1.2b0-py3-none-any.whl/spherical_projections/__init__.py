# /Users/robinsongarcia/projects/gnomonic/projection/__init__.py

"""
Gnomonic Projection Package

This package provides functionalities for gnomonic projections,
including registry management and default projection registration.
"""

from .registry import ProjectionRegistry
from .default_projections import register_default_projections
from .logging_config import setup_logging

# Set up logging
logger = setup_logging()
logger.info("Initializing Gnomonic Projection Package")

# Automatically register default projections
try:
    register_default_projections()
    logger.info("Default projections registered successfully.")
except Exception as e:
    logger.exception("Failed to register default projections.")
    raise RuntimeError("Failed to register default projections.") from e

__all__ = ["ProjectionRegistry"]