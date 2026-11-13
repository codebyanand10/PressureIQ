"""PressureIQ - Phase 8 Master Execution Pipeline.

Executes the Unified Player Rating & Ranking Engine:
1. Loads Phase 5, Phase 6, and Phase 7 validated datasets.
2. Evaluates evidence-based eligibility criteria for batters and bowlers.
3. Computes multi-component ratings (Quality & Resilience, Absolute Performance, Consistency, Pressure Context).
4. Applies Empirical Bayes shrinkage and 95% bootstrap confidence bounds.
5. Performs deterministic tie-breaking and ranks eligible players.
6. Extracts official Top 10 Batters and Top 10 Bowlers under pressure.
7. Generates dynamic, evidence-backed narrative explanations.
8. Validates mathematical constraints, bounds [0, 100], and performs initial fairness audit.
9. Exports 6 processed Parquet datasets to data/processed/rankings/.
10. Generates 7 analytical CSV reports, 2 Excel spreadsheets (.xlsx), 8 publication charts,
    and 6 comprehensive Markdown reports including PHASE_8_FINAL_REPORT.md.

Usage:
    python run_phase8.py [--dry-run]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Set MPLCONFIGDIR to project outputs cache before matplotlib loads
os.environ["MPLCONFIGDIR"] = str(Path(__file__).resolve().parent / "outputs" / ".mpl_cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

from src.config import config
from src.logger import get_logger
from src.ranking.ranking_config import RankingConfig
from src.ranking.data_loader import load_ranking_inputs
from src.ranking.ranking_engine import calculate_unified_player_rankings
from src.ranking.export import (
    export_rankings_datasets,
    export_ranking_reports,
    generate_ranking_visualizations,
)

logger = get_logger("pressureiq_phase8")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PressureIQ Phase 8 Unified Player Rating & Ranking Engine")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and configuration without executing full calculation and file export.",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="primary",
        choices=["primary", "balanced", "baseline_focused", "absolute_focused"],
        help="Weight profile configuration to apply for ratings.",
    )
    return parser.parse_args()


def run_pipeline(dry_run: bool = False, profile: str = "primary") -> int:
    """Execute the Phase 8 player ranking engine pipeline."""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("STARTING PHASE 8: UNIFIED PLAYER RATING & RANKING ENGINE (Dry Run: %s, Profile: %s)", dry_run, profile)
    logger.info("=" * 70)

    try:
        # 1. Load and Validate Configuration
        cfg = RankingConfig()
        logger.info(
            "Loaded RankingConfig (version: %s, top_n: %d, profile: %s, bat_min_balls: %d, bowl_min_balls: %d)",
            cfg.version,
            cfg.top_n,
            profile,
            cfg.bat_min_balls,
            cfg.bowl_min_balls,
        )

        # 2. Load Datasets
        logger.info("Loading input datasets from Phases 5, 6, and 7...")
        inputs = load_ranking_inputs()

        # 3. Input Validation Checks
        bat_required = ["player_id", "balls_faced", "strike_rate", "bppi", "matches_count", "innings_count"]
        bowl_required = ["player_id", "legal_balls_bowled", "economy_rate", "bppi_b", "matches_bowled", "innings_bowled"]

        missing_bat = [c for c in bat_required if c not in inputs["batting_bppi"].columns]
        missing_bowl = [c for c in bowl_required if c not in inputs["bowling_bppi"].columns]

        if missing_bat:
            raise ValueError(f"Batting dataset missing required columns: {missing_bat}")
        if missing_bowl:
            raise ValueError(f"Bowling dataset missing required columns: {missing_bowl}")

        logger.info("Input verification passed: all required Phase 6 & Phase 7 columns present.")

        if dry_run:
            logger.info("=" * 70)
            logger.info("DRY-RUN COMPLETE: Inputs, columns, and ranking configuration validated successfully.")
            logger.info("=" * 70)
            return 0

        # 4. Execute Core Unified Ranking Engine
        logger.info("Executing calculate_unified_player_rankings...")
        results = calculate_unified_player_rankings(
            inputs=inputs,
            config=cfg,
            weights_profile=profile,
        )

        top_10_batters = results["top_10_batters"]
        top_10_bowlers = results["top_10_bowlers"]
        all_batters = results["all_batter_rankings"]
        all_bowlers = results["all_bowler_rankings"]
        bat_eligibility = results["batting_eligibility"]
        bowl_eligibility = results["bowling_eligibility"]
        excluded_players = results["excluded_players"]
        ranking_components = results["ranking_components"]
        ranking_explanations = results["ranking_explanations"]
        validation_checks = results["validation_checks"]
        fairness_audit = results["fairness_audit"]
        cfg_summary = results["configuration_summary"]

        # 5. Export Parquet Datasets
        output_data_dir = config.rankings_data_dir
        logger.info("Exporting processed Parquet datasets to: %s", output_data_dir)
        parquet_exports = {
            "batter_ratings": all_batters,
            "bowler_ratings": all_bowlers,
            "batting_eligibility": bat_eligibility,
            "bowling_eligibility": bowl_eligibility,
            "ranking_components": ranking_components,
            "ranking_explanations": ranking_explanations,
        }
        export_rankings_datasets(parquet_exports, output_data_dir)

        # 6. Export Analytical Reports, Excel Spreadsheets, and Markdown
        reports_dir = config.rankings_dir
        logger.info("Exporting analytical reports, CSVs, Excel, and Markdown to: %s", reports_dir)
        export_ranking_reports(
            top_10_batters=top_10_batters,
            top_10_bowlers=top_10_bowlers,
            all_batters=all_batters,
            all_bowlers=all_bowlers,
            excluded_players=excluded_players,
            ranking_cfg_dict=cfg_summary,
            validation_checks=validation_checks,
            fairness_audit=fairness_audit,
            output_dir=reports_dir,
        )

        # 7. Generate Visualizations
        charts_dir = reports_dir / "charts"
        logger.info("Generating publication-quality charts in: %s", charts_dir)
        generate_ranking_visualizations(
            top_10_batters=top_10_batters,
            top_10_bowlers=top_10_bowlers,
            all_batters=all_batters,
            all_bowlers=all_bowlers,
            excluded_players=excluded_players,
            charts_dir=charts_dir,
        )

        elapsed = time.time() - start_time
        logger.info("=" * 70)
        logger.info("PHASE 8 COMPLETE: Successfully executed in %.2f seconds.", elapsed)
        logger.info("Parquet Datasets: %s", output_data_dir)
        logger.info("CSV/XLSX Reports: %s", reports_dir)
        logger.info("Charts:           %s", charts_dir)
        logger.info("Final Report:     %s", reports_dir / "PHASE_8_FINAL_REPORT.md")
        logger.info("=" * 70)
        return 0

    except Exception as e:
        logger.exception("Phase 8 Pipeline failed with error: %s", e)
        return 1


if __name__ == "__main__":
    args = parse_args()
    exit_code = run_pipeline(dry_run=args.dry_run, profile=args.profile)
    sys.exit(exit_code)

