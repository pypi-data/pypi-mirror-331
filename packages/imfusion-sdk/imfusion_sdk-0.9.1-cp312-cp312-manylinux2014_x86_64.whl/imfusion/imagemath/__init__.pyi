"""

imfusion.imagemath - Bindings for ImageMath Operations  
======================================================

This module provides element-wise arithmetic operations for :class:`~imfusion.SharedImage` and :class:`~imfusion.SharedImageSet`. You can apply these :mod:`~imfusion.imagemath` functionalities directly to objects of :class:`~imfusion.SharedImage` and :class:`~imfusion.SharedImageSet` with eager evaluation. Alternatively, the module offers lazy evaluation functionality through the submodule :mod:`~imfusion.imagemath.lazy`. You can create wrapper expressions using the :class:`~imfusion.imagemath.lazy.Expression` provided by :mod:`~imfusion.imagemath.lazy`.

See :class:`~imfusion.imagemath.lazy.Expression` for details.

*Example for eager evaluation:*

>>> from imfusion import _bindings.imagemath as imagemath

Add `si1` and `si2`, which are :class:`~imfusion.SharedImage` instances:

>>> res = si1 + si2

`res` is a :class:`~imfusion.SharedImage` instance.

>>> print(res)
imfusion.SharedImage(FLOAT width: 512 height: 512)

*Example for lazy evaluation:*

>>> from imfusion import _bindings.imagemath as imagemath

Create expressions from :class:`~imfusion.SharedImage` instances:

>>> expr1 = imagemath.lazy.Expression(si1)
>>> expr2 = imagemath.lazy.Expression(si2)

Add `expr1` and `expr2`:

>>> expr3 = expr1 + expr2

Alternatively, you could add `expr1` and `si2` or `si1` and `expr2`. Any expression containing an instance of :class:`~imagemath.lazy.Expression` will be converted to lazy evaluation expression. 

>>> expr3 = expr1 + si2

Find the result with lazy evaluation: 

>>> res = expr3.evaluate()

`res` is a :class:`~imfusion.SharedImage` instance similar to eager evaluation case.

>>> print(res)
imfusion.SharedImage(FLOAT width: 512 height: 512)
"""
from __future__ import annotations
import imfusion._bindings
import numpy
import typing
from . import lazy
__all__ = ['absolute', 'add', 'arctan2', 'argmax', 'argmin', 'channel_swizzle', 'cos', 'divide', 'equal', 'exp', 'greater', 'greater_equal', 'lazy', 'less', 'less_equal', 'log', 'max', 'maximum', 'mean', 'min', 'minimum', 'multiply', 'negative', 'norm', 'not_equal', 'power', 'prod', 'sign', 'sin', 'sqrt', 'square', 'subtract', 'sum']
@typing.overload
def absolute(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Absolute value, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def absolute(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Absolute value, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def add(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def add(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def arctan2(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def arctan2(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def argmax(x: imfusion._bindings.SharedImage) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of maximum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def argmax(x: imfusion._bindings.SharedImageSet) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of maximum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def argmin(x: imfusion._bindings.SharedImage) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of minimum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def argmin(x: imfusion._bindings.SharedImageSet) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of minimum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def channel_swizzle(x: imfusion._bindings.SharedImage, indices: list[int]) -> imfusion._bindings.SharedImage:
    """
    Reorders the channels of an image based on the input indices, e.g. indices[0] will correspond to the first channel of the output image.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	indices (List[int]): List of channels indices to swizzle the channels of :class:`~imfusion.SharedImage`.
    """
@typing.overload
def channel_swizzle(x: imfusion._bindings.SharedImageSet, indices: list[int]) -> imfusion._bindings.SharedImageSet:
    """
    Reorders the channels of an image based on the input indices, e.g. indices[0] will correspond to the first channel of the output image.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	indices (List[int]): List of channels indices to swizzle the channels of :class:`~imfusion.SharedImageSet`.
    """
@typing.overload
def cos(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Cosine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def cos(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Cosine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def divide(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def divide(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def equal(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def exp(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Exponential operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def exp(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Exponential operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater_equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater_equal(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less_equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less_equal(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def log(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Natural logarithm, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def log(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Natural logarithm, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def max(x: imfusion._bindings.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the maximum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def max(x: imfusion._bindings.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the maximum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def maximum(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def maximum(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def mean(x: imfusion._bindings.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise average of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def mean(x: imfusion._bindings.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise average of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def min(x: imfusion._bindings.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the minimum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def min(x: imfusion._bindings.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the minimum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def minimum(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def minimum(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def multiply(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def multiply(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def negative(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Numerical negative, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def negative(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Numerical negative, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def norm(x: imfusion._bindings.SharedImage, order: typing.Any = 2) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Returns the norm of an image instance, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	order (int, float, 'inf'): Order of the norm. Default is L2 norm.
    """
@typing.overload
def norm(x: imfusion._bindings.SharedImageSet, order: typing.Any = 2) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Returns the norm of an image instance, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	order (int, float, 'inf'): Order of the norm. Default is L2 norm.
    """
@typing.overload
def not_equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def not_equal(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def not_equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def not_equal(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def not_equal(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def power(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def power(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def prod(x: imfusion._bindings.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise production of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def prod(x: imfusion._bindings.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise production of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sign(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Element-wise indication of the sign of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sign(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Element-wise indication of the sign of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sin(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Sine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sin(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Sine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sqrt(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Square-root operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sqrt(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Square-root operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def square(x: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Square operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def square(x: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Square operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: imfusion._bindings.SharedImage, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: imfusion._bindings.SharedImage, x2: float) -> imfusion._bindings.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def subtract(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: imfusion._bindings.SharedImageSet, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: imfusion._bindings.SharedImageSet, x2: float) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def subtract(x1: float, x2: imfusion._bindings.SharedImage) -> imfusion._bindings.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: float, x2: imfusion._bindings.SharedImageSet) -> imfusion._bindings.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sum(x: imfusion._bindings.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise sum of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sum(x: imfusion._bindings.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise sum of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
