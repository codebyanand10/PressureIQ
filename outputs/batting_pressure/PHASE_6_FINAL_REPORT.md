# PressureIQ — Phase 6 Final Report
## Batting Performance Under Pressure Engine

**Project:** PressureIQ  
**Phase:** Phase 6 — Batting Performance Under Pressure Engine  
**Execution Date:** 2026-11-12 10:33:48  
**Status:** **PHASE 6 COMPLETE — PASSED ALL VALIDATION GATES**

---

## 1. Executive Summary

Phase 6 of PressureIQ has successfully developed, validated, and executed the **Batting Performance Under Pressure Engine**.
The engine quantifies how individual batters perform across granular match pressure categories and benchmarks their high-pressure performance against their historical baselines.

Across **200,999 delivery events** from 2022 onwards:
- **24,061 deliveries** were bowled in High or Extreme pressure situations ($\\ge 60.00$).
- **667 unique batters** faced $\\ge 1$ high-pressure delivery.
- **178 batters** met the robust sample threshold of $\\ge 40$ high-pressure balls faced.
- **57 batters** achieved the highest statistical reliability tier ($\\ge 100$ balls faced across $\\ge 5$ matches).

---

## 2. Pressure Category Breakdown

| Category | Score Range | Deliveries | Volume % | Active Batters | Mean Strike Rate | Mean Boundary % | Mean Dot Ball % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Very Low** | $[0.0, 19.99]$ | 20,301 | 10.10% | 278 | 108.77 | 49.65% | 48.40% |
| **Low** | $[20.0, 39.99]$ | 101,029 | 50.26% | 504 | 119.28 | 53.02% | 40.94% |
| **Moderate** | $[40.0, 59.99]$ | 55,608 | 27.67% | 654 | 116.45 | 44.35% | 38.62% |
| **High** | $[60.0, 79.99]$ | 19,019 | 9.46% | 624 | 113.81 | 42.56% | 40.90% |
| **Extreme** | $[80.0, 100.0]$ | 5,042 | 2.51% | 428 | 116.02 | 41.25% | 44.59% |

---

## 3. High-Pressure Performance Index (BPPI)

The **Batting Pressure Performance Index (BPPI)** evaluates relative performance retention and uplift under pressure on an explainable 0–100 scale:
$$\text{BPPI} = \sum_{j=1}^5 w_j \cdot S_j$$

### 3.1 Component Weights & Formulation
- **Strike Rate Retention ($w_1 = 0.30$):** Measures preservation/acceleration of scoring pace ($100\% \to 50.0$ score, $200\% \to 100.0$).
- **Batting Average Retention ($w_2 = 0.25$):** Evaluates preservation of wicket value under duress using stabilized shrinkage baseline.
- **Boundary Efficiency ($w_3 = 0.20$):** High-pressure boundary rate differential ($+30\% \to 100.0$).
- **Dot-Ball Control ($w_4 = 0.15$):** Suppression of scoreless deliveries (negative differential favorable).
- **Dismissal Management ($w_5 = 0.10$):** Minimization of wicket concession risk.

### 3.2 BPPI Distribution Statistics
- **Total Evaluated Batters:** 667
- **Mean BPPI:** 46.50
- **Median BPPI:** 46.79
- **Standard Deviation:** 13.71
- **25th Percentile:** 40.16
- **75th Percentile:** 52.37

---

## 4. Evidence-Based Batter Classification

| Classification | Count | Cohort % | Definition & Criteria |
| :--- | :---: | :---: | :--- |
| **Elite Under Pressure** | **2** | 0.3% | BPPI $\\ge 75.0$, High/Medium reliability, $\\ge 40$ balls faced |
| **Strong Under Pressure** | **24** | 3.6% | BPPI $\\in [60.0, 75.0)$, High/Medium reliability, $\\ge 40$ balls faced |
| **Average Under Pressure** | **199** | 29.8% | BPPI $\\in [45.0, 60.0)$, baseline parity |
| **Below Baseline Under Pressure** | **121** | 18.1% | BPPI $< 45.0$, measurable degradation relative to baseline |
| **Insufficient Evidence** | **321** | 48.1% | Sample size $< 15$ high-pressure balls faced |

---

## 5. Statistical Reliability & Bootstrap Validation

To account for clustered deliveries within matches and innings, match-level block bootstrap resampling (500 resamples) was executed:
- **High Reliability:** **57 batters** ($\\ge 100$ balls faced, $\\ge 5$ matches)
- **Medium Reliability:** **120 batters** ($\\ge 40$ balls faced, $\\ge 3$ matches)
- **Low Reliability:** **169 batters** ($\\ge 15$ balls faced)
- **Insufficient Data:** **321 batters** ($< 15$ balls faced)

---

## 6. Generated Output Artifacts

### Datasets (`data/processed/batting_pressure/`)
1. `batter_pressure_category_metrics.parquet` (2,488 records)
2. `batter_high_pressure_performance.parquet` (667 records)
3. `batter_baseline_comparison.parquet` (667 records)
4. `batter_situational_performance.parquet` (8,117 records)
5. `batter_pressure_reliability.parquet` (667 records)
6. `batter_pressure_performance_index.parquet` (667 records)
7. `batter_pressure_explanations.parquet` (667 records)

### Reports (`outputs/batting_pressure/`)
1. `batter_pressure_category_summary.csv`
2. `high_pressure_batting_summary.csv`
3. `baseline_comparison_report.csv`
4. `batting_situational_analysis.csv`
5. `batter_reliability_report.csv`
6. `bppi_distribution.csv`
7. `batter_classification_report.csv`
8. `bppi_sensitivity_analysis.csv`
9. `batter_validation_report.csv` (10/10 checks PASSED)

### Diagnostic Visualizations (`outputs/batting_pressure/charts/`)
12 publication-quality distribution, comparison, and contextual charts.

---

## 7. Phase 7 Readiness Assessment

Phase 6 has satisfied all domain, statistical, and software engineering criteria for batting under pressure.
The system is now fully prepared for **Phase 7: Bowling Performance Under Pressure Engine**, which will evaluate bowling economy, dot ball pressure, and wicket taking across bowling pressure conditions.
