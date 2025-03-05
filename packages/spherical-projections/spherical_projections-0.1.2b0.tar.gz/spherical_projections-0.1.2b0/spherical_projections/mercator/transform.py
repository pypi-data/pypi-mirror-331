# /Users/robinsongarcia/projects/gnomonic/projection/mercator/transform.py

from typing import Tuple, Any
import numpy as np
import logging
from ..exceptions import TransformationError, ConfigurationError
from ..base.transform import BaseCoordinateTransformer

logger = logging.getLogger('spherical_projections.projection.mercator.transform')

class MercatorTransformer(BaseCoordinateTransformer):
    """
    Transformation logic for the Mercator projection.
    """

    def __init__(self, config):
        """
        Initialize the MercatorTransformer with the given configuration.

        Args:
            config: Configuration object with necessary parameters.

        Raises:
            ConfigurationError: If required attributes are missing.
        """
        logger.debug("Initializing MercatorTransformer.")
        required_attributes = ["lon_min", "lon_max", "lat_min", "lat_max", "x_points", "y_points"]
        missing_attributes = [attr for attr in required_attributes if not hasattr(config, attr)]

        if missing_attributes:
            error_msg = f"Configuration object is missing required attributes: {', '.join(missing_attributes)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

        self.config = config
        logger.info("MercatorTransformer initialized successfully.")

    def spherical_to_image_coords(
        self, lat: np.ndarray, lon: np.ndarray, shape: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert latitude and longitude to Mercator image coordinates.

        Args:
            lat (np.ndarray): Latitude values in degrees.
            lon (np.ndarray): Longitude values in degrees.
            shape (Tuple[int, int]): Shape of the target image (height, width).

        Returns:
            Tuple[np.ndarray, np.ndarray]: X and Y coordinates in image space.

        Raises:
            TransformationError: If input arrays are invalid or computation fails.
        """
        logger.debug("Transforming latitude and longitude to Mercator image coordinates.")
        try:
            if not isinstance(lat, np.ndarray) or not isinstance(lon, np.ndarray):
                raise TypeError("Latitude and longitude must be numpy arrays.")



            # Very simplistic placeholder logic (not a real Mercator transformation).
            x = lon
            y = lat
            map_x = ((x / np.pi) * .5 + .5) * (self.config.x_points - 1)
            map_y = (1 + -1*(( y / (np.pi/2) )* .5 + .5 ))* (self.config.y_points - 1)

            logger.debug("Latitude and longitude transformed successfully.")
            return map_x, map_y

        except Exception as e:
            logger.exception("Failed to transform latitude and longitude to Mercator image coordinates.")
            raise TransformationError(f"Mercator lat/lon transformation failed: {e}")

    def projection_to_image_coords(
        self, x: np.ndarray, y: np.ndarray, shape: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transform XY grid coordinates to Mercator image coordinates.

        Args:
            x (np.ndarray): X grid coordinates.
            y (np.ndarray): Y grid coordinates.
            shape (Tuple[int, int]): Shape of the target image (height, width).

        Returns:
            Tuple[np.ndarray, np.ndarray]: X and Y coordinates in image space.

        Raises:
            TransformationError: If input arrays are invalid or computation fails.
        """
        logger.debug("Transforming XY grid coordinates to Mercator image coordinates.")
        try:
            if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
                raise TypeError("Grid coordinates must be numpy arrays.")

            H = self.config.y_points
            W = self.config.x_points
            lon = x
            lat = y

            y_max = np.log(np.tan(np.pi / 4 + np.radians(self.config.config.lat_max) / 2))
            y_min = np.log(np.tan(np.pi / 4 + np.radians(self.config.config.lat_min) / 2))

            map_x = ((lon / np.radians(self.config.config.lon_max)) * .5 + .5) * (self.config.x_points)

            map_y = ((lat - y_min) / (y_max - y_min)) * self.config.y_points

            logger.debug("XY grid coordinates transformed successfully.")
            return map_x, map_y

        except Exception as e:
            logger.exception("Failed to transform XY grid coordinates to Mercator image coordinates.")
            raise TransformationError(f"Mercator XY transformation failed: {e}")