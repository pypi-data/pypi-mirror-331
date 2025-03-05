# /Users/robinsongarcia/projects/gnomonic/projection/gnomonic/grid.py

from typing import Any, Tuple
from ..base.grid import BaseGridGeneration
from .config import GnomonicConfig
from ..exceptions import GridGenerationError
import numpy as np
import logging

logger = logging.getLogger('spherical_projections.gnomonic_projection.gnomonic.grid')

class GnomonicGridGeneration(BaseGridGeneration):
    """
    Grid generation for the Gnomonic projection.
    """

    def projection_grid(self, delta_lat=0, delta_lon=0):
        """
        Generate the forward-projection grid (X, Y) for the Gnomonic projection.

        Returns:
            Tuple[np.ndarray, np.ndarray]: The X and Y coordinate grids for forward projection.
        """
        logger.debug("Generating Gnomonic projection grid.")
        half_fov_rad = np.deg2rad(self.config.fov_deg / 2)
        x_max = np.tan(half_fov_rad) * self.config.R
        y_max = np.tan(half_fov_rad) * self.config.R
        x_vals = np.linspace(-x_max, x_max, self.config.x_points)
        y_vals = np.linspace(-y_max, y_max, self.config.y_points)
        grid_x, grid_y = np.meshgrid(x_vals, y_vals)
        return grid_x, grid_y

    def spherical_grid(self, delta_lat=0, delta_lon=0):
        """
        Generate the (lon, lat) grid for backward projection.

        Returns:
            Tuple[np.ndarray, np.ndarray]: The longitude and latitude grids.
        """
        logger.debug("Generating Gnomonic spherical grid.")
        lon_vals = np.linspace(self.config.lon_min, self.config.lon_max, self.config.lon_points) + delta_lon
        lat_vals = np.linspace(self.config.lat_min, self.config.lat_max, self.config.lat_points) + delta_lat
        grid_lon, grid_lat = np.meshgrid(lon_vals, lat_vals)
        return grid_lon, grid_lat