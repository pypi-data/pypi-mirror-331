# /Users/robinsongarcia/projects/gnomonic/projection/mercator/config.py

from typing import Any, Optional
from pydantic import BaseModel, Field
import cv2
import logging
from ..exceptions import ConfigurationError

logger = logging.getLogger('spherical_projections.projection.mercator.config')

class MercatorConfigModel(BaseModel):
    """
    Pydantic model for the Mercator projection.

    Attributes:
        R (float): Radius of the sphere.
        lon_min (float): Minimum longitude.
        lon_max (float): Maximum longitude.
        lat_min (float): Minimum latitude.
        lat_max (float): Maximum latitude.
        x_points (int): Number of points along the x-axis.
        y_points (int): Number of points along the y-axis.
        fov_deg (float): Field of view in degrees.
        interpolation (Optional[int]): Interpolation method for OpenCV remap.
        borderMode (Optional[int]): Border mode for OpenCV remap.
        borderValue (Optional[Any]): Border value for OpenCV remap.
    """
    R: float = Field(1., description="Radius of the sphere (in kilometers).")
    lon_min: float = Field(-180.0, description="Minimum longitude.")
    lon_max: float = Field(180.0, description="Maximum longitude.")
    lat_min: float = Field(-85.0, description="Minimum latitude (restricted for Mercator).")
    lat_max: float = Field(85.0, description="Maximum latitude (restricted for Mercator).")
    x_points: int = Field(1024, description="Number of points along the x-axis.")
    y_points: int = Field(512, description="Number of points along the y-axis.")
    lon_points: int = Field(1024, description="Number of longitude points for inverse grid mapping.")
    lat_points: int = Field(512, description="Number of latitude points for inverse grid mapping.")
    fov_deg: float = Field(90.0, description="Field of view in degrees")
    interpolation: Optional[int] = Field(default=cv2.INTER_LINEAR, description="Interpolation method for OpenCV remap")
    borderMode: Optional[int] = Field(default=cv2.BORDER_CONSTANT, description="Border mode for OpenCV remap")
    borderValue: Optional[Any] = Field(default=0, description="Border value for OpenCV remap")

class MercatorConfig:
    """
    Configuration class for Mercator projection.
    """

    def __init__(self, **kwargs):
        """
        Initialize the MercatorConfig with specified parameters.

        Args:
            **kwargs: Arbitrary keyword arguments for config parameters.

        Raises:
            ValueError: If initialization fails due to invalid configuration.
        """
        logger.debug("Initializing MercatorConfig with parameters: %s", kwargs)
        try:
            self.config = MercatorConfigModel(**kwargs)
        except Exception as e:
            logger.error("Failed to initialize MercatorConfig.")
            raise ValueError(f"Configuration error: {e}")

    def __repr__(self):
        """
        Return a string representation of the MercatorConfig.

        Returns:
            str: Stringified config dictionary.
        """
        return f"MercatorConfig({self.config.dict()})"

    def update(self, **kwargs: Any) -> None:
        """
        Dynamically update the Mercator configuration.

        Args:
            **kwargs (Any): Configuration parameters to update.

        Raises:
            ConfigurationError: If an error occurs during update.
        """
        logger.debug(f"Updating MercatorConfig with parameters: {kwargs}")
        try:
            updated_config = self.config.copy(update=kwargs)
            self.config = updated_config
            logger.info("MercatorConfig updated successfully.")
        except Exception as e:
            error_msg = f"Failed to update MercatorConfig: {e}"
            logger.exception(error_msg)
            raise ConfigurationError(error_msg) from e

    def __getattr__(self, item: str) -> Any:
        """
        Access configuration parameters as attributes.

        Args:
            item (str): Attribute name.

        Returns:
            Any: The value of the attribute if it exists.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        logger.debug(f"Accessing MercatorConfig attribute '{item}'.")
        try:
            return getattr(self.config, item)
        except AttributeError:
            error_msg = f"'MercatorConfig' object has no attribute '{item}'"
            logger.error(error_msg)
            raise AttributeError(error_msg) from None