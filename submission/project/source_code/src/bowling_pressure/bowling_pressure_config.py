"""Configuration loader and validator for the Bowling Performance Under Pressure Engine.

Manages pressure category boundaries, BPPI-B component weights, reliability cutoffs,
bowling role criteria, and statistical bootstrap settings.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from src.config import config


class BowlingPressureConfigError(Exception):
    """Raised when bowling pressure configuration parameters are invalid."""
    pass


class BowlingPressureConfig:
    """Manages validated bowling performance under pressure configuration."""

    DEFAULT_CATEGORIES = {
        "very_low_max": 19.99,
        "low_max": 39.99,
        "moderate_max": 59.99,
        "high_max": 79.99,
        "extreme_max": 100.0,
    }

    DEFAULT_HIGH_PRESSURE_THRESHOLD = 60.0

    DEFAULT_BPPI_B_WEIGHTS = {
        "economy_retention": 0.30,
        "wicket_taking_effectiveness": 0.25,
        "dot_ball_generation": 0.20,
        "boundary_prevention": 0.15,
        "bowling_average_retention": 0.10,
    }

    DEFAULT_RELIABILITY = {
        "high_min_balls": 120,
        "medium_min_balls": 48,
        "low_min_balls": 18,
        "min_matches": 5,
        "min_innings": 3,
        "bootstrap_iterations": 500,
        "bootstrap_confidence_level": 0.95,
    }

    DEFAULT_CLASSIFICATION = {
        "elite_bppi_min": 75.0,
        "strong_bppi_min": 60.0,
        "average_bppi_min": 45.0,
        "below_baseline_bppi_min": 0.0,
    }

    DEFAULT_ROLES = {
        "powerplay_phase_threshold": 0.40,
        "middle_phase_threshold": 0.40,
        "death_phase_threshold": 0.40,
        "min_balls_for_role": 36,
    }

    def __init__(self, custom_settings: Optional[Dict[str, Any]] = None) -> None:
        """Initialize configuration from YAML settings or custom dictionary."""
        raw = custom_settings if custom_settings is not None else getattr(config, "bowling_pressure_settings", {})

        self.version: str = str(raw.get("version", "1.0.0"))

        cats = raw.get("categories", {})
        self.very_low_max: float = float(cats.get("very_low_max", self.DEFAULT_CATEGORIES["very_low_max"]))
        self.low_max: float = float(cats.get("low_max", self.DEFAULT_CATEGORIES["low_max"]))
        self.moderate_max: float = float(cats.get("moderate_max", self.DEFAULT_CATEGORIES["moderate_max"]))
        self.high_max: float = float(cats.get("high_max", self.DEFAULT_CATEGORIES["high_max"]))
        self.extreme_max: float = float(cats.get("extreme_max", self.DEFAULT_CATEGORIES["extreme_max"]))

        self.high_pressure_threshold: float = float(
            raw.get("high_pressure_threshold", self.DEFAULT_HIGH_PRESSURE_THRESHOLD)
        )

        bppi_cfg = raw.get("bppi_b", {})
        weights = bppi_cfg.get("weights", self.DEFAULT_BPPI_B_WEIGHTS)
        self.bppi_b_weights: Dict[str, float] = {k: float(v) for k, v in weights.items()}
        self.bppi_retention_cap: float = float(bppi_cfg.get("retention_cap", 200.0))
        self.bppi_retention_floor: float = float(bppi_cfg.get("retention_floor", 0.0))

        rel_cfg = raw.get("reliability", {})
        self.high_min_balls: int = int(rel_cfg.get("high_min_balls", self.DEFAULT_RELIABILITY["high_min_balls"]))
        self.medium_min_balls: int = int(rel_cfg.get("medium_min_balls", self.DEFAULT_RELIABILITY["medium_min_balls"]))
        self.low_min_balls: int = int(rel_cfg.get("low_min_balls", self.DEFAULT_RELIABILITY["low_min_balls"]))
        self.min_matches: int = int(rel_cfg.get("min_matches", self.DEFAULT_RELIABILITY["min_matches"]))
        self.min_innings: int = int(rel_cfg.get("min_innings", self.DEFAULT_RELIABILITY["min_innings"]))
        self.bootstrap_iterations: int = int(rel_cfg.get("bootstrap_iterations", self.DEFAULT_RELIABILITY["bootstrap_iterations"]))
        self.bootstrap_confidence_level: float = float(rel_cfg.get("bootstrap_confidence_level", self.DEFAULT_RELIABILITY["bootstrap_confidence_level"]))

        cls_cfg = raw.get("classification", {})
        self.elite_bppi_min: float = float(cls_cfg.get("elite_bppi_min", self.DEFAULT_CLASSIFICATION["elite_bppi_min"]))
        self.strong_bppi_min: float = float(cls_cfg.get("strong_bppi_min", self.DEFAULT_CLASSIFICATION["strong_bppi_min"]))
        self.average_bppi_min: float = float(cls_cfg.get("average_bppi_min", self.DEFAULT_CLASSIFICATION["average_bppi_min"]))
        self.below_baseline_bppi_min: float = float(cls_cfg.get("below_baseline_bppi_min", self.DEFAULT_CLASSIFICATION["below_baseline_bppi_min"]))

        role_cfg = raw.get("roles", {})
        self.powerplay_threshold: float = float(role_cfg.get("powerplay_phase_threshold", self.DEFAULT_ROLES["powerplay_phase_threshold"]))
        self.middle_threshold: float = float(role_cfg.get("middle_phase_threshold", self.DEFAULT_ROLES["middle_phase_threshold"]))
        self.death_threshold: float = float(role_cfg.get("death_phase_threshold", self.DEFAULT_ROLES["death_phase_threshold"]))
        self.min_balls_for_role: int = int(role_cfg.get("min_balls_for_role", self.DEFAULT_ROLES["min_balls_for_role"]))

        self.validate()

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not (0 < self.very_low_max < self.low_max < self.moderate_max < self.high_max <= self.extreme_max):
            raise BowlingPressureConfigError("Pressure category upper bounds must be strictly increasing.")

        total_weight = sum(self.bppi_b_weights.values())
        if not (0.99 <= total_weight <= 1.01):
            raise BowlingPressureConfigError(f"BPPI-B component weights must sum to 1.0, got {total_weight:.4f}")

        if not (self.low_min_balls < self.medium_min_balls < self.high_min_balls):
            raise BowlingPressureConfigError("Reliability ball thresholds must be strictly increasing.")

        if not (0.0 <= self.below_baseline_bppi_min < self.average_bppi_min < self.strong_bppi_min < self.elite_bppi_min <= 100.0):
            raise BowlingPressureConfigError("Classification BPPI-B thresholds must be strictly increasing in [0, 100].")

