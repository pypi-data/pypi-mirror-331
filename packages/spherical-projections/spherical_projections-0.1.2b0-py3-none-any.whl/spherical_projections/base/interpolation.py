# /Users/robinsongarcia/projects/gnomonic/projection/base/interpolation.py

from typing import Any, Optional
import cv2
import numpy as np
import logging
from ..exceptions import InterpolationError

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.base.interpolation')

class BaseInterpolation:
    """
    Base class for image interpolation in projections.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize the interpolation with the given configuration.

        Args:
            config (Any): The projection configuration.

        Raises:
            TypeError: If 'config' does not have required attributes.
        """
        logger.debug("Initializing BaseInterpolation.")
        if not hasattr(config, "interpolation") or not hasattr(config, "borderMode") or not hasattr(config, "borderValue"):
            error_msg = "Config must have 'interpolation', 'borderMode', and 'borderValue' attributes."
            logger.error(error_msg)
            raise TypeError(error_msg)
        self.config: Any = config
        logger.info("BaseInterpolation initialized successfully.")

    def interpolate(
        self, 
        input_img: np.ndarray, 
        map_x: np.ndarray, 
        map_y: np.ndarray, 
        mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Perform image interpolation based on the provided mapping.

        Args:
            input_img (np.ndarray): The input image to interpolate.
            map_x (np.ndarray): The mapping for the x-coordinates.
            map_y (np.ndarray): The mapping for the y-coordinates.
            mask (Optional[np.ndarray], optional): Mask to apply to the interpolated image. Defaults to None.

        Returns:
            np.ndarray: The interpolated image.

        Raises:
            InterpolationError: If OpenCV remap fails or inputs are invalid.
        """
        logger.debug("Starting image interpolation.")
        if not isinstance(input_img, np.ndarray):
            error_msg = "input_img must be a NumPy ndarray."
            logger.error(error_msg)
            raise InterpolationError(error_msg)
        if not isinstance(map_x, np.ndarray) or not isinstance(map_y, np.ndarray):
            error_msg = "map_x and map_y must be NumPy ndarrays."
            logger.error(error_msg)
            raise InterpolationError(error_msg)

        try:
            map_x_32: np.ndarray = map_x.astype(np.float32)
            map_y_32: np.ndarray = map_y.astype(np.float32)
            logger.debug("map_x and map_y converted to float32 successfully.")
        except Exception as e:
            error_msg = f"Failed to convert map_x or map_y to float32: {e}"
            logger.exception(error_msg)
            raise InterpolationError(error_msg) from e

        try:
            result: np.ndarray = cv2.remap(
                input_img, map_x_32, map_y_32,
                interpolation=self.config.interpolation,
                borderMode=self.config.borderMode,
                borderValue=self.config.borderValue
            )
            logger.debug("OpenCV remap executed successfully.")
        except cv2.error as e:
            error_msg = f"OpenCV remap failed: {e}"
            logger.exception(error_msg)
            raise InterpolationError(error_msg) from e

        if mask is not None:
            logger.debug("Applying mask to interpolated image.")
            if not isinstance(mask, np.ndarray):
                error_msg = "mask must be a NumPy ndarray if provided."
                logger.error(error_msg)
                raise InterpolationError(error_msg)
            if mask.shape != result.shape[:2]:
                error_msg = "mask shape must match the first two dimensions of the result."
                logger.error(error_msg)
                raise InterpolationError(error_msg)
            result *= mask[:, :, None]
            logger.debug("Mask applied successfully.")

        logger.info("Image interpolation completed successfully.")
        return result