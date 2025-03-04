from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pyvista as pv

from .base_cell import BASE_TOLERANCE, BaseCell


@dataclass
class RectangularCell(BaseCell):
    """
    Represents a rectangular cell in 3D space.

    Attributes:
        bounds (np.ndarray):
            [[xmin,xmax],[ymin,ymax],[zmin,zmax]]
    """

    bounds: np.ndarray

    def contains_point_fallback(
        self, x: float, y: float, z: float, tolerance: float = BASE_TOLERANCE
    ) -> bool:
        """
        Determines if a point (x, y, z) is inside the rectangular cell.

        Args:
            x (float): X-coordinate of the point
            y (float): Y-coordinate of the point
            z (float): Z-coordinate of the point

        Returns:
            bool: True if the point is inside the ovoid, False otherwise
        """
        # Convert single values to a point vector
        point = np.array([x, y, z])
        for i in range(len(point)):
            if (point[i] < self.bounds[i]) or (point[i] > self.bounds[i + 1]):
                return False
        return True

    def reflecting_point(
        self,
        x1: float,
        y1: float,
        z1: float,
        x2: float,
        y2: float,
        z2: float,
        max_iterations: int = 5,
    ) -> Tuple[float, float, float]:
        """
        Calculate the final position of a ray after reflections in a 3D rectangular box.

        Args:
            x1, y1, z1: Coordinates of the starting point
            x2, y2, z2: Coordinates of the initial direction point
            max_iterations: Maximum number of reflections to calculate

        Returns:
            Tuple[float, float, float]: The final position after reflections
        """
        if self.contains_point_fallback(x2, y2, z2) and self.contains_point_fallback(
            x1, y1, z1
        ):
            return (x2, y2, z2)
        # Current position
        pos = [x1, y1, z1]

        # Direction vector
        delta = [x2 - x1, y2 - y1, z2 - z1]

        # Extract bounds
        mins = [self.bounds[0], self.bounds[2], self.bounds[4]]  # x_min, y_min, z_min
        maxs = [self.bounds[1], self.bounds[3], self.bounds[5]]  # x_max, y_max, z_max

        for _ in range(max_iterations):
            if all(d == 0 for d in delta):
                break

            for dim in range(3):
                d = delta[dim]
                if d == 0:
                    continue

                # Calculate distances to both boundaries
                dist_to_min = (mins[dim] - pos[dim]) / d if d < 0 else float("inf")
                dist_to_max = (maxs[dim] - pos[dim]) / d if d > 0 else float("inf")

                # Find closest boundary
                dist = min(dist_to_min, dist_to_max)

                if dist < 1:  # Will hit boundary before completing move
                    # Move to boundary
                    for i in range(3):
                        pos[i] += delta[i] * dist

                    # Reflect only the dimension that hit
                    delta[dim] = -delta[dim]

                    # Scale remaining motion
                    for i in range(3):
                        delta[i] *= 1 - dist
                    break
                else:  # Complete move without hitting boundary
                    for i in range(3):
                        pos[i] += delta[i]
                    delta = [0, 0, 0]

        return tuple(pos)


def make_RectangularCell(bounds: np.ndarray) -> RectangularCell:
    """
    Parameters:
    -----------
    bounds (np.ndarray):
        [[xmin,xmax],[ymin,ymax],[zmin,zmax]]

    Returns:
    --------
    RectangularCell object
    """

    pv_bounds = np.asarray(bounds).flatten()
    rec = pv.Box(bounds=pv_bounds)
    return RectangularCell(mesh=rec, bounds=bounds)


@dataclass
class RectangularCellParams:
    bounds: np.ndarray

    @classmethod
    def validate_bounds(cls, value):
        if not isinstance(value, (list, tuple, np.ndarray)):
            raise ValueError("bounds must be an array-like object")

        # Convert to numpy array if needed
        if not isinstance(value, np.ndarray):
            value = np.array(value)

        # Check shape
        if value.shape != (3, 2):
            raise ValueError("bounds must be a 3x2 array (min and max points)")

        # Check min < max
        for i in range(3):
            if value[i, 0] >= value[i, 1]:
                raise ValueError(
                    f"Min bound must be less than max bound for dimension {i}"
                )
