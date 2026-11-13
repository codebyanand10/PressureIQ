"""Tests for CSV and Excel download data formatting."""

from __future__ import annotations
import io
import pytest
import pandas as pd
from dashboard.services.ranking_service import filter_batter_rankings, filter_bowler_rankings


def test_export_dataframe_serialization():
    """Verify that ranking dataframes can be cleanly serialized to CSV and Excel bytes."""
    top_10 = filter_batter_rankings(top_n=10)

    # CSV serialization test
    csv_str = top_10.to_csv(index=False)
    assert "Rinku Singh" in csv_str
    assert "final_fbpr" in csv_str

    # Excel serialization test
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        top_10.to_excel(writer, sheet_name="TestSheet", index=False)
    excel_bytes = output.getvalue()
    assert len(excel_bytes) > 1000

    # Read back Excel to ensure schema integrity
    read_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name="TestSheet")
    assert len(read_df) == 10
    assert read_df.iloc[0]["player_name"] == "Rinku Singh"

