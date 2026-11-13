"""Configuration loader and validator for the Unified Player Rating & Ranking Engine.

Manages:
- Batting and bowling eligibility thresholds (balls faced/bowled, matches, innings).
- Rating component weights (primary, balanced, baseline-focused, absolute-focused).
- Uncertainty and reliability shrinkage parameters.
- Tie-breaking rules.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from src.config import config


class RankingConfigError(Exception):
    """Raised when ranking configuration parameters are invalid."""
    pass


class RankingConfig:
    """Manages validated player ranking and rating configuration."""

    DEFAULT_BATTING_ELIGIBILITY = {
        "min_balls_faced": 40,
        "min_matches": 4,
        "min_innings": 3,
        "provisional_min_balls": 20,
        "provisional_min_matches": 2,
        "require_baseline": True,
    }

    DEFAULT_BOWLING_ELIGIBILITY = {
        "min_legal_balls": 48,
        "min_matches": 4,
        "min_innings": 3,
        "provisional_min_balls": 24,
        "provisional_min_matches": 2,
        "require_baseline": True,
    }

    DEFAULT_WEIGHTS = {
        "quality_and_resilience": 0.50,
        "absolute_performance": 0.20,
        "consistency": 0.15,
        "pressure_context": 0.15,
    }

    DEFAULT_RELIABILITY = {
        "uncertainty_method": "empirical_bayes_shrinkage",
        "shrinkage_prior_weight_batting": 25.0,
        "shrinkage_prior_weight_bowling": 30.0,
        "confidence_level": 0.95,
    }

    DEFAULT_TOP_N = 10

    def __init__(self, settings_dict: Optional[Dict[str, Any]] = None) -> None:
        """Initialize and validate ranking configuration."""
        raw_cfg = settings_dict or config.ranking_settings or {}

        self.version = str(raw_cfg.get("version", "1.0.0"))
        self.top_n = int(raw_cfg.get("top_n", self.DEFAULT_TOP_N))

        # Batting eligibility
        bat_el = raw_cfg.get("batting_eligibility", {})
        self.bat_min_balls = int(bat_el.get("min_balls_faced", self.DEFAULT_BATTING_ELIGIBILITY["min_balls_faced"]))
        self.bat_min_matches = int(bat_el.get("min_matches", self.DEFAULT_BATTING_ELIGIBILITY["min_matches"]))
        self.bat_min_innings = int(bat_el.get("min_innings", self.DEFAULT_BATTING_ELIGIBILITY["min_innings"]))
        self.bat_prov_min_balls = int(bat_el.get("provisional_min_balls", self.DEFAULT_BATTING_ELIGIBILITY["provisional_min_balls"]))
        self.bat_prov_min_matches = int(bat_el.get("provisional_min_matches", self.DEFAULT_BATTING_ELIGIBILITY["provisional_min_matches"]))
        self.bat_require_baseline = bool(bat_el.get("require_baseline", self.DEFAULT_BATTING_ELIGIBILITY["require_baseline"]))

        # Bowling eligibility
        bowl_el = raw_cfg.get("bowling_eligibility", {})
        self.bowl_min_balls = int(bowl_el.get("min_legal_balls", self.DEFAULT_BOWLING_ELIGIBILITY["min_legal_balls"]))
        self.bowl_min_matches = int(bowl_el.get("min_matches", self.DEFAULT_BOWLING_ELIGIBILITY["min_matches"]))
        self.bowl_min_innings = int(bowl_el.get("min_innings", self.DEFAULT_BOWLING_ELIGIBILITY["min_innings"]))
        self.bowl_prov_min_balls = int(bowl_el.get("provisional_min_balls", self.DEFAULT_BOWLING_ELIGIBILITY["provisional_min_balls"]))
        self.bowl_prov_min_matches = int(bowl_el.get("provisional_min_matches", self.DEFAULT_BOWLING_ELIGIBILITY["provisional_min_matches"]))
        self.bowl_require_baseline = bool(bowl_el.get("require_baseline", self.DEFAULT_BOWLING_ELIGIBILITY["require_baseline"]))

        # Weight profiles
        weights_section = raw_cfg.get("weights", {})
        self.weight_profiles: Dict[str, Dict[str, float]] = {
            "primary": weights_section.get("primary", self.DEFAULT_WEIGHTS),
            "balanced": weights_section.get("balanced", {
                "quality_and_resilience": 0.40,
                "absolute_performance": 0.30,
                "consistency": 0.15,
                "pressure_context": 0.15,
            }),
            "baseline_focused": weights_section.get("baseline_focused", {
                "quality_and_resilience": 0.60,
                "absolute_performance": 0.15,
                "consistency": 0.15,
                "pressure_context": 0.10,
            }),
            "absolute_focused": weights_section.get("absolute_focused", {
                "quality_and_resilience": 0.30,
                "absolute_performance": 0.45,
                "consistency": 0.15,
                "pressure_context": 0.10,
            }),
        }
        self.primary_weights = self.weight_profiles["primary"]

        # Reliability settings
        rel_section = raw_cfg.get("reliability", {})
        self.uncertainty_method = str(rel_section.get("uncertainty_method", self.DEFAULT_RELIABILITY["uncertainty_method"]))
        self.shrinkage_prior_weight_batting = float(rel_section.get("shrinkage_prior_weight_batting", self.DEFAULT_RELIABILITY["shrinkage_prior_weight_batting"]))
        self.shrinkage_prior_weight_bowling = float(rel_section.get("shrinkage_prior_weight_bowling", self.DEFAULT_RELIABILITY["shrinkage_prior_weight_bowling"]))
        self.confidence_level = float(rel_section.get("confidence_level", self.DEFAULT_RELIABILITY["confidence_level"]))

        self._validate()

    def _validate(self) -> None:
        """Validate parameter ranges and mathematical consistency."""
        if self.bat_min_balls <= 0 or self.bowl_min_balls <= 0:
            raise RankingConfigError("Minimum balls threshold must be strictly positive.")
        if self.bat_prov_min_balls > self.bat_min_balls:
            raise RankingConfigError("Provisional batting balls threshold cannot exceed full threshold.")
        if self.bowl_prov_min_balls > self.bowl_min_balls:
            raise RankingConfigError("Provisional bowling balls threshold cannot exceed full threshold.")

        for profile_name, weights in self.weight_profiles.items():
            total = sum(weights.values())
            if abs(total - 1.0) > 1e-4:
                raise RankingConfigError(
                    f"Weight profile '{profile_name}' must sum to 1.0, got {total:.4f}"
                )
            for k, v in weights.items():
                if v < 0.0 or v > 1.0:
                    raise RankingConfigError(
                        f"Weight '{k}' in profile '{profile_name}' must be in [0, 1], got {v}"
                    )

