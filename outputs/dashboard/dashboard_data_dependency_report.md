# PressureIQ — Dashboard Data Dependency Report

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Phase:** Phase 10 — Interactive Analytics Dashboard  
**Status:** Audit Completed — All 32 Required Upstream Data Files Verified

---

## 1. Upstream Dataset Audit & Mapping

Every page of the PressureIQ dashboard depends strictly on precomputed, mathematically validated outputs from Phases 1 through 9. No raw datasets are accessed directly, and no rankings or statistics are fabricated.

| Phase | Source Dataset Path | Format | Record Count | Dashboard Target Page | Purpose / Metrics Extracted |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **Ph 8** | `data/processed/rankings/batter_ratings.parquet` | Parquet | 170 | Overview, Batter Rankings, Player Analysis, Player Comparison | Final FBPR ratings, rankings (#1–#170), 95% CIs, strike rate, boundaries, dot %, reliability levels |
| **Ph 8** | `data/processed/rankings/bowler_ratings.parquet` | Parquet | 232 | Overview, Bowler Rankings, Player Analysis, Player Comparison | Final FBOR ratings, rankings (#1–#232), 95% CIs, economy, wickets, dot %, bowling roles, pace/spin |
| **Ph 8** | `data/processed/rankings/ranking_components.parquet` | Parquet | 402 | Player Analysis, Player Comparison | Normalized 4-component score breakdown (Absolute, Resilience, Consistency, Context) |
| **Ph 8** | `data/processed/rankings/ranking_explanations.parquet` | Parquet | 402 | Player Analysis | Algorithmic explanation narratives, key strengths, baseline comparisons, limitations |
| **Ph 8** | `data/processed/rankings/batting_eligibility.parquet` | Parquet | 545 | Batter Rankings, Methodology | Total evaluated batters, exclusion criteria breakdown, minimum balls filters |
| **Ph 8** | `data/processed/rankings/bowling_eligibility.parquet` | Parquet | 486 | Bowler Rankings, Methodology | Total evaluated bowlers, exclusion criteria breakdown, minimum overs filters |
| **Ph 5** | `data/processed/baselines/batting_overall_baseline.parquet` | Parquet | 545 | Player Analysis, Comparison | Historical baseline strike rates, batting averages, boundary %, dot % |
| **Ph 5** | `data/processed/baselines/bowling_overall_baseline.parquet` | Parquet | 486 | Player Analysis, Comparison | Historical baseline economy rates, bowling averages, strike rates, dot % |
| **Ph 6** | `data/processed/batting_pressure/batter_pressure_category_metrics.parquet` | Parquet | 1,480 | Player Analysis, Pressure Analysis | Batting metrics sliced across 5 validated pressure tiers (Very Low to Extreme) |
| **Ph 7** | `data/processed/bowling_pressure/bowler_pressure_category_metrics.parquet` | Parquet | 1,324 | Player Analysis, Pressure Analysis | Bowling metrics sliced across 5 validated pressure tiers (Very Low to Extreme) |
| **Ph 6** | `data/processed/batting_pressure/batter_situational_performance.parquet` | Parquet | 3,120 | Player Analysis, Pressure Analysis | Innings phase (Powerplay, Middle, Death) & chase vs 1st innings batting performance |
| **Ph 7** | `data/processed/bowling_pressure/bowler_situational_performance.parquet` | Parquet | 2,890 | Player Analysis, Pressure Analysis | Innings phase & bowling role situational performance |
| **Ph 4** | `data/processed/pressure/pressure_scores.parquet` | Parquet | 200,999 | Overview, Pressure Analysis | Overall high-pressure delivery counts (47,440), pressure distribution, situation factors |
| **Ph 2** | `data/processed/match_metadata.parquet` | Parquet | 988 | Overview, Data Quality | Total matches, competition coverage (IPL & T20I), dates (2022 onwards) |
| **Ph 9** | `data/processed/validation/robustness_scorecard.parquet` | Parquet | 10 | Statistical Validation | Official 10-dimension robustness scorecard (All 10 Dimensions PASSED) |
| **Ph 9** | `data/processed/validation/batting_bootstrap_results.parquet` | Parquet | 170 | Statistical Validation, Player Analysis | 100-sample match block bootstrap distributions, 90%/95% CIs, median/best/worst ranks |
| **Ph 9** | `data/processed/validation/bowling_bootstrap_results.parquet` | Parquet | 232 | Statistical Validation, Player Analysis | 100-sample match block bootstrap distributions, 90%/95% CIs, median/best/worst ranks |
| **Ph 9** | `data/processed/validation/batting_rank_stability.parquet` | Parquet | 170 | Statistical Validation | LOMO max rank drops, rank variance, stability classifications |
| **Ph 9** | `data/processed/validation/bowling_rank_stability.parquet` | Parquet | 232 | Statistical Validation | LOMO max rank drops, rank variance, stability classifications |
| **Ph 9** | `data/processed/validation/leakage_audit.parquet` | Parquet | 12 | Statistical Validation, Overview | 12-check data leakage audit outcomes (0 Critical Failures) |
| **Ph 9** | `data/processed/validation/batting_sensitivity_results.parquet` | Parquet | 1,190 | Statistical Validation | 6 alternative weighting profiles across candidates |
| **Ph 9** | `data/processed/validation/competition_fairness.parquet` | Parquet | 2 | Statistical Validation | IPL vs T20I representation and exposure balance |
| **Ph 9** | `data/processed/validation/batting_role_fairness.parquet` | Parquet | 3 | Statistical Validation | Role fairness: Top Order, Middle Order, Finishers |
| **Ph 9** | `data/processed/validation/bowling_role_fairness.parquet` | Parquet | 4 | Statistical Validation | Role fairness: Powerplay, Middle, Death, Pace vs Spin |
| **Ph 9** | `data/processed/validation/sample_size_validation.parquet` | Parquet | 402 | Statistical Validation | Empirical Bayes shrinkage validation, volume vs rating correlation |

---

## 2. Validation Gate Assessment

Under Section 1 of the Phase 10 specification:
- **Batting Robustness:** `PASS` (10/10 dimensions satisfied)
- **Bowling Robustness:** `PASS` (10/10 dimensions satisfied)
- **Data Leakage Status:** `PASS` (12/12 checks passed, 0 critical leaks)
- **Critical Validation Warnings:** **0** (No ranking requires disclaimer downgrading; all official rankings are fully validated).

