"""PressureIQ - Batting Performance Under Pressure Engine Package.

Evaluates individual batter performance across pressure categories, benchmarks against
historical baselines, and computes the Batting Pressure Performance Index (BPPI).
"""

from __future__ import annotations

from src.batting_pressure.batting_pressure_config import (
    BattingPressureConfig,
    BattingPressureConfigError,
)
from src.batting_pressure.batting_pressure_metrics import (
    annotate_batting_deliveries,
    compute_batting_pressure_metrics,
)
from src.batting_pressure.pressure_category_aggregator import (
    assign_pressure_category,
    aggregate_by_pressure_category,
)
from src.batting_pressure.baseline_comparator import compare_with_baselines
from src.batting_pressure.situational_analyzer import analyze_situational_batting
from src.batting_pressure.bppi_calculator import calculate_bppi
from src.batting_pressure.batting_reliability import assess_batting_reliability
from src.batting_pressure.batter_classifier import classify_batters
from src.batting_pressure.explanation_generator import generate_batter_explanations
from src.batting_pressure.statistical_validation import validate_batting_pressure_datasets
from src.batting_pressure.batting_pressure_engine import calculate_batting_pressure_performance

__all__ = [
    "BattingPressureConfig",
    "BattingPressureConfigError",
    "annotate_batting_deliveries",
    "compute_batting_pressure_metrics",
    "assign_pressure_category",
    "aggregate_by_pressure_category",
    "compare_with_baselines",
    "analyze_situational_batting",
    "calculate_bppi",
    "assess_batting_reliability",
    "classify_batters",
    "generate_batter_explanations",
    "validate_batting_pressure_datasets",
    "calculate_batting_pressure_performance",
]

