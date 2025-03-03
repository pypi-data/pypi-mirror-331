"""Tests for the arithmetic module."""

import pytest
from mathutils.arithmetic import add, subtract, multiply, divide


def test_add():
    """Test the add function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(1.5, 2.5) == 4.0


def test_subtract():
    """Test the subtract function."""
    assert subtract(5, 3) == 2
    assert subtract(1, 1) == 0
    assert subtract(0, 5) == -5
    assert subtract(10.5, 0.5) == 10.0


def test_multiply():
    """Test the multiply function."""
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 5) == 0
    assert multiply(1.5, 2) == 3.0


def test_divide():
    """Test the divide function."""
    assert divide(6, 3) == 2
    assert divide(1, 1) == 1
    assert divide(0, 5) == 0
    assert divide(5, 2) == 2.5


def test_divide_by_zero():
    """Test that dividing by zero raises an error."""
    with pytest.raises(ZeroDivisionError):
        divide(5, 0) 