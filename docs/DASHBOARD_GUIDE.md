# PressureIQ — Interactive Analytics Dashboard User Guide

**Product Name:** PressureIQ  
**Tagline:** Beyond Performance. Under Pressure.  
**Subtitle:** Cricket Pressure Performance Analytics  
**Platform:** Streamlit Multi-Page Application  
**Coverage Scope:** IPL & T20 Internationals (2022 – Present)

---

## 1. Overview & Launching the Dashboard

### Launch Command
From the root of the `PressureIQ` repository:

```bash
# Windows
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py

# Linux / macOS
python -m streamlit run dashboard/app.py
```

The application will launch on your default local browser at `http://localhost:8501`.

---

## 2. Multi-Page Architecture & Navigation

The application uses Streamlit's official multi-page architecture with `st.navigation`. Navigation is located in the left sidebar:

### Page 1: Overview Dashboard (`pages/1_Overview.py`)
- **Macro Analytics KPIs:** High-level counts of matches analyzed (883), registered players, eligible batters (170), eligible bowlers (232), and high-pressure deliveries (24,061).
- **System Anchors & Distinctions:** Highlights #1 clutch batter (**Rinku Singh**, FBPR: 77.07), #1 clutch bowler (**Joshua Little**, FBOR: 50.05), and highest-volume reliable performers (**David Miller**, **Haris Rauf**).
- **Top 5 Batters & Bowlers:** Quick comparison tables.
- **Delivery Pressure Distribution:** Donut chart of all historical balls broken down by validated Phase 4 pressure tiers.

### Page 2: Batter Rankings (`pages/2_Batter_Rankings.py`)
- **Official Batter Leaderboard:** Displays #1 to #170 eligible batters.
- **Interactive Controls:**
  - *Player Name Search:* Substring search (e.g. "Rinku", "Miller").
  - *Leaderboard Scope:* Switch between Top 10, Top 25, Top 50, or All Eligible.
  - *Minimum Pressure Exposure:* Filter by minimum balls faced under pressure ($P \ge 60$).
- **Interactive Plotly Horizontal Bar Chart:** Visualizes FBPR with asymmetric 95% bootstrap confidence interval error whiskers.
- **Export Suite:** Export current leaderboard to CSV or Excel (.xlsx).

### Page 3: Bowler Rankings (`pages/3_Bowler_Rankings.py`)
- **Official Bowler Leaderboard:** Displays #1 to #232 eligible bowlers.
- **Interactive Controls:**
  - *Bowling Role Filter:* Filter by Death overs, Powerplay, or Middle overs.
  - *Bowling Style Filter:* Filter by Pace vs Spin.
  - *Exposure Slider:* Filter by minimum legal deliveries bowled.
- **Interactive Plotly Horizontal Bar Chart:** Visualizes FBOR with asymmetric 95% bootstrap confidence interval error whiskers.
- **Export Suite:** Export current leaderboard to CSV or Excel (.xlsx).

### Page 4: Individual Player Analysis (`pages/4_Player_Analysis.py`)
- **Player Selector:** Choose any eligible candidate from the dropdown.
- **Dual-Role Toggle:** If a player qualifies as both batter and bowler (e.g., all-rounders), toggle between their Batting profile and Bowling profile seamlessly.
- **10-Metric Performance Grid:**
  - *Batters:* HP Runs, Balls Faced, Strike Rate, Batting Average, BPPI, Boundary %, Dot %, HP Matches, HP Innings, Dismissals.
  - *Bowlers:* HP Wickets, Overs Bowled, HP Economy, Bowling Average, BPPI-B, Dot %, Runs Conceded, Bowling Strike Rate, HP Matches, Primary Role.
- **Baseline Retention Bar Chart:** Side-by-side comparison of normal baseline vs low pressure vs high pressure.
- **Phase 9 Bootstrap Density Curve:** Empirical probability distribution curve showing the official rating, bootstrap mean, and shaded 95% confidence interval band.
- **Official Phase 8 Narrative Callout:** Displays rating rationale, key strengths, baseline comparison, and model limitations.
- **Download Dossier:** One-click CSV export of the individual player's complete statistical record.

### Page 5: Player Comparison (`pages/5_Player_Comparison.py`)
- **Discipline Selector:** Select Batting Comparison or Bowling Comparison.
- **Multi-Player Selector:** Choose 2 to 4 players to evaluate head-to-head.
- **Multi-Dimensional Radar Chart:** Normalized $[0, 100]$ multi-axis polar plot comparing rating, execution, baseline retention, boundary control, dot control, and sample depth without distorting units.
- **Side-by-Side Matrix Table:** Full comparative table comparing all metrics with delta indicators.
- **Export Comparison:** Export comparison matrix to CSV.

### Page 6: Pressure Dynamics & Situational Analysis (`pages/6_Pressure_Analysis.py`)
- **Validated Pressure Tiers:** Clear table of Phase 4 definitions ($0–20$ Very Low, $20–40$ Low, $40–60$ Moderate, $60–80$ High, $80–100$ Extreme).
- **Macro Delivery Distribution:** Detailed counts and percentages across 200,999 historical deliveries.
- **Performance Shift Curves:** Line and bar charts demonstrating strike rate decline, dot ball escalation, economy rate deterioration, and wicket rates across pressure tiers.
- **Situational Anatomy:** Explanations of Required Run Rate (RRR) pressure, wicket depletion leverage, and first-innings baseline modeling.

### Page 7: Statistical Validation & Robustness (`pages/7_Statistical_Validation.py`)
- **Official 10-Dimension Scorecard:** Complete table displaying Batting Status, Bowling Status, and Empirical Evidence for all 10 robustness dimensions (all 10 PASSED).
- **Bootstrap Uncertainty & LOMO Stability:** Full table of bootstrap mean, 95% CIs, median ranks, and Leave-One-Match-Out (LOMO) max rank drop.
- **Weight Sensitivity Matrix:** Performance across 6 alternative weight profiles (Balanced, Absolute-Focused, Baseline-Focused, Consistency-Focused, Reliability-Focused, Pressure-Difficulty-Focused).
- **Fairness Audits:** Cross-competition (IPL vs T20I) and role representation breakdowns.
- **12-Check Data Leakage Audit:** Complete report of all 12 temporal, causal, and cricket-specific integrity checks (0 failures).

### Page 8: Scientific Methodology (`pages/8_Methodology.py`)
- **11 Analytical Phases:** Accordion walkthrough detailing data sources, cleaning, state reconstruction, pressure detection formulas, Empirical Bayes shrinkage derivations, BPPI formulations, composite rating calculations, and validation protocols.
- **Exact Formulas & Weights:** No simplified approximations; matches the exact Python implementations in `src/`.

### Page 9: Data Quality & Governance (`pages/9_Data_Quality.py`)
- **Ingestion Audit:** Cleaned vs raw row counts for all 6 core datasets.
- **Quality Dimensions:** Key uniqueness, referential integrity, and cricket logic validation.
- **Known Limitations:** Documented sample depth nuances, super over constraints, and regional tracking variations.

---

## 3. Global Filters & The Filtered-View Rule

The sidebar provides global filters:
- **Competition:** All Competitions, IPL, T20I.
- **Reliability:** All Levels, High, Medium.
- **Reset All Filters:** Restores default global views.

### Compliance Rule
When a filter is applied (e.g. filtering to IPL only), the dashboard displays a prominent notice:
> 📌 **Global Player Rating — Filtered View:** Displayed rankings represent candidates matching your filter criteria ordered by their validated global PressureIQ rating. They do not constitute newly recalculated competition-specific baselines.

This ensures full adherence to Section 15 of the Phase 10 specification.

---

## 4. Troubleshooting & Performance Tips

1. **Streamlit Port Already in Use:**
   ```bash
   python -m streamlit run dashboard/app.py --server.port 8502
   ```
2. **DuckDB or Parquet File Path Errors:**
   Ensure the current working directory is the root of the repository (`PressureIQ/`). Paths are dynamically resolved relative to `PROJECT_ROOT`.
3. **Data Caching:**
   Datasets are cached in memory using `@st.cache_data`. If you modify any processed data files, click **"Clear cache"** in the top-right Streamlit burger menu or restart the server.

