# /Users/robinsongarcia/projects/gnomonic/projection/gnomonic/__init__.py

"""
Gnomonic Projection Module

This module provides specific implementations for Gnomonic projections,
including configuration, projection strategies, and grid generation.

## Mathematical Foundation

The Gnomonic projection transforms points on the surface of a sphere (e.g., Earth)
onto a plane using a projection point located at the center of the sphere.
This projection is based on the principles of spherical trigonometry and can be
derived using the following key equations:

1. **Projection Equations:** (See inline formulas in the docstring)

2. **Special Cases:** 
   Polar Gnomonic Projection examples and usage.

The Gnomonic projection is particularly useful for mapping great circles as straight lines,
which is advantageous in navigation and aeronautics.

## Projection Processes

1. **Forward Projection:** 
   Maps points from an equirectangular (input) image to the Gnomonic projection plane.

2. **Backward Projection:**
   Maps points from the Gnomonic projection plane back to an equirectangular (output) image.

## Usage

See the example usage in the docstring below.
"""

import logging

from .config import GnomonicConfig
from .strategy import GnomonicProjectionStrategy
from .grid import GnomonicGridGeneration
from .transform import GnomonicTransformer
from ..logging_config import setup_logging

# Initialize logger for this module
logger = logging.getLogger('spherical_projections.gnomonic_projection.gnomonic')

def initialize_gnomonic_module():
    """
    Initialize the Gnomonic Projection module.

    This initialization sets up any module-specific configurations or prerequisites.
    Currently, it primarily logs the initialization status.
    """
    logger.debug("Initializing Gnomonic Projection Module.")
    # Any module-specific initialization can be done here
    logger.info("Gnomonic Projection Module initialized successfully.")

# Call the initialization function upon import
initialize_gnomonic_module()

__all__ = [
    "GnomonicConfig",
    "GnomonicProjectionStrategy",
    "GnomonicGridGeneration",
    "GnomonicTransformer"
]