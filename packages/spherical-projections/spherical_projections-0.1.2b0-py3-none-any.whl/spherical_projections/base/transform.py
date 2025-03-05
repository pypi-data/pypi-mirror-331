# /Users/robinsongarcia/projects/gnomonic/projection/base/transform.py

from typing import Any, Tuple
import numpy as np
import logging
from ..exceptions import TransformationError, ConfigurationError

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.base.transform')

class BaseCoordinateTransformer:
    """
    Utility class for transforming coordinates between different systems.
    """

    def __init__(self, config) -> None:
        """
        Initialize the BaseCoordinateTransformer with a given configuration.

        Args:
            config: The configuration containing necessary projection parameters.
        """
        logger.debug("Initializing BaseCoordinateTransformer.")
        self.config = config

    @classmethod
    def spherical_to_image_coords(
        lat: np.ndarray, 
        lon: np.ndarray, 
        config: Any, 
        shape: Tuple[int, int, ...]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Placeholder method for converting spherical coordinates to image coordinates.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement forward.")

    @staticmethod
    def projection_to_image_coords(
        x: np.ndarray, 
        y: np.ndarray, 
        config: Any
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Placeholder method for converting projection coordinates to image coordinates.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement forward.")