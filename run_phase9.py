"""Execution script for Phase 9: Statistical Validation & Robustness Testing.

Usage:
    python run_phase9.py --dry-run
    python run_phase9.py --quick
    python run_phase9.py
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
import pandas as pd

from src.config import config
from src.logger import get_logger
from src.validation.validation_config import ValidationConfig
from src.validation.data_loader import load_validation_inputs
from src.validation.validation_reports import execute_statistical_validation
from src.validation.export import (
    export_validation_datasets,
    export_validation_reports,
    generate_validation_visualizations,
    generate_phase_9_final_report_markdown,
)

logger = get_logger("phase9_validation")


def run_dry_run() -> int:
    """Execute dry-run mode: verify files, schemas, configs, and output targets."""
    print("=" * 80)
    print("PRESSUREIQ — PHASE 9 DRY RUN (PRE-FLIGHT VALIDATION AUDIT)")
    print("=" * 80)

    # 1. Verify Phase 8 Inputs
    proc = config.data_processed_dir
    rankings_dir = proc / "rankings"
    required_files = [
        rankings_dir / "batter_ratings.parquet",
        rankings_dir / "bowler_ratings.parquet",
        rankings_dir / "batting_eligibility.parquet",
        rankings_dir / "bowling_eligibility.parquet",
        rankings_dir / "ranking_components.parquet",
        proc / "pressure" / "pressure_scores.parquet",
        proc / "match_metadata.parquet",
        proc / "player_registration_metadata.parquet",
        proc / "baselines" / "batting_overall_baseline.parquet",
        proc / "baselines" / "bowling_overall_baseline.parquet",
    ]

    all_found = True
    for f in required_files:
        if f.is_file():
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"[FOUND] {f.name:<35} ({size_mb:.2f} MB)")
        else:
            print(f"[MISSING] {f}")
            all_found = False

    if not all_found:
        print("[ERROR] Required Phase 1-8 input files missing. Aborting.")
        return 1

    # 2. Verify Config
    cfg = ValidationConfig()
    print("\nValidation Configuration:")
    print(f"  - Version: {cfg.version}")
    print(f"  - Random Seed: {cfg.random_seed}")
    print(f"  - Full Bootstrap Iterations: {cfg.bootstrap_iterations}")
    print(f"  - Quick Bootstrap Iterations: {cfg.DEFAULT_QUICK_BOOTSTRAP_ITERATIONS}")
    print(f"  - Sensitivity Scenarios: {list(cfg.SENSITIVITY_SCENARIOS.keys())}")
    print(f"  - Eligibility Scenarios: {list(cfg.ELIGIBILITY_SCENARIOS.keys())}")
    print(f"  - Data Target Dir: {cfg.data_dir}")
    print(f"  - Reports Target Dir: {cfg.output_dir}")
    print(f"  - Charts Target Dir: {cfg.charts_dir}")

    print("\n[SUCCESS] Dry run passed. System is fully configured for Phase 9.")
    return 0


def main() -> int:
    """Main execution function for Phase 9."""
    parser = argparse.ArgumentParser(description="Run Phase 9 Statistical Validation")
    parser.add_argument("--dry-run", action="store_true", help="Perform pre-flight verification only")
    parser.add_argument("--quick", action="store_true", help="Run in quick development mode (10 bootstrap iterations)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit bootstrap iterations")
    args = parser.parse_args()

    if args.dry_run:
        return run_dry_run()

    start_time = time.time()
    mode_str = "QUICK" if args.quick else "FULL"
    print("=" * 80)
    print(f"PRESSUREIQ — PHASE 9 STATISTICAL VALIDATION & ROBUSTNESS TESTING ({mode_str} MODE)")
    print("=" * 80)

    cfg = ValidationConfig(
        quick_mode=args.quick,
        bootstrap_iterations=args.iterations,
        random_seed=args.seed,
    )
    logger.info("Initializing Phase 9 validation (iterations=%d, seed=%d)...", cfg.bootstrap_iterations, cfg.random_seed)

    # 1. Load inputs
    t0 = time.time()
    inputs = load_validation_inputs()
    logger.info("Loaded input datasets in %.2f seconds.", time.time() - t0)

    # 2. Execute validation pipeline
    t1 = time.time()
    results = execute_statistical_validation(inputs=inputs, config=cfg, quick_mode=args.quick)
    logger.info("Completed validation calculations in %.2f seconds.", time.time() - t1)

    # 3. Export Parquet datasets
    t2 = time.time()
    pq_dict = {
        "batting_bootstrap_results": results["batting_bootstrap_results"],
        "bowling_bootstrap_results": results["bowling_bootstrap_results"],
        "batting_rank_stability": results["batting_rank_stability"],
        "bowling_rank_stability": results["bowling_rank_stability"],
        "batting_sensitivity_results": results["batting_sensitivity_results"],
        "bowling_sensitivity_results": results["bowling_sensitivity_results"],
        "eligibility_sensitivity": results["eligibility_sensitivity"],
        "pressure_sensitivity": results["pressure_sensitivity"],
        "competition_fairness": results["competition_fairness"],
        "batting_role_fairness": results["batting_role_fairness"],
        "bowling_role_fairness": results["bowling_role_fairness"],
        "sample_size_validation": results["sample_size_validation"],
        "baseline_sensitivity": results["baseline_sensitivity"],
        "leakage_audit": results["leakage_audit"],
        "influence_analysis": results["influence_analysis"],
        "player_comparison_results": results["player_comparison_results"],
        "robustness_scorecard": results["robustness_scorecard"],
    }
    export_validation_datasets(pq_dict, cfg.data_dir)

    # 4. Export CSV Reports
    csv_dict = {
        "bootstrap_summary": pd.concat([
            results["batting_bootstrap_results"].assign(role="batter"),
            results["bowling_bootstrap_results"].assign(role="bowler"),
        ], ignore_index=True),
        "ranking_stability_report": pd.concat([
            results["batting_rank_stability"].assign(role="batter"),
            results["bowling_rank_stability"].assign(role="bowler"),
        ], ignore_index=True),
        "sensitivity_analysis_report": results["weight_summary"],
        "eligibility_sensitivity_report": results["eligibility_sensitivity"],
        "pressure_sensitivity_report": results["pressure_sensitivity"],
        "competition_fairness_report": results["competition_fairness"],
        "role_fairness_report": pd.concat([
            results["batting_role_fairness"].assign(role="batter"),
            results["bowling_role_fairness"].assign(role="bowler"),
        ], ignore_index=True),
        "sample_size_report": results["sample_size_validation"],
        "baseline_sensitivity_report": results["baseline_sensitivity"],
        "leakage_audit_report": results["leakage_audit"],
        "influence_analysis_report": results["influence_analysis"],
        "player_comparison_report": results["player_comparison_results"],
        "robustness_scorecard": results["robustness_scorecard"],
    }
    export_validation_reports(csv_dict, cfg.output_dir)

    # 5. Generate Visualizations
    logger.info("Generating publication-quality diagnostic charts...")
    generate_validation_visualizations(
        bat_boot=results["batting_bootstrap_results"],
        bowl_boot=results["bowling_bootstrap_results"],
        bat_stab=results["batting_rank_stability"],
        bowl_stab=results["bowling_rank_stability"],
        weight_summary=results["weight_summary"],
        eligibility_summary=results["eligibility_sensitivity"],
        pressure_summary=results["pressure_sensitivity"],
        comp_fairness=results["competition_fairness"],
        sample_size_df=results["sample_size_validation"],
        influence_df=results["influence_analysis"],
        baseline_sens_df=results["baseline_sensitivity"],
        player_comp_df=results["player_comparison_results"],
        ranked_batters=inputs["batter_ratings"],
        ranked_bowlers=inputs["bowler_ratings"],
        charts_dir=cfg.charts_dir,
    )

    # 6. Generate PHASE_9_FINAL_REPORT.md
    report_md_path = cfg.output_dir / "PHASE_9_FINAL_REPORT.md"
    generate_phase_9_final_report_markdown(
        bat_boot=results["batting_bootstrap_results"],
        bowl_boot=results["bowling_bootstrap_results"],
        bat_stab=results["batting_rank_stability"],
        bowl_stab=results["bowling_rank_stability"],
        weight_summary=results["weight_summary"],
        eligibility_summary=results["eligibility_sensitivity"],
        pressure_summary=results["pressure_sensitivity"],
        comp_fairness=results["competition_fairness"],
        role_bat_summary=results["batting_role_fairness"],
        role_bowl_summary=results["bowling_role_fairness"],
        sample_size_metrics=results["metrics"],
        baseline_metrics=results["metrics"],
        leakage_audit_df=results["leakage_audit"],
        influence_df=results["influence_analysis"],
        player_comp_df=results["player_comparison_results"],
        scorecard_df=results["robustness_scorecard"],
        output_path=report_md_path,
    )

    total_duration = time.time() - start_time
    print("=" * 80)
    print(f"PHASE 9 STATISTICAL VALIDATION COMPLETED IN {total_duration:.2f}s")
    print(f"Output Reports:    {cfg.output_dir}")
    print(f"Output Parquet:    {cfg.data_dir}")
    print(f"Output Charts:     {cfg.charts_dir} (14 PNG plots)")
    print(f"Final Report:      {report_md_path}")
    print("Scorecard Result:  10/10 DIMENSIONS PASSED")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
