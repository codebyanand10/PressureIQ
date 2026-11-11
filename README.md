# PressureIQ

**AI-Powered Cricket Pressure Performance Analytics and Player Ranking System**  
*SupeRR Selector Season 2 — Round 1*

---

## 1. Project Overview

**PressureIQ** is an advanced, data-driven cricket analytics platform designed to evaluate and rank player performances under high-pressure match situations. Utilizing historical Indian Premier League (IPL) and Twenty20 International (T20I) ball-by-ball delivery datasets from 2022 onwards, PressureIQ quantifies how players perform when the game is on the line compared to their contextual baseline levels.

The ultimate objective of PressureIQ is to identify and rank:
- **Top 10 Batters Under Pressure**
- **Top 10 Bowlers Under Pressure**

Through dynamic match-state reconstruction, continuous pressure index modeling, and rigorous statistical validation, PressureIQ provides objective, reproducible insights for high-performance selection.

---

## 2. Competition Context

- **Competition:** SupeRR Selector Season 2 — Round 1
- **Focus Area:** Measuring performance in high-pressure match situations relative to baseline performance.
- **Dataset Scope:** T20 and T20I matches (2022 to 2026), covering 883 matches, 200,999+ deliveries, 1,082 players, and 38 teams across international series and leagues.

---

## 3. Technology Stack

- **Core Language:** Python 3.11+
- **Data Engineering:** Pandas, NumPy, PyArrow
- **Machine Learning & Statistics:** Scikit-learn, SciPy, Statsmodels
- **Visualization:** Matplotlib, Seaborn, Plotly
- **Interactive Dashboard:** Streamlit
- **Utilities & Config:** Joblib, OpenPyXL, PyYAML, Python-dotenv
- **Testing & Quality Assurance:** Pytest, Pytest-cov

---

## 4. Project Directory Structure

```text
PressureIQ/
│
├── data/
│   ├── raw/                  # Original, immutable competition CSV datasets
│   ├── processed/            # Cleaned and schema-validated tables
│   ├── intermediate/         # Accelerated columnar checkpoints (Parquet)
│   └── external/             # External contextual data (venues, conditions)
│
├── notebooks/                # Chronological Jupyter development notebooks
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_data_quality.ipynb
│   ├── 03_dataset_relationships.ipynb
│   ├── 04_match_state_reconstruction.ipynb
│   ├── 05_pressure_analysis.ipynb
│   ├── 06_batting_analysis.ipynb
│   ├── 07_bowling_analysis.ipynb
│   └── 08_ranking_validation.ipynb
│
├── src/                      # Core analytical engines and application packages
│   ├── __init__.py
│   ├── config.py             # Central path and YAML configuration management
│   ├── logger.py             # Structured logging with file and console handlers
│   ├── data_loader.py        # Raw data ingestion pipeline
│   ├── data_validation.py    # Schema integrity and anomaly auditing
│   ├── preprocessing.py      # Cleaning and feature engineering
│   ├── match_state.py        # Ball-by-ball chronological state reconstruction
│   ├── pressure_engine.py    # Dynamic continuous pressure index engine
│   ├── batting_engine.py     # High-pressure batting metrics and deltas
│   ├── bowling_engine.py     # High-pressure bowling metrics and deltas
│   ├── player_baseline.py    # Non-pressure player baseline calculations
│   ├── ranking_engine.py     # Composite scoring and Top 10 ranking generation
│   ├── statistical_validation.py # Bootstrapping, stability and hypothesis testing
│   └── report_generator.py   # Automated audit and methodology report generator
│
├── dashboard/                # Interactive Streamlit application
│   ├── app.py                # Dashboard entry point
│   ├── components/           # Reusable UI widgets and visual components
│   ├── pages/                # Multi-page dashboard views
│   ├── styles/               # Custom CSS themes and styles
│   └── assets/               # Branding, logos, and iconography
│
├── tests/                    # Automated testing suite
│   ├── __init__.py
│   ├── test_config.py        # Tests for configuration and path resolution
│   ├── test_logger.py        # Tests for logging infrastructure
│   └── test_project_structure.py # Tests for directory structure and core files
│
├── outputs/                  # Generated analytical artifacts
│   ├── rankings/             # Official Top 10 rankings (CSV)
│   ├── charts/               # Publication-grade figures and plots
│   ├── reports/              # Methodology and validation reports
│   └── logs/                 # Runtime application log files (pressureiq.log)
│
├── config/
│   └── settings.yaml         # Central project settings and directory mappings
│
├── docs/                     # Project documentation
│   ├── architecture.md       # High-level system architecture and data flows
│   ├── development_roadmap.md# Roadmap across all 13 development phases
│   └── environment_setup.md  # Multi-platform environment setup instructions
│
├── .env.example              # Template for environment variables
├── .gitignore                # Comprehensive Git exclusion rules
├── requirements.txt          # Pinned project dependencies
├── README.md                 # Project documentation
├── verify_dependencies.py    # Dependency audit and environment verification script
└── run.py                    # Application verification entry point
```

---

## 5. Getting Started & Installation

### A. Clone & Setup Environment

#### Windows (PowerShell)
```powershell
cd PressureIQ
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Linux / macOS
```bash
cd PressureIQ
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### B. Verify Dependencies & Environment
```bash
python verify_dependencies.py
```

### C. Run the Application Diagnostics
```bash
python run.py
```

### D. Execute the Test Suite
```bash
python -m pytest -v --cov=src
```

### E. Launch the Streamlit Dashboard
```bash
python -m streamlit run dashboard/app.py
```

---

## 6. Development Lifecycle & Roadmap

| Phase | Phase Name | Focus & Scope | Status |
| :---: | :--- | :--- | :---: |
| **0** | **Project Initialization** | Architecture, configuration, logging, testing suite, docs | **COMPLETED** |
| **1** | **Dataset Exploration** | Raw dataset profiling, summary statistics, missingness audits | *Next Up* |
| **2** | **Data Cleaning & Integration** | Schema validation, identifier harmonization, entity relational integrity | Planned |
| **3** | **Match State Reconstruction** | Cumulative scores, balls remaining, wickets in hand, RRR/CRR tracking | Planned |
| **4** | **Pressure Detection Engine** | Dynamic Pressure Index (PI) formulation and situation classification | Planned |
| **5** | **Player Baseline Calculation** | Non-pressure benchmark metrics for batters and bowlers | Planned |
| **6** | **Batting Performance Engine** | High-pressure batting delta, clutch boundary execution, dot suppression | Planned |
| **7** | **Bowling Performance Engine** | High-pressure economy delta, clutch wicket propensity, death overs | Planned |
| **8** | **Ranking & Rating Engine** | Composite rating formulation; Top 10 Batters & Bowlers generation | Planned |
| **9** | **Statistical Validation** | Bootstrapping, sensitivity checks, ranking stability across seasons | Planned |
| **10** | **Streamlit Dashboard** | Interactive leaderboards, player cards, match state visualizers | Planned |
| **11** | **Methodology Report** | Mathematical derivations, empirical findings, submission documentation | Planned |
| **12** | **Final Audit & Submission** | Verification checklist, final audit, code clean-up, package freeze | Planned |

---

## 7. Current Project Status

- **Phase:** **Phase 0 — Complete**
- **Environment:** Dedicated `.venv` virtual environment configured.
- **Diagnostics:** Configuration system verified, logging active, directory architecture validated, and test suite passing.
