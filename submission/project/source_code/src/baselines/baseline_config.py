"""Configuration loader and validator for the Player Baseline Calculation Engine.

Manages low-pressure thresholds, reliability standards, position taxonomies,
and statistical shrinkage parameters.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.config import config


class BaselineConfigError(Exception):
    """Raised when baseline settings are invalid or inconsistent."""
    pass


class BaselineConfig:
    """Manages validated player baseline engine configuration."""

    DEFAULT_LOW_PRESSURE_THRESHOLD = {
        "batting_max": 39.99,
        "bowling_max": 39.99,
    }

    DEFAULT_BATTING_POSITIONS = {
        "top_order": [1, 2, 3],
        "middle_order": [4, 5, 6],
        "lower_order": [7, 8, 9, 10, 11],
    }

    DEFAULT_RELIABILITY = {
        "batting": {
            "high_min_balls": 150,
            "medium_min_balls": 60,
            "low_min_balls": 20,
            "min_dismissals_for_avg": 5,
        },
        "bowling": {
            "high_min_balls": 120,
            "medium_min_balls": 48,
            "low_min_balls": 18,
            "min_wickets_for_avg": 5,
        },
    }

    DEFAULT_SHRINKAGE = {
        "enabled": True,
        "method": "empirical_bayes",
        "batting_sr_k": 60.0,
        "batting_avg_k": 5.0,
        "bowling_econ_k": 120.0,
        "bowling_avg_k": 5.0,
    }

    def __init__(self, custom_settings: Optional[Dict[str, Any]] = None) -> None:
        """Initialize and validate baseline configuration."""
        raw = custom_settings if custom_settings is not None else getattr(config, "baseline_settings", {})

        self.version: str = str(raw.get("version", "1.0.0"))

        lp = raw.get("low_pressure_threshold", {})
        self.batting_low_pressure_max: float = float(
            lp.get("batting_max", self.DEFAULT_LOW_PRESSURE_THRESHOLD["batting_max"])
        )
        self.bowling_low_pressure_max: float = float(
            lp.get("bowling_max", self.DEFAULT_LOW_PRESSURE_THRESHOLD["bowling_max"])
        )

        bp = raw.get("batting_positions", {})
        self.top_order_positions: List[int] = list(bp.get("top_order", self.DEFAULT_BATTING_POSITIONS["top_order"]))
        self.middle_order_positions: List[int] = list(bp.get("middle_order", self.DEFAULT_BATTING_POSITIONS["middle_order"]))
        self.lower_order_positions: List[int] = list(bp.get("lower_order", self.DEFAULT_BATTING_POSITIONS["lower_order"]))

        rel = raw.get("reliability", {})
        rel_bat = rel.get("batting", {})
        self.batting_high_min_balls: int = int(rel_bat.get("high_min_balls", self.DEFAULT_RELIABILITY["batting"]["high_min_balls"]))
        self.batting_medium_min_balls: int = int(rel_bat.get("medium_min_balls", self.DEFAULT_RELIABILITY["batting"]["medium_min_balls"]))
        self.batting_low_min_balls: int = int(rel_bat.get("low_min_balls", self.DEFAULT_RELIABILITY["batting"]["low_min_balls"]))
        self.batting_min_dismissals: int = int(rel_bat.get("min_dismissals_for_avg", self.DEFAULT_RELIABILITY["batting"]["min_dismissals_for_avg"]))

        rel_bowl = rel.get("bowling", {})
        self.bowling_high_min_balls: int = int(rel_bowl.get("high_min_balls", self.DEFAULT_RELIABILITY["bowling"]["high_min_balls"]))
        self.bowling_medium_min_balls: int = int(rel_bowl.get("medium_min_balls", self.DEFAULT_RELIABILITY["bowling"]["medium_min_balls"]))
        self.bowling_low_min_balls: int = int(rel_bowl.get("low_min_balls", self.DEFAULT_RELIABILITY["bowling"]["low_min_balls"]))
        self.bowling_min_wickets: int = int(rel_bowl.get("min_wickets_for_avg", self.DEFAULT_RELIABILITY["bowling"]["min_wickets_for_avg"]))

        shrink = raw.get("shrinkage", {})
        self.shrinkage_enabled: bool = bool(shrink.get("enabled", self.DEFAULT_SHRINKAGE["enabled"]))
        self.shrinkage_method: str = str(shrink.get("method", self.DEFAULT_SHRINKAGE["method"]))
        self.batting_sr_k: float = float(shrink.get("batting_sr_k", self.DEFAULT_SHRINKAGE["batting_sr_k"]))
        self.batting_avg_k: float = float(shrink.get("batting_avg_k", self.DEFAULT_SHRINKAGE["batting_avg_k"]))
        self.bowling_econ_k: float = float(shrink.get("bowling_econ_k", self.DEFAULT_SHRINKAGE["bowling_econ_k"]))
        self.bowling_avg_k: float = float(shrink.get("bowling_avg_k", self.DEFAULT_SHRINKAGE["bowling_avg_k"]))

        self.validate()

    def validate(self) -> None:
        """Validate parameter consistency."""
        if self.batting_low_pressure_max <= 0 or self.batting_low_pressure_max >= 100:
            raise BaselineConfigError(f"batting_low_pressure_max must be in (0, 100), got {self.batting_low_pressure_max}")

        if self.bowling_low_pressure_max <= 0 or self.bowling_low_pressure_max >= 100:
            raise BaselineConfigError(f"bowling_low_pressure_max must be in (0, 100), got {self.bowling_low_pressure_max}")

        if not (self.batting_low_min_balls < self.batting_medium_min_balls < self.batting_high_min_balls):
            raise BaselineConfigError("Batting reliability ball thresholds must be strictly increasing.")

        if not (self.bowling_low_min_balls < self.bowling_medium_min_balls < self.bowling_high_min_balls):
            raise BaselineConfigError("Bowling reliability ball thresholds must be strictly increasing.")

        if self.batting_sr_k <= 0 or self.bowling_econ_k <= 0:
            raise BaselineConfigError("Shrinkage constant K must be strictly positive.")

