"""
Portfolio Analysis Module

This module provides functions for:
- **Multi-Factor Analysis (MFA)**: Factor modeling, feature selection, clustering, and stress testing.

Submodules:
- `multi_factor_analysis`: Handles factor construction, feature selection, clustering, and stress analysis.
- `optimization`: Portfolio optimization functions (e.g., Markowitz, Black-Litterman models).

Imports:

- `run_multi_factor_analysis`: Full multi-factor analysis pipeline.

"""

from .optimization import *
from .multi_factor_analysis import *
__all__ = [
    "multi_factor_analysis",
    "optimization",
]
