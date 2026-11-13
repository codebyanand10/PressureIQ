"""PressureIQ - pressure_engine.py

Top-level module exposing the dynamic pressure index computation engine.
Coordinates delivery-level pressure detection for batters and bowlers.

TODO (Phase 5+): Interface with player baseline engine for pressure-adjusted player evaluation.
"""

from __future__ import annotations

from src.pressure.pressure_config import PressureConfig
from src.pressure.pressure_engine import calculate_pressure_scores
from src.pressure.batting_pressure import calculate_batting_pressure
from src.pressure.bowling_pressure import calculate_bowling_pressure
from src.pressure.chase_pressure import calculate_chase_pressure
from src.pressure.first_innings_pressure import calculate_first_innings_pressure
from src.pressure.pressure_classifier import classify_pressure_score, classify_pressure_vector
from src.pressure.pressure_validator import validate_pressure_scores, audit_leakage

__all__ = [
    "PressureConfig",
    "calculate_pressure_scores",
    "calculate_batting_pressure",
    "calculate_bowling_pressure",
    "calculate_chase_pressure",
    "calculate_first_innings_pressure",
    "classify_pressure_score",
    "classify_pressure_vector",
    "validate_pressure_scores",
    "audit_leakage",
]
