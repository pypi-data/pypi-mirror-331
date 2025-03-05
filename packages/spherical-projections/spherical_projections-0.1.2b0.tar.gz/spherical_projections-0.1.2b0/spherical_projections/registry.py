# /Users/robinsongarcia/projects/gnomonic/projection/registry.py

from typing import Any, Dict, Optional, Type, Union
from .base.config import BaseProjectionConfig
from .processor import ProjectionProcessor
from .exceptions import RegistrationError
import logging

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.registry')

class ProjectionRegistry:
    """
    Registry for managing projection configurations and their components.
    """
    _registry: Dict[str, Dict[str, Type[Any]]] = {}

    @classmethod
    def register(cls, name: str, components: Dict[str, Type[Any]]) -> None:
        """
        Register a projection with its required components.

        Args:
            name (str): Name of the projection (e.g., 'gnomonic').
            components (Dict[str, Type[Any]]): A dictionary containing:
                - 'config': Configuration class
                - 'grid_generation': Grid generation class
                - 'projection_strategy': Projection strategy class
                - 'interpolation' (optional): Interpolation class
                - 'transformer': Transformation class (optional)

        Raises:
            RegistrationError: If required components are missing or invalid.
        """
        logger.debug(f"Attempting to register projection '{name}' with components: {list(components.keys())}")
        required_keys = {"config", "grid_generation", "projection_strategy"}
        missing_keys = required_keys - components.keys()
        if missing_keys:
            error_msg = f"Components must include {required_keys}. Missing keys: {missing_keys}"
            logger.error(error_msg)
            raise RegistrationError(error_msg)

        for key in ["interpolation", "transformer"]:
            if key in components:
                if not isinstance(components[key], type):
                    error_msg = f"'{key}' component must be a class type."
                    logger.error(error_msg)
                    raise RegistrationError(error_msg)
                logger.debug(f"'{key}' component validated as a class type.")

        cls._registry[name] = components
        logger.info(f"Projection '{name}' registered successfully.")

    @classmethod
    def get_projection(
        cls, 
        name: str, 
        return_processor: bool = False, 
        **kwargs: Any
    ) -> Union[BaseProjectionConfig, ProjectionProcessor]:
        """
        Retrieve a configured projection by name.

        Args:
            name (str): Name of the projection to retrieve.
            return_processor (bool): Whether to return the processor instead of the config.
            **kwargs (Any): Configuration parameters to override defaults.

        Returns:
            Union[BaseProjectionConfig, ProjectionProcessor]: Depending on `return_processor`.

        Raises:
            RegistrationError: If the projection name is not found or components are missing.
        """
        logger.debug(f"Retrieving projection '{name}' with override parameters: {kwargs}")
        if name not in cls._registry:
            error_msg = f"Projection '{name}' not found in the registry."
            logger.error(error_msg)
            raise RegistrationError(error_msg)

        components = cls._registry[name]
        try:
            ConfigClass = components["config"]
            GridGenerationClass = components["grid_generation"]
            ProjectionStrategyClass = components["projection_strategy"]
            InterpolationClass = components.get("interpolation", None)
            TransformerClass = components.get("transformer", None)
            logger.debug(f"Components for projection '{name}': {list(components.keys())}")
        except KeyError as e:
            error_msg = f"Missing component in the registry: {e}"
            logger.error(error_msg)
            raise RegistrationError(error_msg) from e

        # Instantiate the configuration object
        try:
            config_instance = ConfigClass(**kwargs)
            logger.debug(f"Configuration instance for projection '{name}' created successfully.")
        except Exception as e:
            error_msg = f"Failed to instantiate config class '{ConfigClass.__name__}': {e}"
            logger.exception(error_msg)
            raise RegistrationError(error_msg) from e

        # Create a BaseProjectionConfig and attach the necessary methods
        base_config = BaseProjectionConfig(config_instance)
        base_config.create_projection = lambda: ProjectionStrategyClass(config_instance)
        base_config.create_grid_generation = lambda: GridGenerationClass(config_instance)
        if InterpolationClass:
            base_config.create_interpolation = lambda: InterpolationClass(config_instance)
        if TransformerClass:
            base_config.create_transformer = lambda: TransformerClass(config_instance)

        if return_processor:
            logger.debug(f"Returning ProjectionProcessor for projection '{name}'.")
            return ProjectionProcessor(base_config)

        logger.debug(f"Returning BaseProjectionConfig for projection '{name}'.")
        return base_config

    @classmethod
    def list_projections(cls) -> list:
        """
        List all registered projections.

        Returns:
            list: A list of projection names.
        """
        logger.debug("Listing all registered projections.")
        projections = list(cls._registry.keys())
        logger.info(f"Registered projections: {projections}")
        return projections