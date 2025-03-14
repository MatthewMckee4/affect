"""Affect is a Python library for building robust applications."""

from affect.core import Failure, Result, Success, is_err, is_ok
from affect.version import __version__

__all__ = ["Failure", "Result", "Success", "__version__", "is_err", "is_ok"]
