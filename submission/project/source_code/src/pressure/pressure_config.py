"""Configuration loader and validator for the Pressure Detection Engine.

Manages component weights, classification thresholds, normalization methods,
and domain parameters for batting and bowling pressure calculations.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from src.config import config


class PressureConfigError(Exception):
    """Raised when pressure settings are invalid or inconsistent."""
    pass


class PressureConfig:
    """Manages validated pressure engine configuration."""

    DEFAULT_SCORE_MIN = 0.0
    DEFAULT_SCORE_MAX = 100.0

    DEFAULT_CLASSIFICATION = {
        "very_low_max": 19.99,
        "low_max": 39.99,
        "moderate_max": 59.99,
        "high_max": 79.99,
        "extreme_max": 100.0,
    }

    DEFAULT_CHASE_WEIGHTS = {
        "urgency": 0.35,
        "wicket_vulnerability": 0.30,
        "time_scarcity": 0.20,
        "match_context": 0.15,
    }

    DEFAULT_FIRST_INN_WEIGHTS = {
        "scoring_pace": 0.30,
        "wicket_vulnerability": 0.35,
        "phase_pressure": 0.20,
        "match_context": 0.15,
    }

    DEFAULT_BOWLING_CHASE_WEIGHTS = {
        "defense_risk": 0.50,
        "time_margin": 0.30,
        "match_context": 0.20,
    }

    DEFAULT_BOWLING_FIRST_INN_WEIGHTS = {
        "containment_risk": 0.45,
        "wicket_need": 0.35,
        "match_context": 0.20,
    }

    def __init__(self, custom_settings: Optional[Dict[str, Any]] = None) -> None:
        """Initialize and validate pressure configuration.

        Args:
            custom_settings: Optional dictionary overriding config/settings.yaml.
        """
        raw = custom_settings if custom_settings is not None else getattr(config, "pressure_settings", {})

        self.version: str = str(raw.get("version", "1.0.0"))

        score_range = raw.get("score_range", {})
        self.score_min: float = float(score_range.get("minimum", self.DEFAULT_SCORE_MIN))
        self.score_max: float = float(score_range.get("maximum", self.DEFAULT_SCORE_MAX))

        classification = raw.get("classification", {})
        self.classification_thresholds = {
            "very_low_max": float(classification.get("very_low_max", self.DEFAULT_CLASSIFICATION["very_low_max"])),
            "low_max": float(classification.get("low_max", self.DEFAULT_CLASSIFICATION["low_max"])),
            "moderate_max": float(classification.get("moderate_max", self.DEFAULT_CLASSIFICATION["moderate_max"])),
            "high_max": float(classification.get("high_max", self.DEFAULT_CLASSIFICATION["high_max"])),
            "extreme_max": float(classification.get("extreme_max", self.DEFAULT_CLASSIFICATION["extreme_max"])),
        }

        norm = raw.get("normalization", {})
        self.normalization_method: str = str(norm.get("method", "percentile"))
        self.minimum_group_size: int = int(norm.get("minimum_group_size", 100))
        self.fallback_to_global: bool = bool(norm.get("fallback_to_global", True))

        indicators = raw.get("indicators", {})
        self.rrr_cap: float = float(indicators.get("rrr_cap", 36.0))
        self.benchmark_baseline_crr: float = float(indicators.get("benchmark_baseline_crr", 8.0))
        self.knockout_boost: float = float(indicators.get("knockout_boost", 1.15))
        self.death_overs_start_ball: int = int(indicators.get("death_overs_start_ball", 96))
        self.powerplay_end_ball: int = int(indicators.get("powerplay_end_ball", 36))

        models = raw.get("models", {})
        chase_model = models.get("chase", {})
        self.chase_enabled: bool = bool(chase_model.get("enabled", True))
        self.chase_weights: Dict[str, float] = self._normalize_weights(
            chase_model.get("weights", self.DEFAULT_CHASE_WEIGHTS)
        )

        first_inn_model = models.get("first_innings", {})
        self.first_innings_enabled: bool = bool(first_inn_model.get("enabled", True))
        self.first_innings_weights: Dict[str, float] = self._normalize_weights(
            first_inn_model.get("weights", self.DEFAULT_FIRST_INN_WEIGHTS)
        )

        bowling_model = models.get("bowling", {})
        self.bowling_enabled: bool = bool(bowling_model.get("enabled", True))
        self.bowling_chase_weights: Dict[str, float] = self._normalize_weights(
            bowling_model.get("chase_weights", self.DEFAULT_BOWLING_CHASE_WEIGHTS)
        )
        self.bowling_first_inn_weights: Dict[str, float] = self._normalize_weights(
            bowling_model.get("first_inn_weights", self.DEFAULT_BOWLING_FIRST_INN_WEIGHTS)
        )

        self.validate()

    @staticmethod
    def _normalize_weights(weights: Dict[str, Any]) -> Dict[str, float]:
        """Convert weights to floats and normalize sum to 1.0."""
        float_weights = {k: float(v) for k, v in weights.items()}
        total = sum(float_weights.values())
        if total <= 0:
            raise PressureConfigError("Sum of component weights must be positive.")
        return {k: round(v / total, 4) for k, v in float_weights.items()}

    def validate(self) -> None:
        """Validate internal consistency of thresholds and settings."""
        if self.score_min >= self.score_max:
            raise PressureConfigError(f"score_min ({self.score_min}) must be strictly less than score_max ({self.score_max})")

        th = self.classification_thresholds
        if not (self.score_min <= th["very_low_max"] < th["low_max"] < th["moderate_max"] < th["high_max"] <= th["extreme_max"]):
            raise PressureConfigError(f"Classification thresholds must be strictly monotonic: {th}")

        if self.rrr_cap <= 0:
            raise PressureConfigError(f"rrr_cap must be strictly positive, got {self.rrr_cap}")

        if self.minimum_group_size < 1:
            raise PressureConfigError(f"minimum_group_size must be >= 1, got {self.minimum_group_size}")

