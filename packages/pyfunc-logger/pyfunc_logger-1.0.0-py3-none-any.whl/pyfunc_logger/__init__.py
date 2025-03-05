"""
PyFunc Logger - Function call logging with precise timing for Python

A lightweight, easy-to-use function logging package that tracks function calls,
arguments, execution times, and return values.
"""

from .logger import log_function, get_logger, FunctionLogger

__version__ = "1.0.0"
__all__ = ["log_function", "get_logger", "FunctionLogger"]
