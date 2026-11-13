"""Phase 9: Statistical Validation & Robustness Testing package for PressureIQ."""

from src.validation.validation_config import ValidationConfig, ValidationConfigError
from src.validation.data_loader import load_validation_inputs
from src.validation.bootstrap_validation import run_match_level_bootstrap
from src.validation.ranking_stability import evaluate_ranking_stability, calculate_ranking_similarity_metrics
from src.validation.sensitivity_analysis import run_weight_sensitivity_analysis
from src.validation.eligibility_sensitivity import evaluate_eligibility_sensitivity
from src.validation.pressure_sensitivity import evaluate_pressure_model_sensitivity
from src.validation.competition_fairness import evaluate_competition_fairness
from src.validation.role_fairness import evaluate_role_fairness
from src.validation.sample_size_validation import validate_sample_size_effects
from src.validation.baseline_sensitivity import evaluate_baseline_sensitivity
from src.validation.leakage_audit import execute_leakage_audit
from src.validation.influence_analysis import evaluate_influential_matches
from src.validation.player_comparison import compare_top_players
from src.validation.robustness_scorecard import generate_robustness_scorecard
from src.validation.validation_reports import execute_statistical_validation
from src.validation.export import (
    export_validation_datasets,
    export_validation_reports,
    generate_validation_visualizations,
    generate_phase_9_final_report_markdown,
)

__all__ = [
    "ValidationConfig",
    "ValidationConfigError",
    "load_validation_inputs",
    "run_match_level_bootstrap",
    "evaluate_ranking_stability",
    "calculate_ranking_similarity_metrics",
    "run_weight_sensitivity_analysis",
    "evaluate_eligibility_sensitivity",
    "evaluate_pressure_model_sensitivity",
    "evaluate_competition_fairness",
    "evaluate_role_fairness",
    "validate_sample_size_effects",
    "evaluate_baseline_sensitivity",
    "execute_leakage_audit",
    "evaluate_influential_matches",
    "compare_top_players",
    "generate_robustness_scorecard",
    "execute_statistical_validation",
    "export_validation_datasets",
    "export_validation_reports",
    "generate_validation_visualizations",
    "generate_phase_9_final_report_markdown",
]

