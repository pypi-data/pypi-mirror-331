"""MathUtils - A simple utility package for mathematical operations.

This package provides basic mathematical utilities including:
- Basic arithmetic operations
- Statistical functions
- Vector operations
"""

__version__ = "0.1.0"

from .arithmetic import add, subtract, multiply, divide
from .statistics import mean, median, mode, standard_deviation
from .vectors import dot_product, cross_product, magnitude

__all__ = [
    'add', 'subtract', 'multiply', 'divide',
    'mean', 'median', 'mode', 'standard_deviation',
    'dot_product', 'cross_product', 'magnitude'
] 