from math import radians

import numpy as np
import pytest
from scenegraph.triangle import Triangle
from scenegraph.transfo import Rotation


def test_triangle_normal_is_correct():
    tr = Triangle(np.array([0, 0, 0]),
                  np.array([1, 0, 0]),
                  np.array([0, 1, 0]))

    n = tr.normal()

    assert np.sqrt(np.dot(n, n)) == pytest.approx(0.5, abs=1e-16)


def test_triangle_normal_is_opposite_to_swapped_triangle():
    tr = Triangle(np.array([0, 0, 0]),
                  np.array([1, 0, 0]),
                  np.array([0, 1, 0]))

    n = tr.normal()

    tr.swap()
    n_swap = tr.normal()

    assert np.dot(n, n_swap) == pytest.approx(-0.25, abs=1e-16)


def test_triangle_rotation_around_oz_not_too_bad():
    tr = Triangle(np.array([0, 0, 0]),
                  np.array([1, 0, 0]),
                  np.array([0, 1, 0]))

    n = np.array(tr.normal())

    tr.apply(Rotation(alpha=radians(40), axis="Oz").matrix())
    n_rot = np.array(tr.normal())

    assert np.dot(n, n_rot) == pytest.approx(0.25, abs=1e-16)
