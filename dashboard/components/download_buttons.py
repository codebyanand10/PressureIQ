"""PressureIQ Data Export & Download Component.

Generates properly formatted CSV and Excel download buttons for leaderboards and dossiers.
"""

from __future__ import annotations
import io
from typing import Optional
import pandas as pd
import streamlit as st


def render_csv_download(
    df: pd.DataFrame,
    filename: str,
    label: str = "📥 Download CSV",
    key: Optional[str] = None,
) -> None:
    """Render a CSV download button."""
    if df.empty:
        return
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        key=key,
        use_container_width=True,
    )


def render_excel_download(
    df: pd.DataFrame,
    filename: str,
    sheet_name: str = "PressureIQ_Rankings",
    label: str = "📊 Download Excel",
    key: Optional[str] = None,
) -> None:
    """Render an Excel (.xlsx) download button using an in-memory buffer."""
    if df.empty:
        return
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    excel_bytes = output.getvalue()

    st.download_button(
        label=label,
        data=excel_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,
        use_container_width=True,
    )


def render_export_suite(
    df: pd.DataFrame,
    base_filename: str,
    sheet_name: str = "Sheet1",
    key_prefix: str = "export",
) -> None:
    """Render side-by-side CSV and Excel download buttons."""
    c1, c2 = st.columns(2)
    with c1:
        render_csv_download(
            df,
            filename=f"{base_filename}.csv",
            key=f"{key_prefix}_csv",
        )
    with c2:
        render_excel_download(
            df,
            filename=f"{base_filename}.xlsx",
            sheet_name=sheet_name,
            key=f"{key_prefix}_xlsx",
        )

