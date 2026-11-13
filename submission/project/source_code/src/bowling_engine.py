"""PressureIQ - bowling_engine.py

Top-level module exposing the Bowling Performance Under Pressure Engine.
Evaluates individual bowler performance across granular pressure categories,
benchmarks against historical baselines, assigns tactical bowling roles,
and calculates the Bowling Pressure Performance Index (BPPI-B).

TODO (Phase 8+): Integrate bowling pressure ratings into overall player rankings and dashboard.
"""

from __future__ import annotations

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_pressure_metrics import (
    annotate_bowling_deliveries,
    compute_bowling_pressure_metrics,
    compute_bowling_innings_consistency,
)
from src.bowling_pressure.pressure_category_aggregator import (
    assign_bowling_pressure_category,
    aggregate_by_bowling_pressure_category,
)
from src.bowling_pressure.baseline_comparator import compare_with_bowling_baselines
from src.bowling_pressure.situational_analyzer import analyze_situational_bowling
from src.bowling_pressure.bowler_role_analyzer import analyze_bowler_roles
from src.bowling_pressure.bppi_b_calculator import calculate_bppi_b
from src.bowling_pressure.bowling_reliability import (
    calculate_match_block_bootstrap_bowling,
    assess_bowling_reliability,
)
from src.bowling_pressure.bowler_classifier import classify_bowlers
from src.bowling_pressure.explanation_generator import generate_bowler_explanations
from src.bowling_pressure.statistical_validation import validate_bowling_pressure_datasets
from src.bowling_pressure.bowling_pressure_engine import calculate_bowling_pressure_performance

__all__ = [
    "BowlingPressureConfig",
    "annotate_bowling_deliveries",
    "compute_bowling_pressure_metrics",
    "compute_bowling_innings_consistency",
    "assign_bowling_pressure_category",
    "aggregate_by_bowling_pressure_category",
    "compare_with_bowling_baselines",
    "analyze_situational_bowling",
    "analyze_bowler_roles",
    "calculate_bppi_b",
    "calculate_match_block_bootstrap_bowling",
    "assess_bowling_reliability",
    "classify_bowlers",
    "generate_bowler_explanations",
    "validate_bowling_pressure_datasets",
    "calculate_bowling_pressure_performance",
]
