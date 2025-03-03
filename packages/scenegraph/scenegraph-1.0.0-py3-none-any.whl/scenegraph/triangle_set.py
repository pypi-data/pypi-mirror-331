import numpy as np

from .shape import Shape
from .triangle import Triangle


class TriangleSet(Shape):
    def __init__(self, points, faces, internals=None):
        super().__init__()
        self._points = points
        self._faces = faces
        if internals is None:
            self._update_internals()
        else:
            self._normals, self._loc_distances = internals

    def _update_internals(self):
        self._normals = []
        self._loc_distances = []
        for face in self._faces:
            tr = Triangle(*(self._points[pid] for pid in face))
            self._normals.append(tr.normal())
            self._loc_distances.append(tr.loc_distance())

    def __getitem__(self, item):
        return self._points[item]

    def __add__(self, other):
        trs = self.copy()
        nb = len(trs._points)
        trs._points += [np.array(pt) for pt in other.points()]
        trs._faces += [tuple(i + nb for i in inds) for inds in other.faces()]
        trs._normals.extend([np.array(vec) for vec in other._normals])
        trs._loc_distances.extend(other._loc_distances)

        return trs

    def points(self):
        """Accessor to the points defining the shape.

        Returns:
            (list)
        """
        return self._points

    def faces(self):
        """Accessor to the faces defining the shape.

        Returns:
            (list)
        """
        return self._faces

    def triangles(self):
        """Iterate over all faces and construct Triangle object

        Returns:
            (iter of Triangle)
        """
        for face, vec, d in zip(self._faces, self._normals, self._loc_distances):
            yield Triangle(*(self._points[pid] for pid in face), internals=(vec, d))

    def swap(self):
        """Swap two corners of each face so that normal get inverted

        Returns:
            None
        """
        self._faces = [(pid0, pid2, pid1) for pid0, pid1, pid2 in self._faces]
        self._update_internals()

    def copy(self):
        """Copy of shape

        Returns:
            (Shape)
        """
        return TriangleSet([np.array(pt) for pt in self._points],
                           [tuple(face) for face in self._faces],
                           internals=([np.array(vec) for vec in self._normals], list(self._loc_distances)))

    def apply(self, matrix):
        """Apply transformation.

        Args:
            matrix (np.Array): (4,4) transformation matrix

        Returns:
            None
        """
        points = []
        for pt in self._points:
            vec = np.ones((4,))
            vec[:3] = pt
            vec = matrix.dot(vec)
            points.append(vec[:3])

        self._points = points
        self._update_internals()


def bbox(xmin, ymin, zmin, xmax, ymax, zmax):
    """Construct axis aligned bounding box

    Notes:
      - cube side is equal to 1
      - cube normals are oriented outward

    Returns:
        (TriangleSet)
    """
    pts = [(xmin, ymin, zmin), (xmin, ymax, zmin), (xmax, ymax, zmin), (xmax, ymin, zmin),
           (xmin, ymin, zmax), (xmin, ymax, zmax), (xmax, ymax, zmax), (xmax, ymin, zmax)]

    faces = [(0, 1, 3), (1, 2, 3),
             (4, 7, 5), (5, 7, 6),
             (0, 3, 4), (7, 4, 3),
             (1, 0, 5), (4, 5, 0),
             (3, 2, 7), (6, 7, 2),
             (1, 5, 2), (6, 2, 5)]

    return TriangleSet([np.array(pt) for pt in pts], faces)


def cube():
    """Construct a unit cube centered around origin

    Notes:
      - cube side is equal to 1
      - cube normals are oriented outward

    Returns:
        (TriangleSet)
    """
    return bbox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
