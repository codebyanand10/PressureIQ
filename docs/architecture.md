# PressureIQ — System Architecture

**Project:** PressureIQ  
**Title:** AI-Powered Cricket Pressure Performance Analytics and Player Ranking System  
**Competition:** SupeRR Selector Season 2 — Round 1  
**Architecture Document Version:** 1.0.0 (Phase 0 Foundation)

---

## 1. Architectural Philosophy

PressureIQ is engineered as a modular, decoupled analytical platform that separates raw cricket event ingestion from match-state reconstruction, situational pressure quantification, and comparative player performance evaluation.

The system ensures that raw match events remain immutable, while analytical pipelines produce reproducible, validated ratings and rankings.

```
┌────────────────────────────────────────────────────────┐
│                   Presentation Layer                   │
│   Streamlit Dashboard (dashboard/app.py & pages)      │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│                    Reporting Layer                     │
│    Methodology & Audit Generator (report_generator.py) │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│                     Ranking Layer                      │
│     Composite Scoring & Normalization (ranking_engine) │
│     Statistical Significance (statistical_validation)  │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│                   Analytical Layer                     │
│   Dynamic Pressure Indexing (pressure_engine.py)       │
│   Batting Pressure Engine (batting_engine.py)          │
│   Bowling Pressure Engine (bowling_engine.py)          │
│   Career Baseline Engine (player_baseline.py)          │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│                   Processing Layer                     │
│   Match State Reconstruction (match_state.py)          │
│   Schema & Integrity Validation (data_validation.py)   │
│   Transformation & Cleaning (preprocessing.py)         │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│                      Data Layer                        │
│   Raw Relational Cricket Datasets (data_loader.py)     │
│   Ball-by-ball, Matches, Lineups, Competitions, Teams  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Layers

### A. Data Layer (`data/` & `src/data_loader.py`)
- **Responsibility:** Ingests relational cricket datasets spanning T20 and T20I matches from 2022 onwards.
- **Components:**
  - `data/raw/`: Read-only storage for original datasets (`matches.csv`, `ball_by_ball.csv`, `playing_eleven.csv`, `competitions.csv`, `teams.csv`, `competition_team_player_mapping.csv`).
  - `data/intermediate/`: Optimized columnar checkpoints (e.g., Parquet / Arrow) for accelerated intermediate queries.
  - `data/processed/`: Cleaned, validated, and normalized event tables ready for state reconstruction.
  - `data/external/`: External reference datasets (venue characteristics, era benchmarks).

### B. Processing Layer (`src/data_validation.py`, `src/preprocessing.py`, `src/match_state.py`)
- **Responsibility:** Cleans, reconciles, and reconstructs chronological match state per ball.
- **Key Operations:**
  - Validation: Verifies ball sequences, score consistency, extras calculations, and dismissal mapping.
  - Chronological Reconstruction: Tracks cumulative score, wickets fallen, balls remaining, current run rate (CRR), and required run rate (RRR) for chases.
  - Context Enrichment: Incorporates venue dimensions/scoring patterns, pitch behavior signals (spin/pace splits, stroke execution, delivery style).

### C. Analytical Layer (`src/pressure_engine.py`, `src/player_baseline.py`, `src/batting_engine.py`, `src/bowling_engine.py`)
- **Responsibility:** Quantifies situational pressure and measures player delta performance.
- **Key Modules:**
  - `pressure_engine.py`: Computes a continuous, dynamic **Pressure Index (PI)** ranging from 0.0 to 1.0 (or scaled 0–100) based on win-probability swing, RRR leverage, wickets in hand, and match stage (death overs, knockouts).
  - `player_baseline.py`: Establishes each player's contextual baseline across regular/low-pressure situations.
  - `batting_engine.py`: Computes high-pressure batting efficiency (pressure strike rate delta, boundary percentage under pressure, clutch survival rate, dot-ball suppression).
  - `bowling_engine.py`: Computes high-pressure bowling efficiency (pressure economy delta, death-over wicket value, dot-ball frequency in clutch overs, boundary concession minimization).

### D. Ranking Layer (`src/ranking_engine.py`, `src/statistical_validation.py`)
- **Responsibility:** Aggregates performance dimensions into objective composite scores and validates statistical significance.
- **Key Modules:**
  - `ranking_engine.py`: Normalizes metrics, applies sample size thresholds (minimum balls faced / bowled in high-pressure states), and generates:
    - **Top 10 Batters Under Pressure**
    - **Top 10 Bowlers Under Pressure**
  - `statistical_validation.py`: Performs bootstrap hypothesis testing, confidence interval estimation, sensitivity analysis, and stability tests across seasons (2022–2026).

### E. Dashboard Layer (`dashboard/app.py`, `dashboard/pages/`, `dashboard/components/`)
- **Responsibility:** Interactive visualization and exploratory dashboard built with Streamlit and Plotly.
- **Capabilities:**
  - Pressure overview and situational filters (chasing vs setting, death overs, match stage).
  - Interactive Top 10 leaderboards with radar charts, breakdown metrics, and head-to-head comparisons.
  - Deep-dive player profile cards showing baseline vs pressure splits.

### F. Reporting Layer (`src/report_generator.py`)
- **Responsibility:** Generates audit-ready reports, Markdown executive summaries, and methodology documentation for competition submission.

---

## 3. Central Utilities & Cross-Cutting Concerns

- **Configuration Management (`src/config.py`):** Centralized singleton pattern reading from `config/settings.yaml`, providing platform-agnostic `pathlib.Path` resolutions and directory validation.
- **Logging Infrastructure (`src/logger.py`):** Reusable logger writing structured records with timestamps and line numbers to both stdout and `outputs/logs/pressureiq.log`.
- **Environment Management:** Driven by `.env` with fallback defaults, ensuring zero hardcoded secrets.
