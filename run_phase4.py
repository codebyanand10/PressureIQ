"""PressureIQ - Phase 4 Master Execution Pipeline.

Executes the Pressure Detection Engine:
1. Loads Phase 3 reconstructed match states.
2. Performs pre-delivery feature extraction.
3. Quantifies batting pressure and bowling pressure across 200,999 delivery events.
4. Assesses delivery-level reliability and enforces zero lookahead leakage.
5. Exports processed pressure datasets in Parquet and CSV formats.
6. Generates diagnostic summary CSV reports, publication charts, and PHASE_4_FINAL_REPORT.md.

Usage:
    python run_phase4.py [--dry-run]
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
from src.pressure.pressure_config import PressureConfig
from src.pressure.pressure_engine import calculate_pressure_scores
from src.pressure.pressure_validator import audit_leakage
from src.pressure.reports import (
    generate_pressure_csv_reports,
    generate_pressure_charts,
    generate_markdown_final_report,
)

logger = get_logger("pressureiq_phase4")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PressureIQ Phase 4 Pressure Detection Engine Pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and configuration without writing the final pressure dataset.",
    )
    return parser.parse_args()


def load_inputs(config_obj) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load reconstructed match states and matches metadata using DuckDB."""
    con = duckdb.connect()
    match_states_path = config_obj.data_processed_dir / "match_state_reconstructed.parquet"
    matches_csv_path = config_obj.data_processed_dir / "cleaned_matches.csv"

    if not match_states_path.is_file():
        raise FileNotFoundError(f"Reconstructed match states not found at: {match_states_path}")
    if not matches_csv_path.is_file():
        raise FileNotFoundError(f"Cleaned matches metadata not found at: {matches_csv_path}")

    logger.info("Loading reconstructed match states from: %s", match_states_path)
    match_states_df = con.execute("SELECT * FROM read_parquet([?])", [str(match_states_path)]).df()
    logger.info("Loaded %d match state delivery records.", len(match_states_df))

    logger.info("Loading matches metadata from: %s", matches_csv_path)
    matches_df = pd.read_csv(matches_csv_path)
    logger.info("Loaded %d matches metadata records.", len(matches_df))

    return match_states_df, matches_df


def run_pipeline(dry_run: bool = False) -> int:
    """Execute the Phase 4 pressure detection engine pipeline."""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("STARTING PHASE 4: PRESSURE DETECTION ENGINE (Dry Run: %s)", dry_run)
    logger.info("=" * 70)

    try:
        # 1. Load Configuration
        cfg = PressureConfig()
        logger.info("Loaded PressureConfig (version: %s, rrr_cap: %.1f)", cfg.version, cfg.rrr_cap)

        # 2. Load Datasets
        match_states_df, matches_df = load_inputs(config)

        # 3. Input Validation & Eligibility
        required_cols = [
            "match_id",
            "innings",
            "delivery_sequence",
            "is_legal_delivery",
            "runs_before",
            "wickets_before",
            "legal_balls_bowled_before",
            "legal_balls_remaining_before",
            "is_chasing_innings",
        ]
        missing = [c for c in required_cols if c not in match_states_df.columns]
        if missing:
            raise ValueError(f"Input match states missing mandatory columns: {missing}")

        logger.info("Input validation passed: all %d required columns present.", len(required_cols))

        if dry_run:
            logger.info("=" * 70)
            logger.info("DRY-RUN COMPLETE: Inputs and configuration validated successfully.")
            logger.info("=" * 70)
            return 0

        # 4. Execute Core Pressure Engine
        logger.info("Executing calculate_pressure_scores across %d deliveries...", len(match_states_df))
        enriched_df = calculate_pressure_scores(
            match_states_df=match_states_df,
            matches_meta_df=matches_df,
            config=cfg,
        )

        # 5. Export Processed Datasets
        output_data_dir = config.pressure_data_dir
        output_data_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = output_data_dir / "pressure_scores.parquet"
        csv_path = output_data_dir / "pressure_scores.csv"

        logger.info("Writing output Parquet dataset to: %s", parquet_path)
        con = duckdb.connect()
        con.execute("COPY enriched_df TO ? (FORMAT PARQUET)", [str(parquet_path)])
        logger.info("Exported %d rows to Parquet.", len(enriched_df))

        logger.info("Writing output CSV dataset to: %s", csv_path)
        enriched_df.to_csv(csv_path, index=False)
        logger.info("Exported CSV dataset.")

        # 6. Generate Diagnostic CSV Reports and Charts
        pressure_reports_dir = config.pressure_dir
        charts_dir = pressure_reports_dir / "charts"
        logger.info("Generating CSV analytical reports in: %s", pressure_reports_dir)
        generate_pressure_csv_reports(enriched_df, pressure_reports_dir)

        logger.info("Generating diagnostic charts in: %s", charts_dir)
        generate_pressure_charts(enriched_df, charts_dir)

        # 7. Generate Final Report
        final_report_path = pressure_reports_dir / "PHASE_4_FINAL_REPORT.md"
        leakage_metrics = audit_leakage(enriched_df)
        generate_markdown_final_report(enriched_df, final_report_path, leakage_metrics)

        elapsed = time.time() - start_time
        logger.info("=" * 70)
        logger.info("PHASE 4 COMPLETE: Successfully executed in %.2f seconds.", elapsed)
        logger.info("Parquet: %s", parquet_path)
        logger.info("Reports: %s", pressure_reports_dir)
        logger.info("Final Report: %s", final_report_path)
        logger.info("=" * 70)
        return 0

    except Exception as e:
        logger.exception("Phase 4 Pipeline failed with error: %s", e)
        return 1


if __name__ == "__main__":
    args = parse_args()
    exit_code = run_pipeline(dry_run=args.dry_run)
    sys.exit(exit_code)
