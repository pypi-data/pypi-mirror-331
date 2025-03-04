"""
Multi-Factor Analysis (MFA) Module

This module provides functions for:
- Collecting historical financial data
- Constructing financial factors
- Selecting important features using ML
- Clustering assets into groups
- Training localized models per cluster
- Running stress & sensitivity analysis
"""

from .DataCollector import DataCollector
from .FactorConstructor import FactorConstructor
from .RandomForestFeatureSelector import RandomForestFeatureSelector
from .KMeansClusterer import KMeansClusterer
from .LocalizedModel import LocalizedModel
from .StressSensitivityAnalysis import StressAnalysis,SensitivityAnalysis
from .main import run_multi_factor_analysis
__all__ = [
    "DataCollector",
    "FactorConstructor",
    "RandomForestFeatureSelector",
    "KMeansClusterer",
    "LocalizedModel",
    "StressAnalysis",
    "SensitivityAnalysis",
    "run_multi_factor_analysis"
]
