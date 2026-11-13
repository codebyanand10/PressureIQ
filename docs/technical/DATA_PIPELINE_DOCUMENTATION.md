# PressureIQ — Data Pipeline & Ingestion Documentation

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Document:** End-to-End Data Pipeline Specification  
**Version:** 1.0.0  

---

## 1. Pipeline Stages

```text
Raw CSV Datasets (data/raw/)
     │
     ▼
Phase 2: Cleaning & Integration (src/preprocessing.py)
     │  • Null imputation, type casting, key deduplication
     │  • Referential integrity linking across teams, matches, and players
     ▼
Cleaned Datasets (data/processed/)
     │
     ▼
Phase 3: Match State Reconstruction (src/match_state/)
     │  • Chronological delivery sequence ordering
     │  • Ball-by-ball pre/post delivery runs, wickets, and remaining balls
     ▼
Match State Dataset (data/processed/match_state_reconstructed.parquet)
     │
     ▼
Phase 4: Pressure Detection Engine (src/pressure/)
     │  • Continuous pressure calculation (0 to 100)
     │  • Pressure tier tagging (Very Low to Extreme)
     ▼
Pressure Scores (data/processed/pressure/pressure_scores.parquet)
     │
     ▼
Phase 5: Baseline Estimation (src/baselines/)
     │  • Career non-pressure benchmarks (2022+)
     │  • Empirical Bayes shrinkage toward cohort priors
     ▼
Baselines (data/processed/baselines/)
     │
     ▼
Phases 6 & 7: Batting & Bowling Engines (src/batting_pressure/, src/bowling_pressure/)
     │  • BPPI & BPPI-B resilience calculation
     │  • Situational slicing (phase, competition, chase)
     ▼
Performance Data (data/processed/batting_pressure/, data/processed/bowling_pressure/)
     │
     ▼
Phase 8: Unified Ranking Engine (src/ranking/)
     │  • 4-pillar composite scoring (FBPR / FBOR)
     │  • Bayesian confidence intervals & eligibility filtering
     ▼
Official Leaderboards (data/processed/rankings/)
     │
     ▼
Phase 9: Statistical Validation (src/validation/)
     │  • Match-level block bootstrap (100 iterations)
     │  • Leave-One-Match-Out (LOMO) jackknife stability
     │  • 12-check data leakage audit
     ▼
Validation Artifacts (data/processed/validation/, outputs/validation/)
```

---

## 2. Ingestion Integrity Rules & Auditing

1. **Immutable Raw Data:** `data/raw/` is treated as strictly read-only.
2. **Deterministic Processing:** Random seeds are fixed (`seed = 42`) across bootstrap and shrinkage sampling.
3. **Columnar Checkpoints:** Large datasets are stored as Snappy-compressed Parquet files for fast I/O.
4. **Data Leakage Guards:** First-innings scoring pressure strictly avoids second-innings required run rates; match results never factor into ball-by-ball execution scores.

