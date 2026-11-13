"""PressureIQ - Phase 7 Master Execution Pipeline.

Executes the Bowling Performance Under Pressure Engine:
1. Loads Phase 4 delivery pressure scores and Phase 5 baseline datasets.
2. Evaluates bowler performance across 5 pressure categories (Very Low, Low, Moderate, High, Extreme).
3. Identifies dedicated high-pressure (pressure >= 60.0) bowling performance across 559 bowlers.
4. Compares high-pressure metrics against overall and low-pressure historical baselines.
5. Performs situational breakdown (phase, innings, competition, stage, bowling style, intensity).
6. Analyzes bowling phase roles (Powerplay, Middle, Death, Multi-Phase).
7. Computes the Bowling Pressure Performance Index (BPPI-B: 0 to 100) and explainable component breakdown.
8. Evaluates sample reliability and runs match-level block bootstrap resampling (500 resamples).
9. Classifies bowlers into evidence-based tiers (Elite, Strong, Average, Below Baseline, Insufficient Evidence).
10. Generates dynamic narrative explanations for each bowler.
11. Validates mathematical consistency, non-negativity, and domain constraints.
12. Exports 8 processed Parquet datasets to data/processed/bowling_pressure/.
13. Generates 10 analytical CSV summary reports, 14 publication charts, and PHASE_7_FINAL_REPORT.md.

Usage:
    python run_phase7.py [--dry-run]
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

import duckdb
import pandas as pd

from src.config import config
from src.logger import get_logger
from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.bowling_pressure_engine import calculate_bowling_pressure_performance
from src.bowling_pressure.reports import (
    generate_bowling_pressure_csv_reports,
    generate_bowling_pressure_charts,
    generate_markdown_final_report,
)

logger = get_logger("pressureiq_phase7")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PressureIQ Phase 7 Bowling Performance Under Pressure Engine")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and configuration without executing full calculation and parquet export.",
    )
    return parser.parse_args()


def load_inputs(config_obj) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load pressure dataset and bowling baseline datasets."""
    con = duckdb.connect()
    pressure_path = config_obj.pressure_data_dir / "pressure_scores.parquet"
    registry_path = config_obj.baselines_data_dir / "player_registry.parquet"
    bowl_overall_path = config_obj.baselines_data_dir / "bowling_overall_baseline.parquet"
    bowl_lp_path = config_obj.baselines_data_dir / "bowling_low_pressure_baseline.parquet"

    for path, name in [
        (pressure_path, "Pressure scores parquet"),
        (registry_path, "Player registry parquet"),
        (bowl_overall_path, "Bowling overall baseline parquet"),
        (bowl_lp_path, "Bowling low-pressure baseline parquet"),
    ]:
        if not path.is_file():
            raise FileNotFoundError(f"{name} not found at: {path}")

    logger.info("Loading delivery pressure scores from: %s", pressure_path)
    deliveries_df = con.execute("SELECT * FROM read_parquet([?])", [str(pressure_path)]).df()
    logger.info("Loaded %d delivery events with pressure scores.", len(deliveries_df))

    logger.info("Loading player registry from: %s", registry_path)
    registry_df = con.execute("SELECT * FROM read_parquet([?])", [str(registry_path)]).df()
    logger.info("Loaded %d player registry records.", len(registry_df))

    logger.info("Loading bowling overall baseline from: %s", bowl_overall_path)
    overall_base_df = con.execute("SELECT * FROM read_parquet([?])", [str(bowl_overall_path)]).df()
    logger.info("Loaded %d overall bowling baseline records.", len(overall_base_df))

    logger.info("Loading bowling low-pressure baseline from: %s", bowl_lp_path)
    lp_base_df = con.execute("SELECT * FROM read_parquet([?])", [str(bowl_lp_path)]).df()
    logger.info("Loaded %d low-pressure bowling baseline records.", len(lp_base_df))

    return deliveries_df, registry_df, overall_base_df, lp_base_df


def run_pipeline(dry_run: bool = False) -> int:
    """Execute the Phase 7 bowling pressure engine pipeline."""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("STARTING PHASE 7: BOWLING PERFORMANCE UNDER PRESSURE ENGINE (Dry Run: %s)", dry_run)
    logger.info("=" * 70)

    try:
        # 1. Load Configuration
        cfg = BowlingPressureConfig()
        logger.info(
            "Loaded BowlingPressureConfig (version: %s, high_pressure_threshold: %.1f, bootstrap_iters: %d)",
            cfg.version,
            cfg.high_pressure_threshold,
            cfg.bootstrap_iterations,
        )

        # 2. Load Datasets
        deliveries_df, registry_df, overall_base_df, lp_base_df = load_inputs(config)

        # 3. Input Validation
        required_cols = [
            "match_id",
            "innings",
            "bowler_id",
            "batter_runs",
            "extras_runs",
            "extras_type",
            "is_legal_delivery",
            "is_wicket",
            "bowling_pressure_score",
        ]
        missing = [c for c in required_cols if c not in deliveries_df.columns]
        if missing:
            raise ValueError(f"Input delivery dataset missing required columns: {missing}")

        logger.info("Input verification passed: all %d required columns present.", len(required_cols))

        if dry_run:
            logger.info("=" * 70)
            logger.info("DRY-RUN COMPLETE: Inputs and configuration validated successfully.")
            logger.info("=" * 70)
            return 0

        # 4. Execute Core Bowling Pressure Engine
        logger.info("Executing calculate_bowling_pressure_performance...")
        datasets = calculate_bowling_pressure_performance(
            deliveries_df=deliveries_df,
            player_registry_df=registry_df,
            overall_baseline_df=overall_base_df,
            low_pressure_baseline_df=lp_base_df,
            config=cfg,
        )

        # 5. Export Parquet Datasets
        output_data_dir = config.bowling_pressure_data_dir
        output_data_dir.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect()

        tables_to_export = [
            ("bowler_pressure_category_metrics", datasets["bowler_pressure_category_metrics"]),
            ("bowler_high_pressure_performance", datasets["bowler_high_pressure_performance"]),
            ("bowler_baseline_comparison", datasets["bowler_baseline_comparison"]),
            ("bowler_situational_performance", datasets["bowler_situational_performance"]),
            ("bowler_role_analysis", datasets["bowler_role_analysis"]),
            ("bowler_pressure_reliability", datasets["bowler_pressure_reliability"]),
            ("bowler_pressure_performance_index", datasets["bowler_pressure_performance_index"]),
            ("bowler_pressure_explanations", datasets["bowler_pressure_explanations"]),
        ]

        logger.info("Exporting %d bowling pressure datasets to Parquet in: %s", len(tables_to_export), output_data_dir)
        for tbl_name, tbl_df in tables_to_export:
            pq_path = output_data_dir / f"{tbl_name}.parquet"
            con.execute("COPY tbl_df TO ? (FORMAT PARQUET)", [str(pq_path)])
            logger.info("  Exported %-36s -> %d rows", f"{tbl_name}.parquet", len(tbl_df))

        # 6. Generate Analytical CSV Reports
        reports_dir = config.bowling_pressure_dir
        logger.info("Generating analytical CSV reports in: %s", reports_dir)
        generate_bowling_pressure_csv_reports(datasets, reports_dir)

        # 7. Generate Diagnostic Charts
        charts_dir = reports_dir / "charts"
        logger.info("Generating diagnostic charts in: %s", charts_dir)
        generate_bowling_pressure_charts(datasets, charts_dir)

        # 8. Generate Markdown Final Report
        final_report_path = reports_dir / "PHASE_7_FINAL_REPORT.md"
        logger.info("Generating final report at: %s", final_report_path)
        generate_markdown_final_report(datasets, final_report_path)

        elapsed = time.time() - start_time
        logger.info("=" * 70)
        logger.info("PHASE 7 COMPLETE: Successfully executed in %.2f seconds.", elapsed)
        logger.info("Parquet Datasets: %s", output_data_dir)
        logger.info("CSV Reports:      %s", reports_dir)
        logger.info("Charts:           %s", charts_dir)
        logger.info("Final Report:     %s", final_report_path)
        logger.info("=" * 70)
        return 0

    except Exception as e:
        logger.exception("Phase 7 Pipeline failed with error: %s", e)
        return 1


if __name__ == "__main__":
    args = parse_args()
    exit_code = run_pipeline(dry_run=args.dry_run)
    sys.exit(exit_code)
