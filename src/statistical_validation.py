"""PressureIQ - statistical_validation.py

Top-level interface for Phase 9: Statistical Validation & Robustness Testing.
Provides access to the modular validation engine and verification suite.
"""

from __future__ import annotations

# Expose Phase 9 core functions
from src.validation import (
    ValidationConfig,
    execute_statistical_validation,
    load_validation_inputs,
    run_match_level_bootstrap,
    evaluate_ranking_stability,
    run_weight_sensitivity_analysis,
    evaluate_eligibility_sensitivity,
    evaluate_pressure_model_sensitivity,
    evaluate_competition_fairness,
    evaluate_role_fairness,
    validate_sample_size_effects,
    evaluate_baseline_sensitivity,
    execute_leakage_audit,
    evaluate_influential_matches,
    compare_top_players,
    generate_robustness_scorecard,
)

# TODO (Phase 10+): Web dashboard interactivity, automated model retraining, and live match integration
