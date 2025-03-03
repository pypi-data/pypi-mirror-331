"""Vector operations module.

This module provides basic vector operations for 3D vectors.
"""

import math


def dot_product(v1, v2):
    """Calculate the dot product of two vectors.
    
    Args:
        v1: First vector as a list or tuple of numbers
        v2: Second vector as a list or tuple of numbers
        
    Returns:
        The dot product of v1 and v2
        
    Raises:
        ValueError: If vectors have different dimensions
    """
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension")
    
    return sum(a * b for a, b in zip(v1, v2))


def cross_product(v1, v2):
    """Calculate the cross product of two 3D vectors.
    
    Args:
        v1: First vector as a list or tuple of 3 numbers
        v2: Second vector as a list or tuple of 3 numbers
        
    Returns:
        The cross product of v1 and v2 as a list
        
    Raises:
        ValueError: If either vector is not 3-dimensional
    """
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Cross product requires 3D vectors")
    
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]


def magnitude(vector):
    """Calculate the magnitude (length) of a vector.
    
    Args:
        vector: A vector as a list or tuple of numbers
        
    Returns:
        The magnitude of the vector
    """
    return math.sqrt(sum(x * x for x in vector)) 