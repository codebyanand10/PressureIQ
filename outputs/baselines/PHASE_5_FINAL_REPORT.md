# PressureIQ — Phase 5 Final Report
## Player Baseline Calculation Engine & Normal Performance Anchors

**Project:** PressureIQ  
**Phase:** Phase 5 — Player Baseline Calculation Engine  
**Execution Date:** 2026-11-12 10:08:08  
**Status:** **PHASE 5 COMPLETE — PASSED ALL VALIDATION GATES**  

---

## 1. Executive Summary

Phase 5 of PressureIQ has successfully developed, validated, and executed the **Player Baseline Calculation Engine**.
The engine establishes statistically rigorous, unshrinkable, and shrinkage-adjusted historical reference baselines for all active players across **200,999 delivery events** from **867 historical IPL and T20 International matches** (2022–2026).

Two strictly decoupled baseline datasets have been generated:
1. **Overall Performance Baseline:** Reflects general historical performance across all match situations.
2. **Low-Pressure Performance Baseline:** Isolates performance strictly under low-pressure conditions (Phase 4 pressure score $\le 39.99$), establishing the definitive reference point for measuring subsequent pressure degradation or enhancement.

---

## 2. Player Universe & Participation Summary

| Analytical Population | Count | Description |
| :--- | :---: | :--- |
| **Total Registered Players in Mapping** | **1,217** | Complete player catalog across all squads |
| **Players Named in Playing XI** | **1,082** | Selected in official team sheets |
| **Eligible Batting Baseline Cohort** | **888** | Players who faced $\ge 1$ ball on field |
| **Eligible Bowling Baseline Cohort** | **647** | Players who bowled $\ge 1$ delivery on field |
| **Low-Pressure Batters Cohort** | **506** | Batters with $\ge 1$ delivery under low pressure |
| **Low-Pressure Bowlers Cohort** | **526** | Bowlers with $\ge 1$ delivery under low pressure |

---

## 3. Empirical Baseline Distributions

### 3.1 Batting Baselines (Overall vs Low-Pressure)

| Metric | Overall Batting Baseline | Low-Pressure Batting Baseline |
| :--- | :---: | :---: |
| **Active Batters** | 888 | 506 |
| **Mean Strike Rate** | 110.98 | 117.97 |
| **Median Strike Rate** | 116.67 | 121.70 |
| **Mean Batting Average** | 17.58 | 23.25 |
| **Median Batting Average** | 16.00 | 22.21 |
| **Mean Boundary %** | 48.34% | 53.14% |
| **Mean Dot Ball %** | 42.53% | 41.57% |

### 3.2 Bowling Baselines (Overall vs Low-Pressure)

| Metric | Overall Bowling Baseline | Low-Pressure Bowling Baseline |
| :--- | :---: | :---: |
| **Active Bowlers** | 647 | 526 |
| **Mean Economy Rate** | 9.23 | 8.80 |
| **Median Economy Rate** | 8.97 | 8.65 |
| **Mean Bowling Average** | 32.18 | 25.68 |
| **Median Bowling Average** | 27.91 | 22.50 |
| **Mean Dot Ball % Conceded** | 33.42% | 34.16% |
| **Mean Boundary % Conceded** | 20.04% | 18.23% |

---

## 4. Statistical Shrinkage Methodology

To handle small-sample volatility, Empirical Bayes shrinkage was applied:
$$\hat{\theta}_i = w_i \cdot X_i + (1 - w_i) \cdot \mu_{\text{ref}}$$
where $w_i = \frac{N_i}{N_i + K}$:
- **Batting Strike Rate:** $K = 60.0$, $\mu_{\text{ref}} = 125.0$
- **Batting Average:** $K = 5.0$, $\mu_{\text{ref}} = 22.0$
- **Bowling Economy:** $K = 120.0$, $\mu_{\text{ref}} = 8.20$
- **Bowling Average:** $K = 5.0$, $\mu_{\text{ref}} = 24.0$

Raw metrics are preserved unadjusted alongside shrunk values in all baseline datasets.

---

## 5. Baseline Reliability Breakdown

| Role | High Reliability | Medium Reliability | Low Reliability | Insufficient Data |
| :--- | :---: | :---: | :---: | :---: |
| **Batters** | 248 | 167 | 228 | 245 |
| **Bowlers** | 292 | 167 | 120 | 68 |

---

## 6. Generated Output Artifacts

### Datasets (`data/processed/baselines/`)
1. `player_registry.parquet` (1,217 records)
2. `batting_overall_baseline.parquet` (888 records)
3. `batting_low_pressure_baseline.parquet` (506 records)
4. `bowling_overall_baseline.parquet` (647 records)
5. `bowling_low_pressure_baseline.parquet` (526 records)
6. `batting_contextual_baseline.parquet` (6,009 records)
7. `bowling_contextual_baseline.parquet` (3,683 records)
8. `baseline_reliability.parquet` (1,535 records)
9. `baseline_metadata.parquet` (8 records)

### Reports (`outputs/baselines/`)
1. `player_baseline_summary.csv`
2. `batting_baseline_summary.csv`
3. `bowling_baseline_summary.csv`
4. `contextual_baseline_summary.csv`
5. `baseline_reliability_report.csv`
6. `baseline_shrinkage_report.csv`
7. `competition_normalization_report.csv`
8. `baseline_validation_report.csv`

### Diagnostic Visualizations (`outputs/baselines/charts/`)
12 publication-quality distribution, comparison, and contextual charts.

---

## 7. Phase 6 Readiness Assessment

Phase 5 has met all mathematical, data engineering, and cricket domain requirements. 
The system is now fully prepared for **Phase 6: Batting Pressure Performance Engine**, which will evaluate how individual batters perform specifically in high-pressure delivery states compared against these established baselines.
