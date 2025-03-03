"""
Basic triangle primitive
"""
import numpy as np

from .shape import Shape


class Triangle(Shape):
    """Simple triangle in 3D space
    """

    def __init__(self, p0, p1, p2, internals=None):
        """Constructor

        Args:
            p0 (np.array): 3D point in space
            p1 (np.array): 3D point in space
            p2 (np.array): 3D point in space
            normal (np.array): Normal to triangle plane
            loc_distance (float): internal use only
        """
        super().__init__()

        self._corners = [p0, p1, p2]
        if internals is None:
            self._update_internals()
        else:
            self._normal, self._loc_distance = internals

    def _update_internals(self):
        p0, p1, p2 = self._corners
        self._normal = np.cross(p1 - p0, p2 - p0) / 2
        self._loc_distance = np.dot(self._normal, p0)

    def __getitem__(self, item):
        return self._corners[item]

    def points(self):
        """Accessor to the three corners of triangle.

        Returns:
            (list)
        """
        return self._corners

    def normal(self):
        return self._normal

    def loc_distance(self):
        return self._loc_distance

    def swap(self):
        """Swap two corners so that normal get inverted

        Returns:
            None
        """
        self._corners[0], self._corners[2], self._corners[1] = self._corners
        self._update_internals()

    def copy(self):
        """Copy of triangle

        Returns:
            (Triangle)
        """
        return Triangle(*[np.array(pt) for pt in self._corners], internals=(np.array(self._normal), self._loc_distance))

    def apply(self, matrix):
        """Apply transformation.

        Args:
            matrix (np.Array): (4,4) transformation matrix

        Returns:
            None
        """
        corners = []
        for pt in self._corners:
            vec = np.ones((4,))
            vec[:3] = pt
            vec = matrix.dot(vec)
            corners.append(vec[:3])

        self._corners = corners
        self._update_internals()
