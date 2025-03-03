"""Tests for the statistics module."""

import pytest
from mathutils.statistics import mean, median, mode, standard_deviation


def test_mean():
    """Test the mean function."""
    assert mean([1, 2, 3, 4, 5]) == 3
    assert mean([0, 0, 0]) == 0
    assert mean([1.5, 2.5, 3.5]) == 2.5
    
    with pytest.raises(ValueError):
        mean([])


def test_median():
    """Test the median function."""
    # Odd number of elements
    assert median([1, 3, 2, 5, 4]) == 3
    # Even number of elements
    assert median([1, 2, 3, 4]) == 2.5
    # Single element
    assert median([5]) == 5
    
    with pytest.raises(ValueError):
        median([])


def test_mode():
    """Test the mode function."""
    # Single mode
    assert mode([1, 2, 2, 3]) == [2]
    # Multiple modes
    assert sorted(mode([1, 1, 2, 2, 3])) == [1, 2]
    # All values appear once
    assert sorted(mode([1, 2, 3])) == [1, 2, 3]
    
    with pytest.raises(ValueError):
        mode([])


def test_standard_deviation():
    """Test the standard deviation function."""
    assert standard_deviation([2, 4, 4, 4, 5, 5, 7, 9]) == 2.0
    assert standard_deviation([1, 1, 1, 1]) == 0.0
    
    with pytest.raises(ValueError):
        standard_deviation([])
    
    with pytest.raises(ValueError):
        standard_deviation([1]) 