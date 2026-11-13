"""Configuration module for Phase 9: Statistical Validation & Robustness Testing.

Manages validation parameters, random seeds, bootstrap sample sizes,
sensitivity profiles, eligibility variations, and directory paths.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import config

logger = logging.getLogger(__name__)


class ValidationConfigError(Exception):
    """Raised when validation configuration parameters are invalid."""
    pass


class ValidationConfig:
    """Manages validated configuration for robustness testing and statistical validation."""

    DEFAULT_BOOTSTRAP_ITERATIONS = 100
    DEFAULT_QUICK_BOOTSTRAP_ITERATIONS = 10
    DEFAULT_SEED = 42
    DEFAULT_CONFIDENCE_LEVELS = [0.90, 0.95]
    DEFAULT_TOP_N = 10

    # Defensible alternative weighting profiles for sensitivity testing
    SENSITIVITY_SCENARIOS = {
        "primary": {
            "quality_and_resilience": 0.50,
            "absolute_performance": 0.20,
            "consistency": 0.15,
            "pressure_context": 0.15,
        },
        "balanced": {
            "quality_and_resilience": 0.40,
            "absolute_performance": 0.30,
            "consistency": 0.15,
            "pressure_context": 0.15,
        },
        "absolute_focused": {
            "quality_and_resilience": 0.30,
            "absolute_performance": 0.45,
            "consistency": 0.15,
            "pressure_context": 0.10,
        },
        "baseline_focused": {
            "quality_and_resilience": 0.60,
            "absolute_performance": 0.15,
            "consistency": 0.15,
            "pressure_context": 0.10,
        },
        "consistency_focused": {
            "quality_and_resilience": 0.35,
            "absolute_performance": 0.20,
            "consistency": 0.35,
            "pressure_context": 0.10,
        },
        "reliability_focused": {
            "quality_and_resilience": 0.40,
            "absolute_performance": 0.20,
            "consistency": 0.20,
            "pressure_context": 0.20,
        },
        "pressure_difficulty_focused": {
            "quality_and_resilience": 0.35,
            "absolute_performance": 0.20,
            "consistency": 0.15,
            "pressure_context": 0.30,
        },
    }

    # Defensible eligibility scenarios
    ELIGIBILITY_SCENARIOS = {
        "lower": {
            "bat_min_balls": 20,
            "bat_min_matches": 2,
            "bat_min_inns": 2,
            "bowl_min_balls": 24,
            "bowl_min_matches": 2,
            "bowl_min_inns": 2,
        },
        "primary": {
            "bat_min_balls": 40,
            "bat_min_matches": 4,
            "bat_min_inns": 3,
            "bowl_min_balls": 48,
            "bowl_min_matches": 4,
            "bowl_min_inns": 3,
        },
        "higher": {
            "bat_min_balls": 60,
            "bat_min_matches": 6,
            "bat_min_inns": 4,
            "bowl_min_balls": 72,
            "bowl_min_matches": 6,
            "bowl_min_inns": 4,
        },
    }

    def __init__(
        self,
        quick_mode: bool = False,
        bootstrap_iterations: Optional[int] = None,
        random_seed: Optional[int] = None,
        custom_settings: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize validation configuration."""
        raw_cfg = custom_settings or config.validation_settings or {}

        self.version = str(raw_cfg.get("version", "1.0.0"))
        self.quick_mode = quick_mode
        self.random_seed = (
            random_seed
            if random_seed is not None
            else int(raw_cfg.get("random_seed", self.DEFAULT_SEED))
        )

        if bootstrap_iterations is not None:
            self.bootstrap_iterations = bootstrap_iterations
        elif quick_mode:
            self.bootstrap_iterations = int(
                raw_cfg.get("quick_bootstrap_iterations", self.DEFAULT_QUICK_BOOTSTRAP_ITERATIONS)
            )
        else:
            self.bootstrap_iterations = int(
                raw_cfg.get("bootstrap_iterations", self.DEFAULT_BOOTSTRAP_ITERATIONS)
            )

        self.confidence_levels: List[float] = [
            float(c) for c in raw_cfg.get("confidence_levels", self.DEFAULT_CONFIDENCE_LEVELS)
        ]
        self.leave_one_match_out = bool(raw_cfg.get("leave_one_match_out", True))
        self.top_n = int(raw_cfg.get("top_n", self.DEFAULT_TOP_N))

        # Output paths
        self.output_dir: Path = config.validation_dir
        self.data_dir: Path = config.validation_data_dir
        self.charts_dir: Path = config.validation_charts_dir

        self._validate()

    def _validate(self) -> None:
        """Validate configuration bounds."""
        if self.bootstrap_iterations <= 0:
            raise ValidationConfigError("Bootstrap iterations must be strictly positive.")
        for cl in self.confidence_levels:
            if not (0.50 < cl < 1.0):
                raise ValidationConfigError(f"Confidence level must be in (0.50, 1.0), got {cl}")
        for name, weights in self.SENSITIVITY_SCENARIOS.items():
            total = sum(weights.values())
            if abs(total - 1.0) > 1e-4:
                raise ValidationConfigError(
                    f"Weight profile '{name}' must sum to 1.0, got {total:.4f}"
                )

