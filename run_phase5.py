"""PressureIQ - Phase 5 Master Execution Pipeline.

Executes the Player Baseline Calculation Engine:
1. Loads Phase 4 delivery-level pressure dataset and cleaned metadata.
2. Constructs the master player registry across 1,217 players.
3. Computes batting and bowling overall baselines across all match situations.
4. Computes batting and bowling low-pressure baselines (pressure <= 39.99).
5. Computes contextual baselines partitioned by phase, competition, innings, and order.
6. Applies Empirical Bayes shrinkage to mitigate small-sample distortion.
7. Evaluates sample reliability tiers and assigns quality audit flags.
8. Exports processed Parquet datasets to data/processed/baselines/.
9. Generates 8 CSV analytical reports, 12 publication charts, and PHASE_5_FINAL_REPORT.md.

Usage:
    python run_phase5.py [--dry-run]
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
from src.baselines.baseline_config import BaselineConfig
from src.baselines.baseline_engine import calculate_all_player_baselines
from src.baselines.reports import (
    generate_baseline_csv_reports,
    generate_baseline_charts,
    generate_markdown_final_report,
)

logger = get_logger("pressureiq_phase5")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PressureIQ Phase 5 Player Baseline Calculation Engine")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and configuration without executing full baseline calculation and export.",
    )
    return parser.parse_args()


def load_inputs(config_obj) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load pressure dataset and cleaned metadata."""
    con = duckdb.connect()
    pressure_path = config_obj.pressure_data_dir / "pressure_scores.parquet"
    mapping_path = config_obj.data_processed_dir / "cleaned_competition_team_player_mapping.csv"
    pe_path = config_obj.data_processed_dir / "cleaned_playing_eleven.csv"
    matches_path = config_obj.data_processed_dir / "cleaned_matches.csv"

    for path, name in [
        (pressure_path, "Pressure scores parquet"),
        (mapping_path, "Cleaned player mapping CSV"),
        (pe_path, "Cleaned playing eleven CSV"),
        (matches_path, "Cleaned matches CSV"),
    ]:
        if not path.is_file():
            raise FileNotFoundError(f"{name} not found at: {path}")

    logger.info("Loading delivery pressure scores from: %s", pressure_path)
    deliveries_df = con.execute("SELECT * FROM read_parquet([?])", [str(pressure_path)]).df()
    logger.info("Loaded %d delivery events with pressure scores.", len(deliveries_df))

    logger.info("Loading player mapping from: %s", mapping_path)
    mapping_df = pd.read_csv(mapping_path)
    logger.info("Loaded %d player mapping records.", len(mapping_df))

    logger.info("Loading playing eleven from: %s", pe_path)
    playing_eleven_df = pd.read_csv(pe_path)
    logger.info("Loaded %d playing eleven records.", len(playing_eleven_df))

    logger.info("Loading matches from: %s", matches_path)
    matches_df = pd.read_csv(matches_path)
    logger.info("Loaded %d matches records.", len(matches_df))

    return deliveries_df, mapping_df, playing_eleven_df, matches_df


def run_pipeline(dry_run: bool = False) -> int:
    """Execute the Phase 5 player baseline calculation engine pipeline."""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("STARTING PHASE 5: PLAYER BASELINE CALCULATION ENGINE (Dry Run: %s)", dry_run)
    logger.info("=" * 70)

    try:
        # 1. Load Baseline Configuration
        cfg = BaselineConfig()
        logger.info(
            "Loaded BaselineConfig (version: %s, batting_low_pressure_max: %.2f, batting_high_min_balls: %d)",
            cfg.version,
            cfg.batting_low_pressure_max,
            cfg.batting_high_min_balls,
        )

        # 2. Load Datasets
        deliveries_df, mapping_df, playing_eleven_df, matches_df = load_inputs(config)

        # 3. Input Validation
        required_delivery_cols = [
            "match_id",
            "innings",
            "striker_id",
            "bowler_id",
            "batter_runs",
            "extras_runs",
            "extras_type",
            "is_legal_delivery",
            "is_wicket",
            "batting_pressure_score",
            "bowling_pressure_score",
        ]
        missing = [c for c in required_delivery_cols if c not in deliveries_df.columns]
        if missing:
            raise ValueError(f"Input delivery dataset missing required columns: {missing}")

        logger.info("Input verification passed: all required fields present.")

        if dry_run:
            logger.info("=" * 70)
            logger.info("DRY-RUN COMPLETE: Inputs and configuration validated successfully.")
            logger.info("=" * 70)
            return 0

        # 4. Execute Core Baseline Engine
        logger.info("Executing calculate_all_player_baselines...")
        baselines = calculate_all_player_baselines(
            deliveries_df=deliveries_df,
            mapping_df=mapping_df,
            playing_eleven_df=playing_eleven_df,
            matches_df=matches_df,
            config=cfg,
        )

        # 5. Export Parquet Datasets
        output_data_dir = config.baselines_data_dir
        output_data_dir.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect()

        tables_to_export = [
            ("player_registry", baselines["player_registry"]),
            ("batting_overall_baseline", baselines["batting_overall_baseline"]),
            ("batting_low_pressure_baseline", baselines["batting_low_pressure_baseline"]),
            ("bowling_overall_baseline", baselines["bowling_overall_baseline"]),
            ("bowling_low_pressure_baseline", baselines["bowling_low_pressure_baseline"]),
            ("batting_contextual_baseline", baselines["batting_contextual_baseline"]),
            ("bowling_contextual_baseline", baselines["bowling_contextual_baseline"]),
            ("baseline_reliability", baselines["baseline_reliability"]),
            ("baseline_metadata", baselines["baseline_metadata"]),
        ]

        logger.info("Exporting %d baseline datasets to Parquet in: %s", len(tables_to_export), output_data_dir)
        for tbl_name, tbl_df in tables_to_export:
            pq_path = output_data_dir / f"{tbl_name}.parquet"
            con.execute("COPY tbl_df TO ? (FORMAT PARQUET)", [str(pq_path)])
            logger.info("  Exported %-32s -> %d rows", f"{tbl_name}.parquet", len(tbl_df))

        # 6. Generate Analytical CSV Reports
        baselines_reports_dir = config.baselines_dir
        logger.info("Generating analytical CSV reports in: %s", baselines_reports_dir)
        generate_baseline_csv_reports(baselines, baselines_reports_dir)

        # 7. Generate Diagnostic Charts
        charts_dir = baselines_reports_dir / "charts"
        logger.info("Generating diagnostic charts in: %s", charts_dir)
        generate_baseline_charts(baselines, charts_dir)

        # 8. Generate Markdown Final Report
        final_report_path = baselines_reports_dir / "PHASE_5_FINAL_REPORT.md"
        logger.info("Generating final report at: %s", final_report_path)
        generate_markdown_final_report(baselines, final_report_path)

        elapsed = time.time() - start_time
        logger.info("=" * 70)
        logger.info("PHASE 5 COMPLETE: Successfully executed in %.2f seconds.", elapsed)
        logger.info("Parquet Datasets: %s", output_data_dir)
        logger.info("CSV Reports:      %s", baselines_reports_dir)
        logger.info("Charts:           %s", charts_dir)
        logger.info("Final Report:     %s", final_report_path)
        logger.info("=" * 70)
        return 0

    except Exception as e:
        logger.exception("Phase 5 Pipeline failed with error: %s", e)
        return 1


if __name__ == "__main__":
    args = parse_args()
    exit_code = run_pipeline(dry_run=args.dry_run)
    sys.exit(exit_code)
