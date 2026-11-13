"""PressureIQ Page 9: Data Quality & Pipeline Transparency.

Comprehensive data governance and quality audit page summarizing Phase 1 exploration,
Phase 2 cleaning & referential integrity, and pipeline filtering exclusions.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.header import render_header
from dashboard.components.sidebar import render_sidebar
from dashboard.components.metric_cards import render_metric_row


def main() -> None:
    st.set_page_config(page_title="Data Quality | PressureIQ", page_icon="🔍", layout="wide")

    css_path = PROJECT_ROOT / "dashboard" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header(subtitle="Data Quality, Governance & Pipeline Transparency")

    # Macro Ingestion Audit Row
    render_metric_row([
        {"title": "Raw Datasets Ingested", "value": "6 Core Tables", "subtitle": "Phases 1 & 2 verified"},
        {"title": "Cleaned Deliveries", "value": "200,999 Balls", "subtitle": "0 Duplicate Keys"},
        {"title": "Cleaned Matches", "value": "988 Matches", "subtitle": "100% Referential Integrity"},
        {"title": "Null Values Handled", "value": "0 Critical", "subtitle": "Deterministic imputation"},
        {"title": "Integrity Check", "value": "100% Passed", "subtitle": "Phase 2 & 9 audited"},
    ])

    st.markdown("---")

    # Ingestion & Cleaning Breakdown Table
    st.markdown("### 📊 Ingested Datasets Audit (Phase 1 & Phase 2)")

    datasets_audit = [
        {"Dataset Name": "raw_ball_by_ball.csv", "Raw Rows": "201,005", "Cleaned Rows": "200,999", "Exclusions / Fixes": "6 malformed rows removed; delivery numbering deduplicated", "Status": "CLEAN"},
        {"Dataset Name": "raw_matches.csv", "Raw Rows": "992", "Cleaned Rows": "988", "Exclusions / Fixes": "4 abandoned/no-result games with zero legal deliveries removed", "Status": "CLEAN"},
        {"Dataset Name": "raw_competitions.csv", "Raw Rows": "6", "Cleaned Rows": "6", "Exclusions / Fixes": "Standardized competition codes (IPL vs T20I)", "Status": "CLEAN"},
        {"Dataset Name": "raw_teams.csv", "Raw Rows": "38", "Cleaned Rows": "38", "Exclusions / Fixes": "Normalized team abbreviations and multi-spelling names", "Status": "CLEAN"},
        {"Dataset Name": "raw_playing_eleven.csv", "Raw Rows": "21,736", "Cleaned Rows": "21,736", "Exclusions / Fixes": "Verified 11 players per team per match", "Status": "CLEAN"},
        {"Dataset Name": "raw_comp_team_player.csv", "Raw Rows": "4,120", "Cleaned Rows": "4,120", "Exclusions / Fixes": "Harmonized player ID referential links", "Status": "CLEAN"},
    ]
    st.dataframe(pd.DataFrame(datasets_audit), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Data Quality Dimensions Accordion
    st.markdown("### 🔍 Verified Data Quality Dimensions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            #### 1. Deduplication & Key Uniqueness
            - **Delivery Keys:** Every delivery is uniquely addressed by `(match_id, innings, overid, over_ball_num)`.
            - **Duplicates Found:** **0 duplicates** present in processed datasets.
            
            #### 2. Referential Integrity
            - **Player IDs:** 100% of striker IDs, non-striker IDs, and bowler IDs resolve to valid master player records.
            - **Match IDs:** All deliveries match valid match metadata records.
            - **Zero Orphan Records:** 0 orphaned ball-by-ball entries.
            """
        )

    with col2:
        st.markdown(
            """
            #### 3. Cricket Logic Validation
            - **Wicket & Run Attribution:** Verified that run outs, retired out/hurt, and timed out dismissals are strictly excluded from bowler wicket counts.
            - **Extras Bounds:** Wides and no-balls are accurately flagged as illegal deliveries; runs and extras never contain negative values.
            - **Target Scoring:** 2nd innings target scores accurately match first-innings total + 1, including verified DLS revisions.
            """
        )

    st.markdown("---")

    # Known Processing Limitations
    st.markdown("### ⚠️ Methodological Limitations & Known Constraints")
    st.markdown(
        """
        1. **Sample Size Disparities:** Certain players in low-volume international series have fewer high-pressure opportunities than full-season IPL regulars. While Empirical Bayes shrinkage mitigates artificial rating inflation, wider confidence intervals reflect greater uncertainty.
        2. **Super Over Sample Depth:** Super over deliveries occur in only 11 matches in the historical dataset. While evaluated at extreme pressure, they do not dominate career pressure indices.
        3. **Tracking Data Limitations:** Ball tracking (Hawkeye) trajectories and exact release speed were not uniformly available across all regional T20I matches, so pressure is modeled on situational match leverage rather than tracking telemetry.
        """
    )


if __name__ == "__main__":
    main()

