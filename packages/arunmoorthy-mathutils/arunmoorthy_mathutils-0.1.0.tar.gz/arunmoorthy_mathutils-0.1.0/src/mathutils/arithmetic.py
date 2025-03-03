"""Basic arithmetic operations module.

This module provides simple arithmetic functions.
"""

def add(a, b):
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b


def subtract(a, b):
    """Subtract b from a.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The difference (a - b)
    """
    return a - b


def multiply(a, b):
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The product of a and b
    """
    return a * b


def divide(a, b):
    """Divide a by b.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        The quotient (a / b)
        
    Raises:
        ZeroDivisionError: If b is zero
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b 