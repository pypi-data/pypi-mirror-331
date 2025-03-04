from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pyvista as pv

from .base_cell import BASE_TOLERANCE, BaseCell
from .typedefs import Vector3D


@dataclass
class SphericalCell(BaseCell):
    """
    Represents a spherical cell in 3D space, centered around Z=0.

    Attributes:
        center (Tuple[float,float,float]): center coordinate of the sphere
        radius (float): Radius of the sphere
    """

    center: Tuple[float, float, float]
    radius: float

    def __post_init__(self):
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        # Precalculate values needed for is_point_inside method
        self._setup_containment_check()

    def _setup_containment_check(self):
        """
        Precalculates values needed for efficient point containment checks.
        """
        # Precalculate squared radius for more efficient distance checks
        self._radius_squared = self.radius**2

    def contains_point_fallback(
        self, x: float, y: float, z: float, tolerance: float = BASE_TOLERANCE
    ) -> bool:
        """
        Determines if a point (x, y, z) is inside the spherical cell.

        Args:
            x (float): X-coordinate of the point
            y (float): Y-coordinate of the point
            z (float): Z-coordinate of the point

        Returns:
            bool: True if the point is inside the sphere, False otherwise
        """
        # Calculate squared distance from point to center
        # Using squared distance avoids costly square root operation
        dx = x - self.center[0]
        dy = y - self.center[1]
        dz = z - self.center[2]
        distance_squared = dx * dx + dy * dy + dz * dz

        # Check if the point is within the radius of the sphere
        return distance_squared <= self._radius_squared

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
        Calculate the final position of a ray after reflections in a 3D spherical cell.

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
        pos = np.array([x1, y1, z1], dtype=float)
        # Direction vector
        direction = np.array([x2 - x1, y2 - y1, z2 - z1], dtype=float)

        # Normalize direction vector
        direction_length = np.sqrt(np.sum(direction**2))
        if direction_length < 1e-10:  # Avoid division by zero
            return (x1, y1, z1)

        direction = direction / direction_length

        center = np.array(self.center, dtype=float)

        for _ in range(max_iterations):
            # Skip if direction is zero
            if np.allclose(direction, 0):
                break

            # Calculate intersection with sphere
            oc = pos - center
            a = np.sum(direction**2)
            b = 2.0 * np.sum(oc * direction)
            c = np.sum(oc**2) - self._radius_squared

            discriminant = b**2 - 4 * a * c

            if discriminant < 0:
                # No intersection, ray doesn't hit sphere
                # Move in the direction vector
                pos += direction * direction_length
                break

            # Calculate the two possible intersection distances
            t0 = (-b - np.sqrt(discriminant)) / (2.0 * a)
            t1 = (-b + np.sqrt(discriminant)) / (2.0 * a)

            # Use the smallest positive t
            t = t1 if t0 < 0 else t0

            if t >= 1 or t < 0:
                # Complete move without hitting boundary
                pos += direction * direction_length
                break

            # Move to intersection point
            intersection = pos + direction * t * direction_length

            # Calculate normal at intersection point (pointing outward from sphere center)
            normal = (intersection - center) / self.radius
            normal = normal / np.sqrt(np.sum(normal**2))  # Normalize

            # Reflect direction vector around normal
            reflection = direction - 2 * np.sum(direction * normal) * normal

            # Update position to intersection point
            pos = intersection

            # Update direction to reflection
            direction = reflection

            # Scale remaining motion
            remaining_length = (1 - t) * direction_length
            direction_length = remaining_length

        return (pos[0], pos[1], pos[2])


def make_SphericalCell(
    center: Tuple[float, float, float], radius: float
) -> SphericalCell:
    return SphericalCell(
        mesh=pv.Sphere(radius=radius, center=center), center=center, radius=radius
    )


@dataclass
class SphericalCellParams:
    center: Vector3D
    radius: float

    @classmethod
    def validate_center(cls, value):
        if not isinstance(value, (list, tuple, np.ndarray)) or len(value) != 3:
            raise ValueError("center must be a 3D vector")

    @classmethod
    def validate_radius(cls, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("radius must be a positive number")
