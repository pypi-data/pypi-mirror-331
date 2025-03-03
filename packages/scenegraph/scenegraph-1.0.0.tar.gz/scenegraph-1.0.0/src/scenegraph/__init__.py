"""
Simple organisation of shapes in space
"""
# {# pkglts, src
# FYEO
# #}
# {# pkglts, version, after src
from . import version

__version__ = version.__version__
# #}

from .scene import Scene, ScNode
from .transfo import Rotation, RotationEuler, Scaling, Translation
from .triangle import Triangle
from .triangle_set import TriangleSet
