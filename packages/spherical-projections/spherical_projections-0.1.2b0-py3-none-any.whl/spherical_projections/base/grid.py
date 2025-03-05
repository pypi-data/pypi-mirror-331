# /Users/robinsongarcia/projects/gnomonic/projection/base/grid.py

from typing import Any, Tuple
import numpy as np
import logging
from ..exceptions import GridGenerationError, ProcessingError

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.base.grid')

class BaseGridGeneration:
    """
    Base class for grid generation in projections.
    """

    def __init__(self, config):
        """
        Initialize the BaseGridGeneration with the given configuration.

        Args:
            config (Any): Projection configuration object.
        """
        logger.debug("Initializing BaseGridGeneration.")
        self.config = config

    def projection_grid(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Placeholder method to generate the grid for forward projection.

        Returns:
            Tuple[np.ndarray, np.ndarray]: The X and Y coordinate grids.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        logger.debug("projection_grid method called (Base class).")
        raise NotImplementedError("Subclasses must implement _create_grid.")