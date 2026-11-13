# PressureIQ — Project Technical Documentation

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Document:** Technical Implementation & Codebase Architecture  
**Target:** SupeRR Selector Season 2 — Round 1  
**Version:** 1.0.0  

---

## 1. System Engineering Architecture

PressureIQ is implemented as a modular Python package adhering to Clean Architecture principles. Business logic, state manipulation, statistical modeling, and data presentation reside in decoupled directories:

- `src/config.py`: Central path and configuration management reading `config/settings.yaml`.
- `src/logger.py`: Centralized structured logging to `outputs/logs/pressureiq.log` and stdout.
- `src/match_state/`: Reconstructs match state ball-by-ball.
- `src/pressure/`: Calculates continuous batting and bowling pressure indices.
- `src/baselines/`: Computes Empirical Bayes shrunk player benchmarks.
- `src/batting_pressure/`: Calculates BPPI and situational batting metrics.
- `src/bowling_pressure/`: Calculates BPPI-B, death-over leverage, and bowling metrics.
- `src/ranking/`: Executes unified multi-pillar rating models and produces official Top 10 leaderboards.
- `src/validation/`: Executes block bootstrap, sensitivity scans, and data leakage audits.
- `dashboard/`: Multi-page Streamlit application.

---

## 2. Directory Layout & Module Index

```text
PressureIQ/
├── config/
│   └── settings.yaml             # Core configuration parameters, thresholds, and weights
├── data/
│   ├── raw/                      # Original immutable competition CSV files
│   └── processed/                # Cleaned, validated, and intermediate Parquet datasets
├── docs/
│   ├── methodology/              # Formal methodology report and mathematical formulation
│   └── technical/                # Technical documentation, pipeline specs, and user guides
├── outputs/
│   ├── rankings/                 # Official Top 10 rankings in CSV, XLSX, and Markdown
│   ├── validation/               # Phase 9 validation reports, scorecard, and 300 DPI charts
│   ├── methodology/              # Final Phase 11 deliverables (Markdown, DOCX, PDF)
│   └── dashboard/                # Phase 10 dashboard final report and dependency audit
├── src/                          # Analytical engine packages
├── dashboard/                    # Streamlit multi-page dashboard
└── tests/                        # 183 automated pytest test cases
```

---

## 3. Execution Pipeline Reference Scripts

The complete analytics workflow can be executed sequentially or selectively using dedicated command-line runners:
- `python run_phase2.py`: Data cleaning, deduplication, and referential integration.
- `python run_phase3.py`: Match state reconstruction across 200,999 deliveries.
- `python run_phase4.py`: Pressure detection and continuous scoring.
- `python run_phase5.py`: Baseline calculation with Empirical Bayes shrinkage.
- `python run_phase6.py`: Batting pressure performance evaluation (BPPI).
- `python run_phase7.py`: Bowling pressure performance evaluation (BPPI-B).
- `python run_phase8.py`: Unified rating calculation and Top 10 ranking generation.
- `python run_phase9.py`: Statistical validation, block bootstrap, and leakage audit.
- `python -m streamlit run dashboard/app.py`: Interactive analytics dashboard.
- `python run_phase11.py`: Automated documentation validation and PDF/DOCX generation.

