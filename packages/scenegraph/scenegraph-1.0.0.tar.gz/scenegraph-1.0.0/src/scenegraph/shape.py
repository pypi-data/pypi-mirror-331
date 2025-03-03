"""
Interface class for geometries in space
"""


class Shape:
    def __init__(self):
        self.meta = {}

    def points(self):
        """Accessor to the points defining the shape.

        Returns:
            (list)
        """
        raise NotImplementedError

    def copy(self):
        """Copy of shape

        Returns:
            (Shape)
        """
        raise NotImplementedError

    def apply(self, matrix):
        """Apply transformation.

        Args:
            matrix (np.Array): (4,4) transformation matrix

        Returns:
            None
        """
        raise NotImplementedError
