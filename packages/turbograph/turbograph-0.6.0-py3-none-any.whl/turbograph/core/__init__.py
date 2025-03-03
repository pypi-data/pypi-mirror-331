"""Core module for TurboGraph.

This package provides the fundamental abstractions, types, and utilities
for constructing and manipulating dependency graphs.
"""

from .constant import NA
from .specification import RawVertexSpecification, VertexSpecification

__all__ = ["NA", "RawVertexSpecification", "VertexSpecification"]
