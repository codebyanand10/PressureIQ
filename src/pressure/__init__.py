"""PressureIQ - Pressure Detection Engine Package.

Provides delivery-level pre-delivery pressure quantification for batters and bowlers
across IPL and T20 International cricket matches.
"""

from __future__ import annotations

from src.pressure.pressure_config import PressureConfig
from src.pressure.pressure_features import (
    calc_rrr_pressure,
    calc_run_rate_gap_pressure,
    calc_wicket_pressure,
    calc_time_pressure,
    calc_match_importance_pressure,
    calc_match_closeness_pressure,
)
from src.pressure.chase_pressure import calculate_chase_pressure
from src.pressure.first_innings_pressure import calculate_first_innings_pressure
from src.pressure.batting_pressure import calculate_batting_pressure
from src.pressure.bowling_pressure import calculate_bowling_pressure
from src.pressure.pressure_normalizer import PressureNormalizer
from src.pressure.pressure_classifier import classify_pressure_score, classify_pressure_vector
from src.pressure.pressure_validator import validate_pressure_scores, audit_leakage
from src.pressure.pressure_engine import calculate_pressure_scores

__all__ = [
    "PressureConfig",
    "calc_rrr_pressure",
    "calc_run_rate_gap_pressure",
    "calc_wicket_pressure",
    "calc_time_pressure",
    "calc_match_importance_pressure",
    "calc_match_closeness_pressure",
    "calculate_chase_pressure",
    "calculate_first_innings_pressure",
    "calculate_batting_pressure",
    "calculate_bowling_pressure",
    "PressureNormalizer",
    "classify_pressure_score",
    "classify_pressure_vector",
    "validate_pressure_scores",
    "audit_leakage",
    "calculate_pressure_scores",
]

