# Understanding the Projection Process Conceptually

Projection systems map points from one coordinate space (e.g., spherical) to another (e.g., planar). This process transforms geographic or spherical coordinates (latitude and longitude) into Cartesian or image coordinates and vice versa. Below is a conceptual overview of projection design, focusing on creating a custom projection system.

---

## 1. The Core Idea of Projection

A projection maps points on a sphere (or ellipsoid) onto a flat surface.

- **Forward Projection**: Transforms from spherical coordinates \((\phi, \lambda)\), where \(\phi\) is latitude and \(\lambda\) is longitude, to Cartesian coordinates \((x, y)\).
- **Backward Projection**: Transforms from Cartesian coordinates \((x, y)\) back to spherical coordinates \((\phi, \lambda)\).

### Types of Projections
- **Gnomonic Projections**: Great circles are straight lines.
- **Mercator Projections**: Angles are preserved; used for navigation.
- **Lambert Projections**: Preserves either area or shape.

### Key Design Consideration
Identify which geometric property to preserve—shape, area, angles, or distances—and derive equations accordingly.

---

## 2. Key Components of a Projection

A projection system typically has three main components:

### a. Configuration
Defines the parameters for the projection, such as:
- **Field of View (FOV)**: Angular extent of the scene.
- **Resolution**: Grid point density in Cartesian space.
- **Reference Points**: Center of the projection (e.g., specific latitude and longitude).

### b. Grid Generation
Creates grids for:
- **Forward Projection**: Points in Cartesian space \((x, y)\).
- **Backward Projection**: Points in geographic space \((\phi, \lambda)\).

Example:
- Forward grid: Evenly spaced points on a flat plane.
- Backward grid: Evenly spaced points in latitude and longitude.

### c. Transformation Logic
Defines the mathematical transformation:
- **Forward Transformation**: Converts \((\phi, \lambda)\) to \((x, y)\).
- **Backward Transformation**: Converts \((x, y)\) to \((\phi, \lambda)\).

---

## 3. Designing the Forward Projection

The forward projection defines how Cartesian coordinates are derived from geographic ones.

### Mapping Equations
For a gnomonic projection:
$$
x = R \frac{\cos(\phi) \sin(\Delta\lambda)}{\cos(\phi_1)\cos(\phi) + \sin(\phi_1)\sin(\phi)\cos(\Delta\lambda)} 
\quad (6.1.1)
$$
$$
y = R \frac{\cos(\phi_1)\sin(\phi) - \sin(\phi_1)\cos(\phi)\cos(\Delta\lambda)}{\cos(\phi_1)\cos(\phi) + \sin(\phi_1)\sin(\phi)\cos(\Delta\lambda)}
\quad (6.1.2)
$$
Where:
- \(R\): Radius of the sphere.
- \(\phi_1, \lambda_0\): Latitude and longitude of the projection center.
- \(\Delta\lambda = \lambda - \lambda_0\): Longitude difference.

### Considerations
- **Singularities**: Handle undefined behavior at the poles or beyond 90° from the center.
- **Range Limits**: Define valid regions for the projection.

---

## 4. Designing the Backward Projection

The backward projection inverses the forward logic, mapping Cartesian coordinates back to geographic ones.

### Inverse Mapping Equations
For a gnomonic projection:
$$
\rho = \sqrt{x^2 + y^2} 
\quad (6.2.1)
$$
$$
\phi = \arcsin\left(\cos(c)\sin(\phi_1) + \frac{y\sin(c)\cos(\phi_1)}{\rho}\right) 
\quad (6.2.2)
$$
$$
\lambda = \lambda_0 + \arctan2\left(x\sin(c), \rho\cos(c)\cos(\phi_1) - y\sin(c)\sin(\phi_1)\right) 
\quad (6.2.3)
$$
Where:
- \(c = \arctan\left(\frac{\rho}{R}\right)\): Angular distance from the center.

### Masking and Clipping
Points outside valid geographic ranges (e.g., \(-90° \leq \phi \leq 90°\)) should be masked.

---

## 5. Practical Considerations

### Numerical Stability
- Avoid division by zero by adding small offsets.
- Handle edge cases gracefully.

### Performance
- Optimize grid computations using array-based operations (e.g., NumPy).
- Avoid loops for large grids.

### Interpolation
- Use interpolation for smooth image projection.
- Example: `cv2.remap` for pixel-wise transformation.

---

## 6. Building Your Own Projection

### Steps to Design
1. **Define the Purpose**: Decide the goal (e.g., preserving angles, distances, or area).
2. **Write the Equations**:
   - Forward transformation (\((x, y)\) to \((\phi, \lambda)\)).
   - Backward transformation (\((\phi, \lambda)\) to \((x, y)\)).
3. **Generate Grids**:
   - Create grids in Cartesian and geographic spaces for testing.
4. **Implement and Test**:
   - Validate transformations with known points (e.g., poles, equator).
   - Visualize the grid to confirm correct behavior.
5. **Handle Edge Cases**: Mask or clip invalid regions.

---

By understanding the mathematical and conceptual foundation of projections, you can design flexible systems to map coordinates effectively. The goal is to tailor projection equations to the specific needs of your application, balancing accuracy, performance, and usability.

1. Create Configuration Class

Define a configuration class for your new projection using Pydantic. This class ensures input validation and provides a structured way to manage projection parameters.
	•	File: projection/new_projection/config.py
	•	Expected Output: An instance of NewProjectionConfig containing validated configuration parameters.


```python
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger('gnomonic_projection.new_projection.config')

class NewProjectionConfigModel(BaseModel):
    param1: float = Field(1.0, description="Radius or scale factor for the projection.")
    param2: int = Field(100, description="Grid resolution or number of points.")

class NewProjectionConfig:
    """
    Configuration class for NewProjection projection.
    """

    def __init__(self, **kwargs):
        logger.debug("Initializing NewProjectionConfig with parameters: %s", kwargs)
        try:
            self.config = NewProjectionConfigModel(**kwargs)
        except Exception as e:
            logger.error("Failed to initialize NewProjectionConfig.")
            raise ValueError(f"Configuration error: {e}")

    def __repr__(self):
        return f"NewProjectionConfig({self.config.dict()})"
```
2. Create Grid Generation Class

Implement the grid generation logic to produce grids for the projection.
	•	File: projection/new_projection/grid.py
	•	Expected Output:
	•	Forward Grid: Two numpy.ndarray objects representing the X and Y coordinates of the grid.
	•	Backward Grid: Two numpy.ndarray objects representing longitude and latitude grids.
```python
from ..base.grid import BaseGridGeneration
import numpy as np
import logging

logger = logging.getLogger('gnomonic_projection.new_projection.grid')

class NewProjectionGridGeneration(BaseGridGeneration):
    """
    Grid generation for NewProjection.
    """

    def __init__(self, config):
        self.config = config

    def _create_grid(self, direction: str):
        if direction == 'forward':
            # Create a grid in Cartesian space
            x = np.linspace(-self.config.param1, self.config.param1, self.config.param2)
            y = np.linspace(-self.config.param1, self.config.param1, self.config.param2)
            grid_x, grid_y = np.meshgrid(x, y)
            return grid_x, grid_y  # (numpy.ndarray, numpy.ndarray)
        elif direction == 'backward':
            # Create a grid in geographic coordinates
            lon = np.linspace(-180, 180, self.config.param2)
            lat = np.linspace(-90, 90, self.config.param2)
            grid_lon, grid_lat = np.meshgrid(lon, lat)
            return grid_lon, grid_lat  # (numpy.ndarray, numpy.ndarray)
        else:
            raise ValueError("Invalid direction. Must be 'forward' or 'backward'.")

```

3. Create Projection Strategy

Define the mathematical transformation for your projection, converting between Cartesian and geographic coordinates.
	•	File: projection/new_projection/strategy.py
	•	Expected Output:
	•	Forward Method: Two numpy.ndarray objects for latitude (lat) and longitude (lon) values.
	•	Backward Method: Two numpy.ndarray objects for X and Y Cartesian coordinates, and one mask numpy.ndarray.

```python
from ..base.strategy import BaseProjectionStrategy
import numpy as np
import logging

logger = logging.getLogger('gnomonic_projection.new_projection.strategy')

class NewProjectionStrategy(BaseProjectionStrategy):
    """
    Projection strategy for NewProjection.
    """

    def forward(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Convert Cartesian coordinates to latitude and longitude.
        """
        lat = y / self.config.param1 * 90  # Example calculation
        lon = x / self.config.param1 * 180  # Example calculation
        return lat, lon  # (numpy.ndarray, numpy.ndarray)

    def backward(self, lat: np.ndarray, lon: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert latitude and longitude to Cartesian coordinates.
        """
        x = lon / 180 * self.config.param1  # Example calculation
        y = lat / 90 * self.config.param1  # Example calculation
        mask = (lat >= -90) & (lat <= 90) & (lon >= -180) & (lon <= 180)
        return x, y, mask  # (numpy.ndarray, numpy.ndarray, numpy.ndarray)
```
4. Update __init__.py for Your Projection Module

Ensure all your classes are imported and listed in __all__.
	•	File: projection/new_projection/__init__.py

```python
from .config import NewProjectionConfig
from .grid import NewProjectionGridGeneration
from .strategy import NewProjectionStrategy

__all__ = [
    "NewProjectionConfig",
    "NewProjectionGridGeneration",
    "NewProjectionStrategy",
]
```

5. Register Your Projection

Add the new projection to the system’s registry.
	•	File: projection/default_projections.py

```python
from .registry import ProjectionRegistry
from .new_projection.config import NewProjectionConfig
from .new_projection.grid import NewProjectionGridGeneration
from .new_projection.strategy import NewProjectionStrategy
from .base.interpolation import BaseInterpolation

def register_default_projections():
    # Register NewProjection
    ProjectionRegistry.register("new_projection", {
        "config": NewProjectionConfig,
        "grid_generation": NewProjectionGridGeneration,
        "projection_strategy": NewProjectionStrategy,
        "interpolation": BaseInterpolation,  # Optional
    })
```

