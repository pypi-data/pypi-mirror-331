"""
macro-gridder - A library for real-time macro grid calculation for stock data
"""

from .core import MacroGridder, compute_recommended_vertical_steps
from .realtime import RealtimeMacroGridder

__version__ = "0.1.0"
__all__ = ["MacroGridder", "RealtimeMacroGridder", "compute_recommended_vertical_steps"]
