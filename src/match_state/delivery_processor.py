"""PressureIQ - Chronological Delivery Processor.

Processes delivery records in chronological sequence, classifies legal versus
illegal balls, extracts scoring and dismissal metrics, and guarantees exact
traceability to original delivery identifiers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from src.logger import get_logger

logger = get_logger("PressureIQ.MatchState.DeliveryProcessor")

# Delivery categories where ball is re-bowled and does not decrement the legal ball counter
ILLEGAL_EXTRAS = {"wide", "Overstep", "other"}


def process_deliveries(bbb_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and standardize deliveries for sequential match state calculation.

    Args:
        bbb_df: Ball-by-ball DataFrame containing delivery events.

    Returns:
        Sorted, enriched DataFrame with delivery metrics and legal ball classification.
    """
    logger.info(f"Processing {len(bbb_df):,} delivery events...")
    processed = bbb_df.copy()

    # Guarantee stable delivery ordering index
    if "delivery_order_idx" not in processed.columns:
        processed["delivery_order_idx"] = np.arange(len(processed), dtype=np.int64)

    # Sort strictly by match, innings, and delivery order
    sort_cols = ["match_id", "innings", "delivery_order_idx"]
    processed = processed.sort_values(by=sort_cols).reset_index(drop=True)

    # Re-verify sequence within innings
    processed["delivery_sequence"] = processed.groupby(["match_id", "innings"]).cumcount() + 1

    # Extract scoring metrics
    processed["batter_runs"] = processed["runs"].fillna(0).astype(int)
    extras1 = processed["extras1_runs"].fillna(0).astype(int)
    extras2 = processed["extras_2_runs"].fillna(0).astype(int)
    processed["extras_runs"] = extras1 + extras2
    processed["delivery_runs"] = processed["batter_runs"] + processed["extras_runs"]

    # Extract dismissal metrics
    processed["is_wicket"] = processed["is_wicket"].astype(bool)
    processed["wickets_on_delivery"] = processed["is_wicket"].astype(int)

    # Legal delivery classification (wides, oversteps, and other no-balls are illegal)
    is_illegal = processed["extras_type"].isin(ILLEGAL_EXTRAS)
    processed["is_legal_delivery"] = ~is_illegal

    logger.info(
        f"Delivery processing complete: {processed['is_legal_delivery'].sum():,} legal balls, "
        f"{(~processed['is_legal_delivery']).sum():,} illegal balls."
    )
    return processed

