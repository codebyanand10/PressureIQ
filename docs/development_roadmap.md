# PressureIQ — Development Roadmap

**Project:** PressureIQ  
**Title:** AI-Powered Cricket Pressure Performance Analytics and Player Ranking System  
**Competition:** SupeRR Selector Season 2 — Round 1  
**Roadmap Version:** 1.0.0 (Phase 0 Baseline)

---

## Overview

The PressureIQ project follows a phased engineering lifecycle designed for data integrity, reproducibility, and rigorous statistical validation.

```
Phase 0 ──> Phase 1 ──> Phase 2 ──> Phase 3 ──> Phase 4
 (Init)      (Explore)   (Clean)     (State)     (Pressure)
                                                    │
┌───────────────────────────────────────────────────┘
│
▼
Phase 5 ──> Phase 6 ──> Phase 7 ──> Phase 8 ──> Phase 9
(Baseline)  (Batting)   (Bowling)   (Ranking)   (Validation)
                                                    │
┌───────────────────────────────────────────────────┘
│
▼
Phase 10 ─> Phase 11 ─> Phase 12
(Dashboard) (Report)    (Audit & Submission)
```

---

## Detailed Phase Breakdown

### Phase 0 — Project Initialization & Environment Setup
- **Goal:** Establish a robust project architecture, virtual environment, central configuration, structured logging, testing suite, and baseline documentation.
- **Deliverables:** Directory structure, `src/config.py`, `src/logger.py`, `.venv`, `requirements.txt`, minimal `dashboard/app.py`, baseline tests, and docs.
- **Current Status:** **COMPLETED**

### Phase 1 — Dataset Exploration
- **Goal:** Ingest and profile all raw competition datasets (`ball_by_ball.csv`, `matches.csv`, `playing_eleven.csv`, `competitions.csv`, `teams.csv`, `competition_team_player_mapping.csv`).
- **Deliverables:** Notebook `01_dataset_exploration.ipynb`, schema profiles, distribution charts, cardinality summaries, and missingness audits.
- **Status:** Pending Phase 1 initiation.

### Phase 2 — Data Cleaning and Integration
- **Goal:** Resolve missing values, standardize player/team identifiers across tables, handle extras/dismissal discrepancies, and merge relational tables.
- **Deliverables:** `src/data_validation.py`, `src/preprocessing.py`, notebooks `02_data_quality.ipynb` and `03_dataset_relationships.ipynb`, and validated parquet tables in `data/processed/`.
- **Status:** Planned.

### Phase 3 — Match State Reconstruction
- **Goal:** Reconstruct granular match context ball-by-ball chronologically.
- **Deliverables:** `src/match_state.py`, notebook `04_match_state_reconstruction.ipynb`. Tracks cumulative runs, wickets fallen, balls remaining, current run rate, required run rate, partnership runs, and entry points.
- **Status:** Planned.

### Phase 4 — Dynamic Pressure Detection Engine
- **Goal:** Formulate and calibrate a mathematically sound dynamic **Pressure Index (PI)**.
- **Deliverables:** `src/pressure_engine.py`, notebook `05_pressure_analysis.ipynb`. Derives situational pressure weighting combining win probability swings, leverage indices, required run rates, wickets in hand, and stage of match (death overs, knockouts).
- **Status:** Planned.

### Phase 5 — Player Baseline Calculation
- **Goal:** Compute baseline performance profiles for every batter and bowler in non-pressure / regular match situations.
- **Deliverables:** `src/player_baseline.py`. Measures baseline strike rates, averages, dot-ball percentages, economy rates, and boundary percentages.
- **Status:** Planned.

### Phase 6 — Batting Performance Engine
- **Goal:** Evaluate batting performance specifically under high-pressure conditions relative to career/league baselines.
- **Deliverables:** `src/batting_engine.py`, notebook `06_batting_analysis.ipynb`. Pressure strike rate delta, clutch boundary execution, dot suppression under pressure, high-leverage wicket preservation.
- **Status:** Planned.

### Phase 7 — Bowling Performance Engine
- **Goal:** Evaluate bowling performance under high-pressure conditions relative to career/league baselines.
- **Deliverables:** `src/bowling_engine.py`, notebook `07_bowling_analysis.ipynb`. Pressure economy delta, critical wicket-taking propensity (high leverage dismissals), boundary minimization in death overs, dot-ball ratios.
- **Status:** Planned.

### Phase 8 — Player Rating and Ranking Engine
- **Goal:** Formulate composite pressure ratings, enforce sample size criteria, and generate the final rankings.
- **Deliverables:** `src/ranking_engine.py`, notebook `08_ranking_validation.ipynb`, output CSVs in `outputs/rankings/`.
  - **Top 10 Batters Under Pressure**
  - **Top 10 Bowlers Under Pressure**
- **Status:** Planned.

### Phase 9 — Statistical Validation
- **Goal:** Quantitatively test ranking stability, metric correlation, bootstrapping confidence intervals, and sensitivity to sample thresholds.
- **Deliverables:** `src/statistical_validation.py`, statistical summary charts in `outputs/charts/`.
- **Status:** Planned.

### Phase 10 — Streamlit Interactive Dashboard
- **Goal:** Build a complete, responsive interactive dashboard for exploring pressure rankings, player profile comparisons, and match state replays.
- **Deliverables:** `dashboard/app.py`, multi-page views, Plotly interactive radar charts, filtering controls.
- **Status:** Planned.

### Phase 11 — Methodology Report
- **Goal:** Compile a comprehensive, formal analytics methodology report explaining the mathematical formulation, definitions of pressure, empirical findings, and validation results.
- **Deliverables:** `src/report_generator.py`, final PDF/Markdown report in `outputs/reports/`.
- **Status:** Planned.

### Phase 12 — Final Audit and Submission
- **Goal:** Execute end-to-end regression tests, verify submission checklist against competition rubric, and finalize repository packaging.
- **Deliverables:** Verified repository, reproducible pipeline execution via `run.py`, and submission package.
- **Status:** Planned.

