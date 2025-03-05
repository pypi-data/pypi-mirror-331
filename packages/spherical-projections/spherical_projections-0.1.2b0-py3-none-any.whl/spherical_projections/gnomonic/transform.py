# /Users/robinsongarcia/projects/gnomonic/projection/gnomonic/transform.py

from typing import Tuple, Any
import numpy as np
import logging
from ..exceptions import TransformationError, ConfigurationError
from ..base.transform import BaseCoordinateTransformer

# Configure logger for the transformation module
logger = logging.getLogger('spherical_projections.gnomonic_projection.gnomonic.transform')

class GnomonicTransformer(BaseCoordinateTransformer):
    """
    Transformation Logic for Gnomonic Projection.

    The `GnomonicTransformer` class handles the conversion between geographic coordinates
    (latitude and longitude) and image coordinates on the Gnomonic projection plane.
    """

    def __init__(self, config):
        """
        Initialize the GnomonicTransformer with the given configuration.

        Args:
            config: Configuration object containing necessary projection parameters.
        """
        logger.debug("Initializing GnomonicTransformer.")
        required_attributes = [
            "lon_min",
            "lon_max",
            "lat_min",
            "lat_max",
            "fov_deg",
            "R",
            "x_points",
            "y_points"
        ]
        missing_attributes = [attr for attr in required_attributes if not hasattr(config, attr)]

        if missing_attributes:
            error_msg = f"Configuration object is missing required attributes: {', '.join(missing_attributes)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

        self.config = config
        logger.info("GnomonicTransformer initialized successfully.")

    def _validate_inputs(self, array: np.ndarray, name: str) -> None:
        """
        Validate input arrays to ensure they are NumPy arrays.

        Args:
            array (np.ndarray): Input array to validate.
            name (str): Name of the array for error messages.

        Raises:
            TransformationError: If the input is not a NumPy ndarray.
        """
        if not isinstance(array, np.ndarray):
            error_msg = f"{name} must be a NumPy ndarray."
            logger.error(error_msg)
            raise TransformationError(error_msg)

    def _compute_image_coords(
        self, values: np.ndarray, min_val: float, max_val: float, size: int
    ) -> np.ndarray:
        """
        Generalized method to compute normalized image coordinates.

        Args:
            values (np.ndarray): Input values to normalize (e.g., lat, lon, x, y).
            min_val (float): Minimum value for normalization.
            max_val (float): Maximum value for normalization.
            size (int): Size of the target axis.

        Returns:
            np.ndarray: Normalized image coordinates scaled to [0, size-1].
        """
        normalized = (values - min_val) / (max_val - min_val) * (size - 1)
        logger.debug(f"Computed normalized image coordinates.")
        return normalized

    def spherical_to_image_coords(
        self, lat: np.ndarray, lon: np.ndarray, shape: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert spherical coordinates (lat, lon) to image coordinates.

        Args:
            lat (np.ndarray): Array of latitude values.
            lon (np.ndarray): Array of longitude values.
            shape (Tuple[int, int]): Shape of the image (height, width).

        Returns:
            Tuple[np.ndarray, np.ndarray]: Image coordinates map_x, map_y.
        """
        logger.debug("Mapping spherical coordinates to image coordinates for Gnomonic projection.")
        H, W = shape  

        # Clamp extreme values if necessary (example only, logic unchanged)
        lon[lon>180] = -360 + lon[lon>180]
        lon[lon<-180] = 180 + (lon[lon<-180] + 180)
        lat[lat>90] = -180 + lat[lat>90]

        map_x = self._compute_image_coords(
            lon, self.config.lon_min, self.config.lon_max, W
        )
        map_y = self._compute_image_coords(
            lat, self.config.lat_max, self.config.lat_min, H
        )
        return map_x, map_y

    def projection_to_image_coords(
        self, x: np.ndarray, y: np.ndarray, config: Any
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert Gnomonic planar coordinates (x, y) to image coordinates.

        Args:
            x (np.ndarray): Planar X-coordinates.
            y (np.ndarray): Planar Y-coordinates.
            config (Any): Projection configuration object with fov_deg, R, etc.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Image coordinates map_x, map_y.
        """
        logger.debug("Mapping Gnomonic planar coordinates to image coordinates.")
        half_fov_rad = np.deg2rad(config.fov_deg / 2)
        x_max = np.tan(half_fov_rad) * config.R
        y_max = np.tan(half_fov_rad) * config.R
        x_min, y_min = -x_max, -y_max

        map_x = self._compute_image_coords(x, x_min, x_max, config.x_points)
        map_y = self._compute_image_coords(y, y_max, y_min, config.y_points)

        return map_x, map_y