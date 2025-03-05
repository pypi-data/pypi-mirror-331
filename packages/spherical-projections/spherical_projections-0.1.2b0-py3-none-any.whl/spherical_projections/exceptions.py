# /Users/robinsongarcia/projects/gnomonic/projection/exceptions.py

"""
Custom exception classes for the Gnomonic Projection module.
"""

class ProjectionError(Exception):
    """Base exception for projection-related errors."""
    pass

class ConfigurationError(ProjectionError):
    """Exception raised for configuration-related issues."""
    pass

class RegistrationError(ProjectionError):
    """Exception raised during projection registration."""
    pass

class ProcessingError(ProjectionError):
    """Exception raised during projection processing."""
    pass

class GridGenerationError(ProjectionError):
    """Exception raised during grid generation."""
    pass

class TransformationError(ProjectionError):
    """Exception raised during coordinate transformations."""
    pass

class InterpolationError(ProjectionError):
    """Exception raised during image interpolation."""
    pass