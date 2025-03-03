"""Statistical functions module.

This module provides basic statistical operations.
"""

import math
from collections import Counter


def mean(numbers):
    """Calculate the arithmetic mean of a list of numbers.
    
    Args:
        numbers: List or tuple of numbers
        
    Returns:
        The arithmetic mean
        
    Raises:
        ValueError: If the input list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(numbers) / len(numbers)


def median(numbers):
    """Calculate the median of a list of numbers.
    
    Args:
        numbers: List or tuple of numbers
        
    Returns:
        The median value
        
    Raises:
        ValueError: If the input list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    
    if n % 2 == 0:
        # Even number of elements
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        # Odd number of elements
        return sorted_numbers[n//2]


def mode(numbers):
    """Calculate the mode (most common value) of a list of numbers.
    
    Args:
        numbers: List or tuple of numbers
        
    Returns:
        The mode value(s) as a list
        
    Raises:
        ValueError: If the input list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate mode of empty list")
    
    counts = Counter(numbers)
    max_count = max(counts.values())
    return [num for num, count in counts.items() if count == max_count]


def standard_deviation(numbers):
    """Calculate the standard deviation of a list of numbers.
    
    Args:
        numbers: List or tuple of numbers
        
    Returns:
        The standard deviation
        
    Raises:
        ValueError: If the input list has fewer than 2 elements
    """
    if len(numbers) < 2:
        raise ValueError("Standard deviation requires at least 2 values")
    
    avg = mean(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
    return math.sqrt(variance) 