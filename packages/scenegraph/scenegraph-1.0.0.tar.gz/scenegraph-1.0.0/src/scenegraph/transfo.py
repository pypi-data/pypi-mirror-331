"""
Spatial transformations
"""
from dataclasses import dataclass, field
from math import cos, sin
from typing import Union

import numpy as np


@dataclass
class Transfo:
    name: str = ""
    """Potential name for the instance of transfo.
    No test are done to ensure unicity in list of transfos of node.
    """

    def matrix(self):
        """Computes 4x4 matrix associated to this transfo

        Returns:
            (np.array)
        """
        raise NotImplementedError


@dataclass
class Translation(Transfo):
    vec: np.array = field(default_factory=lambda: np.zeros(3))
    """Translation vector
    """

    def __post_init__(self):
        if not isinstance(self.vec, np.ndarray):
            self.vec = np.array(self.vec)

    def matrix(self):
        ret = np.identity(4)
        ret[0:3, -1] = self.vec

        return ret


@dataclass
class Scaling(Transfo):
    vec: np.array = field(default_factory=lambda: np.ones(3))
    """Scaling vector (along each axis)
    """

    def __post_init__(self):
        if not isinstance(self.vec, np.ndarray):
            self.vec = np.array(self.vec)

    def matrix(self):
        ret = np.identity(4)
        for i in range(3):
            ret[i, i] = self.vec[i]

        return ret


@dataclass
class Rotation(Transfo):
    alpha: float = 0.
    """[rad] Oriented rotation angle around axis.
    """

    axis: Union[str, np.array] = 'Oz'
    """Axis of rotation
    Either a normalized vector or one of Ox, Oy, Oz
    """

    def __post_init__(self):
        if not isinstance(self.axis, str) and not isinstance(self.axis, np.ndarray):
            self.axis = np.array(self.axis)

    def matrix(self):
        if isinstance(self.axis, str):
            ret = np.identity(4)
            ca = cos(self.alpha)
            sa = sin(self.alpha)
            if self.axis == 'Ox':
                ret[1, 1] = ca
                ret[1, 2] = -sa
                ret[2, 1] = sa
                ret[2, 2] = ca
            elif self.axis == 'Oy':
                ret[2, 2] = ca
                ret[2, 0] = -sa
                ret[0, 2] = sa
                ret[0, 0] = ca
            elif self.axis == 'Oz':
                ret[0, 0] = ca
                ret[0, 1] = -sa
                ret[1, 0] = sa
                ret[1, 1] = ca
            else:
                raise UserWarning(f"Unrecognized axis descr '{self.axis}")
        else:  # np.array normalized vector
            x, y, z = self.axis
            ca = cos(self.alpha)
            sa = sin(self.alpha)
            ta = 1 - ca
            ret = np.array([
                [x * x * ta + ca, y * x * ta + z * sa, z * x * ta - y * sa, 0.],
                [x * y * ta - z * sa, y * y * ta + ca, z * y * ta + x * sa, 0.],
                [x * z * ta + y * sa, y * z * ta - x * sa, z * z * ta + ca, 0.],
                [0., 0., 0., 1.]
            ])

        return ret


@dataclass
class RotationEuler(Transfo):
    pitch: float = 0.
    """[rad] Oriented rotation angle around local vertical axis.
    """

    roll: float = 0.
    """[rad] Oriented rotation angle around local longitudinal axis.
    """

    yaw: float = 0.
    """[rad] Oriented rotation angle around local transversal axis.
    """

    def matrix(self):
        sp = np.sin(self.pitch)
        cp = np.cos(self.pitch)
        sr = np.sin(self.roll)
        cr = np.cos(self.roll)
        sy = np.sin(self.yaw)
        cy = np.cos(self.yaw)

        return np.array([
            # m1
            [
                cy * cp,
                -cy * sp * cr + sy * sr,
                cy * sp * sr + sy * cr,
                0.
            ],
            # m2
            [
                sp,
                cp * cr,
                -cp * sr,
                0.
            ],
            # m3
            [
                -sy * cp,
                sy * sp * cr + cy * sr,
                -sy * sp * sr + cy * cr,
                0.
            ],
            # bottom line
            [0., 0., 0., 1.]
        ])
