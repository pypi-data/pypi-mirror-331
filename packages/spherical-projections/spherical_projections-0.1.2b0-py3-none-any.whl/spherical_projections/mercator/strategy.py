# /Users/robinsongarcia/projects/gnomonic/projection/mercator/strategy.py

from ..base.strategy import BaseProjectionStrategy
import numpy as np
import logging

logger = logging.getLogger('spherical_projections.projection.mercator.strategy')

class MercatorProjectionStrategy(BaseProjectionStrategy):
    """
    Projection strategy for Mercator projection.
    """

    def __init__(self, config):
        """
        Initialize the MercatorProjectionStrategy with the given config.

        Args:
            config: A MercatorConfig instance.
        """
        logger.debug("Initializing MercatorProjectionStrategy.")
        self.config = config

    def from_projection_to_spherical(self, lon: np.ndarray, lat: np.ndarray):
        """
        Perform forward Mercator projection (not typical naming, but as per code).

        Args:
            lon (np.ndarray): Longitude values (radians).
            lat (np.ndarray): Latitude values for the projection (already transformed).

        Returns:
            Tuple[np.ndarray, np.ndarray]: The (lat, lon) in some form.
        """
        lon = lon / self.config.R
        lat =  np.pi / 2 - 2 * np.arctan(np.e**(lat/ self.config.R))
        logger.debug("Mercator forward projection computed successfully.")
        return lat, lon

    def from_spherical_to_projection(self, x: np.ndarray, y: np.ndarray):
        """
        Perform inverse Mercator projection (again, naming reversed in code).

        Args:
            x (np.ndarray): X coordinates (longitudes in degrees).
            y (np.ndarray): Y coordinates (latitudes in degrees).

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: The projected X, Y, and a mask.
        """
        logger.debug("Starting inverse Mercator projection (spherical to projection).")
        lon_rad = np.radians(x)
        lat_rad = np.radians(y)
        x = 1 * lon_rad
        y = 1 * np.log(np.tan(np.pi / 4 + lat_rad / 2))
        mask = np.ones_like(x) == 1
        logger.debug("Inverse Mercator projection computed successfully.")
        return x, y, mask