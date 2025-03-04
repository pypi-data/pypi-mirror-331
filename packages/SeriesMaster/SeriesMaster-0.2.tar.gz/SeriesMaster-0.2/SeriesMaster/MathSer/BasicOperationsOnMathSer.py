import warnings
from math import gcd  
from functools import reduce  
import SeriesMaster.MathSer.BasicOperationsOnMathSer as BasicOperationsOnMathSer  # type:ignore

"""
BasicOperationsOnMathSer

This module provides functions to perform element-wise arithmetic operations
on two instances of MathSer Series.Ser.

Functions:
    Subtract(ser1, ser2) -> list:
        Returns a new list where each element is the result of subtracting the 
        corresponding element of ser2 from ser1.
    
    Add(ser1, ser2) -> list:
        Returns a new list where each element is the sum of the corresponding 
        elements of ser1 and ser2.
    
    Multiply(ser1, ser2) -> list:
        Returns a new list where each element is the product of the corresponding 
        elements of ser1 and ser2.
    
    Divide(ser1, ser2) -> list:
        Returns a new list where each element is the result of dividing the 
        corresponding element of ser1 by ser2. Raises a ValueError if division by zero occurs.
    
    Percentage(inp) -> list:
        Computes the percentage change between consecutive elements in the input sequence.
    
    Frac(inp) -> str:
        Returns the percentage change as a fraction out of 100.
    
    Deci(inp) -> float:
        Returns the percentage change in decimal form.
"""

def Subtract(ser1, ser2):
    """
    Performs element-wise subtraction between the two MathSer Series.
    
    Args:
        ser1: First MathSer Series instance.
        ser2: Second MathSer Series instance.
    
    Returns:
        list: A new list where each element is (ser1[i] - ser2[i]).
    """
    return [ser1.ser[i] - ser2.ser[i] for i in range(len(ser1.ser))]

def Add(ser1, ser2):
    """
    Performs element-wise addition of the two MathSer Series.
    
    Args:
        ser1: First MathSer Series instance.
        ser2: Second MathSer Series instance.
    
    Returns:
        list: A new list where each element is (ser1[i] + ser2[i]).
    """
    return [ser1.ser[i] + ser2.ser[i] for i in range(len(ser1.ser))]

def Multiply(ser1, ser2):
    """
    Performs element-wise multiplication of the two MathSer Series.
    
    Args:
        ser1: First MathSer Series instance.
        ser2: Second MathSer Series instance.
    
    Returns:
        list: A new list where each element is (ser1[i] * ser2[i]).
    """
    return [ser1.ser[i] * ser2.ser[i] for i in range(len(ser1.ser))]

def Divide(ser1, ser2):
    """
    Performs element-wise division of the two MathSer Series.
    
    Args:
        ser1: First MathSer Series instance.
        ser2: Second MathSer Series instance.
    
    Returns:
        list: A new list where each element is (ser1[i] / ser2[i]).
    
    Raises:
        ValueError: If any element in ser2 is zero.
    """
    if 0 in ser2.ser:
        raise ValueError('Cannot divide by 0')
    return [ser1.ser[i] / ser2.ser[i] for i in range(len(ser1.ser))]

def Percentage(inp):
    """
    Computes the percentage change between consecutive elements in the input sequence.
    
    Args:
        inp (list): A list of numerical values.
    
    Returns:
        list: A list containing percentage changes between consecutive elements.
    """
    inp = list(inp)
    return [((inp[i + 1] / inp[i]) - 1) * 100 for i in range(len(inp) - 1)]

def Frac(inp):
    """
    Returns the percentage change as a fraction out of 100.
    
    Args:
        inp (list): A list of numerical values.
    
    Returns:
        str: A fraction representation of the percentage change.
    """
    return str(Percentage(inp)) + "/100"

def Deci(inp):
    """
    Returns the percentage change in decimal form.
    
    Args:
        inp (list): A list of numerical values.
    
    Returns:
        float: The percentage change in decimal form.
    """
    return [p / 100 for p in Percentage(inp)]