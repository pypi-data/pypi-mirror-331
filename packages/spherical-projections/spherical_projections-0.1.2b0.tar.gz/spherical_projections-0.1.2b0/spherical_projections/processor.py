# /Users/robinsongarcia/projects/gnomonic/projection/processor.py

from typing import Any, Optional, Tuple
from .base.config import BaseProjectionConfig
from .exceptions import ProcessingError, InterpolationError, GridGenerationError, TransformationError
import logging
import cv2
import numpy as np
from .utils import PreprocessEquirectangularImage
# Initialize logger for this module
logger = logging.getLogger('spherical_projections.processor')

class ProjectionProcessor:
    """
    Processor for handling forward and backward projections using the provided configuration.
    """

    def __init__(self, config: BaseProjectionConfig) -> None:
        """
        Initialize the ProjectionProcessor with a given configuration.

        Args:
            config (BaseProjectionConfig): The projection configuration.

        Raises:
            TypeError: If 'config' is not an instance of BaseProjectionConfig.
            ProcessingError: If initialization of components fails.
        """
        logger.debug("Initializing ProjectionProcessor.")
        if not isinstance(config, BaseProjectionConfig):
            error_msg = f"config must be an instance of BaseProjectionConfig, got {type(config)} instead."
            logger.error(error_msg)
            raise TypeError(error_msg)

        self.config: BaseProjectionConfig = config
        try:
            self.projection = config.create_projection()
            self.grid_generation = config.create_grid_generation()
            self.interpolation = config.create_interpolation()
            self.transformer = config.create_transformer()  # Initialize transformer
            logger.info("ProjectionProcessor components initialized successfully.")
        except Exception as e:
            error_msg = f"Failed to initialize ProjectionProcessor components: {e}"
            logger.exception(error_msg)
            raise ProcessingError(error_msg) from e

    def forward(self, img: np.ndarray, **kwargs: Any) -> np.ndarray:
        """
        Forward projection of an image.

        Args:
            img (np.ndarray): The input equirectangular image.
            **kwargs (Any): Additional parameters to override projection configuration.

        Returns:
            np.ndarray: Projected rectilinear image.

        Raises:
            ValueError: If the input image is not a valid NumPy array.
            GridGenerationError: If grid generation fails.
            ProcessingError: If forward projection fails.
            TransformationError: If coordinate transformation fails.
            InterpolationError: If interpolation fails.
        """
        logger.debug("Starting forward projection.")
        if not isinstance(img, np.ndarray):
            error_msg = "Input image must be a NumPy ndarray."
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.config.update(**kwargs)
            logger.debug(f"Configuration updated with parameters: {kwargs}")

            img = PreprocessEquirectangularImage.preprocess(img, **kwargs)

            x_grid, y_grid = self.grid_generation.projection_grid()
            logger.debug("Forward grid generated successfully.")

            lat, lon = self.projection.from_projection_to_spherical(x_grid, y_grid)
            logger.debug("Forward projection computed successfully.")

            map_x, map_y = self.transformer.spherical_to_image_coords(lat, lon, img.shape[:2])
            logger.debug("Coordinates transformed to image space successfully.")

            projected_img = self.interpolation.interpolate(img, map_x, map_y)
            logger.info("Forward projection completed successfully.")
            return projected_img

        except (GridGenerationError, ProcessingError, TransformationError, InterpolationError) as e:
            logger.error(f"Forward projection failed: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during forward projection.")
            raise ProcessingError(f"Unexpected error during forward projection: {e}")

    def backward(self, rect_img: np.ndarray, return_mask: bool=False, **kwargs: Any) -> np.ndarray:
        """
        Backward projection of a rectilinear image to equirectangular.

        Args:
            rect_img (np.ndarray): The rectilinear image.
            **kwargs (Any): Additional parameters to override projection configuration.

        Returns:
            np.ndarray: Back-projected equirectangular image.

        Raises:
            ValueError: If the input image is not a valid NumPy array.
            GridGenerationError: If grid generation fails.
            ProcessingError: If backward projection fails.
            TransformationError: If coordinate transformation fails.
            InterpolationError: If interpolation fails.
        """
        logger.debug("Starting backward projection.")
        if not isinstance(rect_img, np.ndarray):
            error_msg = "Rectilinear image must be a NumPy ndarray."
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.config.update(**kwargs)
            logger.debug(f"Configuration updated with parameters: {kwargs}")
      
            lon_grid, lat_grid = self.grid_generation.spherical_grid()
            logger.debug("Backward grid generated successfully.")

            x, y, mask = self.projection.from_spherical_to_projection(lat_grid, lon_grid)
            logger.debug("Backward projection computed successfully.")

            map_x, map_y = self.transformer.projection_to_image_coords(x, y, self.config.config_object)
            logger.debug("Grid coordinates transformed to image space successfully.")

            back_projected_img = self.interpolation.interpolate(
                rect_img, map_x, map_y, mask if kwargs.get("return_mask", True) else None
            )
            logger.info("Backward projection completed successfully.")
            if return_mask:
                return cv2.flip(back_projected_img, 0), cv2.flip(mask * 1,0) == 1

            return cv2.flip(back_projected_img, 0)

        except (GridGenerationError, ProcessingError, TransformationError, InterpolationError) as e:
            logger.error(f"Backward projection failed: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during backward projection.")
            raise ProcessingError(f"Unexpected error during backward projection: {e}")