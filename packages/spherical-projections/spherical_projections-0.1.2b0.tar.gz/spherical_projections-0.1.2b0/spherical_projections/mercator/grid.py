# /Users/robinsongarcia/projects/gnomonic/projection/mercator/grid.py

from ..base.grid import BaseGridGeneration
import numpy as np
import logging

logger = logging.getLogger('spherical_projections.projection.mercator.grid')

class MercatorGridGeneration(BaseGridGeneration):
    """
    Grid generation for Mercator projection.
    """

    def projection_grid(self):
        """
        Generate the Mercator projection grid (lon, lat).

        Returns:
            Tuple[np.ndarray, np.ndarray]: The longitude and latitude grids for forward projection.
        """
        logger.debug("Generating Mercator projection grid.")
        y_max = np.log(np.tan(np.pi / 4 + np.radians(self.config.config.lat_max) / 2))
        y_min = np.log(np.tan(np.pi / 4 + np.radians(self.config.config.lat_min) / 2))
        lat = np.linspace(y_min, y_max, self.config.config.y_points)
        lon = np.linspace(self.config.config.lon_min, self.config.config.lon_max, self.config.config.x_points)
        lon = np.radians(lon)
        grid_lon, grid_lat = np.meshgrid(lon, lat)
        return grid_lon, grid_lat

    def spherical_grid(self):
        """
        Generate the grid for backward projection in Mercator projection.

        Returns:
            Tuple[np.ndarray, np.ndarray]: The X and Y coordinate grids (map_x, map_y).
        """
        logger.debug("Generating Mercator spherical grid.")
        x = np.linspace(self.config.config.lon_min, self.config.config.lon_max, self.config.config.lon_points)
        y = np.linspace(self.config.config.lat_max, self.config.config.lat_min, self.config.config.lat_points)
        map_y, map_x = np.meshgrid(x, y)
        return map_x, map_y