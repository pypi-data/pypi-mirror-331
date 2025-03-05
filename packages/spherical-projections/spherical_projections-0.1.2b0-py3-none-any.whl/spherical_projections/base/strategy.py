# /Users/robinsongarcia/projects/gnomonic/projection/base/strategy.py

from typing import Any, Tuple
import numpy as np
import logging
from ..exceptions import ProcessingError

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.base.strategy')

class BaseProjectionStrategy:
    """
    Base class for projection strategies.
    """

    @classmethod
    def from_spherical_to_projection(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform forward projection from grid coordinates to latitude and longitude.

        Args:
            x (np.ndarray): X-coordinates in the grid.
            y (np.ndarray): Y-coordinates in the grid.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Latitude and longitude arrays.

        Raises:
            ProcessingError: If inputs are not valid NumPy arrays or method is not overridden.
        """
        logger.debug("Starting forward projection in BaseProjectionStrategy.")
        if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
            error_msg = "x and y must be NumPy ndarrays."
            logger.error(error_msg)
            raise ProcessingError(error_msg)
        logger.debug("Forward projection inputs are valid.")
        raise NotImplementedError("Subclasses must implement forward.")

    @classmethod
    def from_projection_to_spherical(self, lat: np.ndarray, lon: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform backward projection from latitude and longitude to grid coordinates.

        Args:
            lat (np.ndarray): Latitude values.
            lon (np.ndarray): Longitude values.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: X and Y coordinates in the grid, and a mask array.

        Raises:
            ProcessingError: If inputs are not valid NumPy arrays or method is not overridden.
        """
        logger.debug("Starting backward projection in BaseProjectionStrategy.")
        if not isinstance(lat, np.ndarray) or not isinstance(lon, np.ndarray):
            error_msg = "lat and lon must be NumPy ndarrays."
            logger.error(error_msg)
            raise ProcessingError(error_msg)
        logger.debug("Backward projection inputs are valid.")
        raise NotImplementedError("Subclasses must implement backward.")