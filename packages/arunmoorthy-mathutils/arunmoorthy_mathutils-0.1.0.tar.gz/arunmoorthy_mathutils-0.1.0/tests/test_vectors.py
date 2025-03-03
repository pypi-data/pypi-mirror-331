"""Tests for the vectors module."""

import pytest
import math
from mathutils.vectors import dot_product, cross_product, magnitude


def test_dot_product():
    """Test the dot product function."""
    assert dot_product([1, 2, 3], [4, 5, 6]) == 32
    assert dot_product([1, 0, 0], [0, 1, 0]) == 0  # Perpendicular vectors
    assert dot_product([2, 2], [3, 4]) == 14
    
    with pytest.raises(ValueError):
        dot_product([1, 2], [1, 2, 3])


def test_cross_product():
    """Test the cross product function."""
    assert cross_product([1, 0, 0], [0, 1, 0]) == [0, 0, 1]
    assert cross_product([2, 3, 4], [5, 6, 7]) == [-3, 6, -3]
    
    with pytest.raises(ValueError):
        cross_product([1, 2], [3, 4])
    
    with pytest.raises(ValueError):
        cross_product([1, 2, 3, 4], [5, 6, 7, 8])


def test_magnitude():
    """Test the magnitude function."""
    assert magnitude([3, 4]) == 5.0
    assert magnitude([1, 0, 0]) == 1.0
    assert magnitude([0, 0, 0]) == 0.0
    assert magnitude([1, 1, 1, 1]) == 2.0 