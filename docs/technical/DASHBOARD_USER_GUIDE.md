# PressureIQ — Dashboard Technical User Guide

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Document:** Streamlit Dashboard User & Operations Manual  
**Version:** 1.0.0  

---

## 1. Quick Launch Guide

```bash
# From repository root
python -m streamlit run dashboard/app.py
```

Runs on `http://localhost:8501`.

---

## 2. Page Navigation & Features

1. **Overview (`pages/1_Overview.py`):**
   - High-level KPIs: 883 matches, 1,082 players, 170 eligible batters, 232 eligible bowlers, 24,061 high-pressure balls.
   - Anchor highlights: Rinku Singh (#1 Batter), Joshua Little (#1 Bowler), David Miller (High-Volume Batter), Haris Rauf (High-Volume Bowler).
   - Macro delivery pressure distribution donut chart.

2. **Batter Leaderboard (`pages/2_Batter_Rankings.py`):**
   - Interactive table with search, scope toggle (Top 10 to All Eligible), and exposure sliders.
   - Plotly horizontal bar chart with 95% Bayesian confidence intervals.
   - CSV and Excel (.xlsx) export buttons.

3. **Bowler Leaderboard (`pages/3_Bowler_Rankings.py`):**
   - Interactive table with bowling role filters (Death, Powerplay, Middle) and bowling style filters (Pace vs Spin).
   - Plotly horizontal bar chart with 95% Bayesian confidence intervals.
   - CSV and Excel export buttons.

4. **Individual Player Dossier (`pages/4_Player_Analysis.py`):**
   - Searchable player dropdown.
   - Dual-role batting/bowling mode toggling.
   - 10-metric KPI performance grid with baseline retention deltas.
   - Phase 9 bootstrap density curve with shaded 95% CI bands.
   - Phase 8 algorithmic narrative callout and CSV dossier download.

5. **Multi-Player Comparison (`pages/5_Player_Comparison.py`):**
   - Side-by-side comparison of 2 to 4 players.
   - Normalized $[0, 100]$ multi-attribute radar chart.
   - Grouped bar comparison of ratings vs baseline retention.
   - Comparative matrix table with CSV export.

6. **Pressure Analysis (`pages/6_Pressure_Analysis.py`):**
   - Validated Phase 4 pressure tier definitions table.
   - Delivery counts across all 200,999 balls.
   - Strike rate degradation, dot ball escalation, and economy rate escalation across pressure tiers.

7. **Statistical Validation Scorecard (`pages/7_Statistical_Validation.py`):**
   - Official 10-dimension robustness scorecard (10/10 PASS).
   - Block bootstrap uncertainty distributions and LOMO max rank drops.
   - Sensitivity matrix across 6 alternative weight profiles.
   - 12-check data leakage audit table.

8. **Scientific Methodology (`pages/8_Methodology.py`):**
   - 11-step analytical walkthrough with exact equations, weights, and shrinkage parameters.

9. **Data Quality & Governance (`pages/9_Data_Quality.py`):**
   - Ingestion audit: raw vs cleaned rows.
   - Key uniqueness and referential integrity reports.
   - Documented pipeline limitations.

---

## 3. Operations & Compliance

- **Filtered View Notice:** Applied filters automatically trigger:
  > 📌 **Global Player Rating — Filtered View:** Displayed rankings represent candidates matching your filter criteria ordered by their validated global PressureIQ rating. They do not constitute newly recalculated competition-specific baselines.
- **Validation Gate:** Automatically checks Phase 9 scorecard outcomes; displays validation badges across all headers.

