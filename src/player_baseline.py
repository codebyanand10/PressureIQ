"""PressureIQ - player_baseline.py

Top-level module exposing the Player Baseline Calculation Engine.
Calculates historical reference baselines for batters and bowlers across overall,
low-pressure, and contextual competition settings.

TODO (Phase 6+): Provide reference baseline inputs to batting and bowling pressure engines.
"""

from __future__ import annotations

from src.baselines.baseline_config import BaselineConfig
from src.baselines.player_registry import build_player_registry
from src.baselines.batting_metrics import compute_batting_metrics
from src.baselines.bowling_metrics import compute_bowling_metrics
from src.baselines.batting_baseline import calculate_batting_baselines
from src.baselines.bowling_baseline import calculate_bowling_baselines
from src.baselines.contextual_baseline import calculate_contextual_baselines
from src.baselines.baseline_shrinkage import apply_baseline_shrinkage
from src.baselines.baseline_reliability import assess_baseline_reliability
from src.baselines.baseline_validation import validate_baselines
from src.baselines.baseline_engine import calculate_all_player_baselines

__all__ = [
    "BaselineConfig",
    "build_player_registry",
    "compute_batting_metrics",
    "compute_bowling_metrics",
    "calculate_batting_baselines",
    "calculate_bowling_baselines",
    "calculate_contextual_baselines",
    "apply_baseline_shrinkage",
    "assess_baseline_reliability",
    "validate_baselines",
    "calculate_all_player_baselines",
]
