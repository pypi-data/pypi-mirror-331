# /Users/robinsongarcia/projects/gnomonic/projection/base/config.py

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator
from ..base.interpolation import BaseInterpolation
from ..exceptions import ConfigurationError
import logging

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.base.config')

class BaseProjectionConfigModel(BaseModel):
    """
    Pydantic model holding basic projection configuration parameters.

    Attributes:
        interpolation (Optional[int]): Interpolation method for OpenCV remap.
        borderMode (Optional[int]): Border mode for OpenCV remap.
        borderValue (Optional[Any]): Border value for OpenCV remap.
    """
    interpolation: Optional[int] = Field(default=0, description="Interpolation method for OpenCV remap")
    borderMode: Optional[int] = Field(default=0, description="Border mode for OpenCV remap")
    borderValue: Optional[Any] = Field(default=0, description="Border value for OpenCV remap")

    class Config:
        arbitrary_types_allowed = True

class BaseProjectionConfig:
    """
    Base class for projections, allowing dynamic initialization with configuration objects.
    Utilizes Pydantic for configuration validation and management.
    """

    def __init__(self, config_object: Any) -> None:
        """
        Initialize the projection configuration.

        Args:
            config_object (Any): An object (e.g., GnomonicConfig) containing configuration parameters.

        Raises:
            ConfigurationError: If the configuration object does not have a 'config' attribute.
        """
        logger.debug("Initializing BaseProjectionConfig.")
        if not hasattr(config_object, "config"):
            error_msg = "Configuration object must have a 'config' attribute."
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        self.config_object: Any = config_object
        try:
            self.params: BaseProjectionConfigModel = config_object.config
            logger.debug("Configuration parameters loaded successfully.")
        except Exception as e:
            error_msg = f"Failed to load configuration parameters: {e}"
            logger.exception(error_msg)
            raise ConfigurationError(error_msg) from e
        self.extra_params: Dict[str, Any] = {}

    def create_projection(self) -> Any:
        """
        Placeholder for creating a projection object.
        Subclasses or dynamic creation logic should override this method.

        Raises:
            NotImplementedError: If the method is not overridden by subclasses.
        """
        logger.debug("create_projection method called.")
        raise NotImplementedError("Subclasses or configuration must implement create_projection.")

    def create_grid_generation(self) -> Any:
        """
        Placeholder for creating a grid generation object.
        Subclasses or dynamic creation logic should override this method.

        Raises:
            NotImplementedError: If the method is not overridden by subclasses.
        """
        logger.debug("create_grid_generation method called.")
        raise NotImplementedError("Subclasses or configuration must implement create_grid_generation.")

    def create_interpolation(self) -> BaseInterpolation:
        """
        Create an interpolation object using the configuration.

        Returns:
            BaseInterpolation: The interpolation object.
        """
        logger.debug("Creating interpolation object.")
        return BaseInterpolation(self)

    def create_transformer(self) -> Any:
        """
        Placeholder for creating a transformer object.

        Raises:
            NotImplementedError: If the method is not overridden by subclasses.
        """
        logger.debug("create_transformer method called.")
        raise NotImplementedError("Subclasses or configuration must implement create_transformer.")

    def update(self, **kwargs: Any) -> None:
        """
        Update configuration parameters dynamically.

        Args:
            **kwargs (Any): Parameters to update in the configuration.
        """
        logger.debug(f"Updating configuration with parameters: {kwargs}")
        for key, value in kwargs.items():
            if key in self.params.__fields__:
                try:
                    setattr(self.params, key, value)
                    logger.debug(f"Parameter '{key}' updated to {value}.")
                except Exception as e:
                    error_msg = f"Failed to update parameter '{key}': {e}"
                    logger.exception(error_msg)
                    raise ConfigurationError(error_msg) from e
            else:
                self.extra_params[key] = value
                logger.debug(f"Extra parameter '{key}' set to {value}.")

    def __getattr__(self, item: str) -> Any:
        """
        Access configuration parameters as attributes.

        Args:
            item (str): Parameter name.

        Returns:
            Any: The value of the parameter if it exists.

        Raises:
            AttributeError: If the parameter does not exist.
        """
        logger.debug(f"Accessing attribute '{item}'.")
        if hasattr(self.config_object, item):
            return getattr(self.config_object, item)
        if item in self.extra_params:
            return self.extra_params[item]
        error_msg = f"'{type(self).__name__}' object has no attribute '{item}'"
        logger.error(error_msg)
        raise AttributeError(error_msg)

    def __repr__(self) -> str:
        """
        String representation of the configuration.

        Returns:
            str: Human-readable string of configuration parameters.
        """
        return f"BaseProjectionConfig(params={self.params.dict()}, extra_params={self.extra_params})"