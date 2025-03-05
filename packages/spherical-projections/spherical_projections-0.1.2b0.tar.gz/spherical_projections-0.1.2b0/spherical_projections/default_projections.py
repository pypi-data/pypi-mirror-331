# /Users/robinsongarcia/projects/gnomonic/projection/default_projections.py

from .registry import ProjectionRegistry

from .gnomonic.config import GnomonicConfig
from .gnomonic.grid import GnomonicGridGeneration
from .gnomonic.strategy import GnomonicProjectionStrategy
from .gnomonic.transform import GnomonicTransformer  # Updated to per-projection transformer

from .mercator.config import MercatorConfig
from .mercator.grid import MercatorGridGeneration
from .mercator.strategy import MercatorProjectionStrategy
from .mercator.transform import MercatorTransformer  # Updated to per-projection transformer

from .base.interpolation import BaseInterpolation
from .exceptions import RegistrationError
import logging

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.default_projections')

def register_default_projections():
    """
    Register default projections with their components.

    Raises:
        RegistrationError: If registration of any default projection fails.
    """
    logger.debug("Registering default projections.")
    try:
        # Register Gnomonic projection
        ProjectionRegistry.register("gnomonic", {
            "config": GnomonicConfig,
            "grid_generation": GnomonicGridGeneration,
            "projection_strategy": GnomonicProjectionStrategy,
            "interpolation": BaseInterpolation,
            "transformer": GnomonicTransformer,  # Updated to GnomonicTransformer
        })
        logger.info("Default projection 'gnomonic' registered successfully.")

        # Register Mercator projection
        ProjectionRegistry.register("mercator", {
            "config": MercatorConfig,
            "grid_generation": MercatorGridGeneration,
            "projection_strategy": MercatorProjectionStrategy,
            "interpolation": BaseInterpolation,
            "transformer": MercatorTransformer,  # Updated to MercatorTransformer
        })


        logger.info("Default projection 'mercator' registered successfully.")

    except RegistrationError as e:
        logger.exception("Failed to register default projections.")
        raise RegistrationError(f"Failed to register default projections: {e}") from e
    except Exception as e:
        logger.exception("An unexpected error occurred while registering default projections.")
        raise RegistrationError(f"An unexpected error occurred: {e}") from e

    logger.debug("All default projections registered.")