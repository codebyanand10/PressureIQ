# PressureIQ — Phase 6 Pre-Implementation Audit Report
## Batting Performance Under Pressure Engine

**Project:** PressureIQ  
**Phase:** Phase 6 — Batting Performance Under Pressure Engine  
**Author:** Senior Cricket Data Scientist, Sports Statistician, and Python Developer  
**Audit Date:** 2026-11-12  
**Status:** **APPROVED — ALL PRE-CONDITIONS SATISFIED**

---

## 1. Executive Summary

Phase 6 implements the **Batting Performance Under Pressure Engine**, evaluating individual batting performance across granular match-pressure categories and rigorously comparing it against established historical baselines (Overall Baseline, Low-Pressure Baseline, and Contextual Baselines from Phase 5).

This mandatory pre-implementation audit inspects all Phase 1–5 outputs, verifies input dataset integrity, schema consistency, player ID referential fidelity, pressure category boundaries, empirical distributions, and formalizes the mathematical and statistical methodologies for Phase 6.

---

## 2. Input Dataset Audit & Verification

All 7 required upstream datasets have been inspected and confirmed present, valid, and unmodified:

| Dataset | Path | Records | File Size | Integrity Status |
| :--- | :--- | :---: | :---: | :---: |
| **Match State Reconstructed** | `data/processed/match_state_reconstructed.parquet` | 200,999 | 6.75 MB | Verified (Phase 3) |
| **Pressure Scores** | `data/processed/pressure/pressure_scores.parquet` | 200,999 | 9.27 MB | Verified (Phase 4) |
| **Player Registry** | `data/processed/baselines/player_registry.parquet` | 1,217 | 0.08 MB | Verified (Phase 5) |
| **Batting Overall Baseline** | `data/processed/baselines/batting_overall_baseline.parquet` | 888 | 0.09 MB | Verified (Phase 5) |
| **Batting Low-Pressure Baseline** | `data/processed/baselines/batting_low_pressure_baseline.parquet` | 506 | 0.05 MB | Verified (Phase 5) |
| **Batting Contextual Baseline** | `data/processed/baselines/batting_contextual_baseline.parquet` | 6,009 | 0.30 MB | Verified (Phase 5) |
| **Baseline Reliability** | `data/processed/baselines/baseline_reliability.parquet` | 1,535 | 0.03 MB | Verified (Phase 5) |

---

## 3. Verified Scoring & Attribution Axioms

1. **Balls Faced Axiom:**
   - Deliveries where `extras_type == 'wide'` do NOT count as balls faced by the batter.
   - Legal deliveries, no-balls, byes, and leg-byes DO count as balls faced under official cricket scoring rules.
   - Vectorized definition: `is_ball_faced = (extras_type.fillna('') != 'wide').astype(int)`

2. **Runs off Bat:**
   - Batter runs strictly taken from `batter_runs` (fielding extras such as byes/leg-byes/wides are excluded).

3. **Dismissal Attribution:**
   - A dismissal is attributed to the striker if and only if `is_wicket == True` and `dismissed_player_id == striker_id`.
   - Non-striker run outs are excluded from the striker's dismissal count.
   - When dismissals $= 0$, batting average is strictly defined as `None` / `np.nan` (never 0 or fabricated).

4. **Zero Lookahead Leakage:**
   - Pressure classification and match-state evaluation rely strictly on pre-delivery match variables (`batting_pressure_score`), completely isolated from the current delivery outcome.

---

## 4. Empirical Pressure Distribution Audit

Across all 200,999 historical deliveries in the dataset:

| Pressure Category | Score Range | Deliveries | Volume % | Unique Batters |
| :--- | :---: | :---: | :---: | :---: |
| **Very Low** | $[0.0, 19.99]$ | 20,301 | 10.10% | 278 |
| **Low** | $[20.0, 39.99]$ | 101,029 | 50.26% | 504 |
| **Moderate** | $[40.0, 59.99]$ | 55,608 | 27.67% | 654 |
| **High** | $[60.0, 79.99]$ | 19,019 | 9.46% | 624 |
| **Extreme** | $[80.0, 100.0]$ | 5,042 | 2.51% | 428 |
| **Combined High + Extreme** | $[60.0, 100.0]$ | **24,061** | **11.97%** | **667** |

### High-Pressure Sample Distribution among Batters
Among the 667 batters who faced High or Extreme pressure ($\ge 60.0$):
- $\ge 100$ balls faced under high pressure: **57 players**
- $\ge 40$ balls faced under high pressure: **178 players**
- $\ge 15$ balls faced under high pressure: **360 players**
- $< 15$ balls faced under high pressure: **306 players**

---

## 5. Proposed Phase 6 Methodology

### 5.1 Metrics Formulation per Pressure Category
For each player in each of the 5 categories (and combined High+Extreme):
1. **Scoring:** `runs`, `balls_faced`, `strike_rate`, `batting_average`, `fours`, `sixes`, `boundary_runs`, `boundary_percentage`, `dot_balls`, `dot_ball_percentage`, `singles`, `twos`, `threes`, `scoring_delivery_percentage`.
2. **Dismissal:** `dismissals`, `dismissal_rate` (dismissals / balls faced), `balls_per_dismissal`.
3. **Innings-Level Consistency:** Grouped by `(striker_id, match_id, innings)` to evaluate `high_score`, `low_score`, `innings_30_plus`, `innings_50_plus`, and score variability.

### 5.2 Baseline Comparison Formulations
Each batter's high-pressure performance ($\ge 60.0$) is benchmarked against both their **Overall Baseline** and their **Low-Pressure Baseline**:
- **Strike Rate Difference:** $\Delta_{\text{SR}} = \text{SR}_{\text{HP}} - \text{SR}_{\text{base}}$
- **Strike Rate Retention:** $\text{Ret}_{\text{SR}} = \left(\frac{\text{SR}_{\text{HP}}}{\text{SR}_{\text{base}}}\right) \times 100$
- **Average Difference:** $\Delta_{\text{Avg}} = \text{Avg}_{\text{HP}} - \text{Avg}_{\text{base}}$
- **Average Retention:** $\text{Ret}_{\text{Avg}} = \left(\frac{\text{Avg}_{\text{HP}}}{\text{Avg}_{\text{base}}}\right) \times 100$ (with shrinkage handling for low dismissal counts)
- **Boundary % Difference:** $\Delta_{\text{Bnd}} = \text{Bnd\%}_{\text{HP}} - \text{Bnd\%}_{\text{base}}$
- **Dot-Ball % Difference:** $\Delta_{\text{Dot}} = \text{Dot\%}_{\text{HP}} - \text{Dot\%}_{\text{base}}$ (negative is favorable)
- **Dismissal Risk Difference:** $\Delta_{\text{Dism}} = \text{DismRate}_{\text{HP}} - \text{DismRate}_{\text{base}}$ (negative is favorable)

### 5.3 Batting Pressure Performance Index (BPPI)
A normalized 0–100 index measuring performance retention and uplift under high pressure relative to expected baselines:
$$\text{BPPI} = \sum_{j} w_j \cdot S_j$$
Where components $S_j \in [0, 100]$:
1. **Strike Rate Retention ($w_1 = 0.30$):** Scaled retention of scoring efficiency.
2. **Batting Average Retention ($w_2 = 0.25$):** Scaled preservation of wicket value under pressure.
3. **Boundary Efficiency ($w_3 = 0.20$):** High-pressure boundary rate relative to baseline.
4. **Dot-Ball Control ($w_4 = 0.15$):** Suppression of dot balls under pressure.
5. **Dismissal Management ($w_5 = 0.10$):** Survival capability when defending wickets under pressure.

### 5.4 Statistical Reliability & Block Bootstrap
- Because deliveries within a single match and innings are clustered (not independent), confidence intervals are calculated using **match-level block bootstrap resampling** (500 resamples per player).
- **Reliability Tiers:**
  - **High:** $\ge 100$ balls faced under high pressure across $\ge 5$ matches and baseline reliability $\ge$ Medium.
  - **Medium:** $\ge 40$ balls faced across $\ge 3$ matches.
  - **Low:** $\ge 15$ balls faced across $\ge 2$ matches.
  - **Insufficient Data:** $< 15$ balls faced.

### 5.5 Classification Rules
- **Elite Under Pressure:** $\text{BPPI} \ge 75.0$ with Reliability $\in \{\text{High}, \text{Medium}\}$ and $\ge 40$ balls faced.
- **Strong Under Pressure:** $\text{BPPI} \in [60.0, 75.0)$ with Reliability $\in \{\text{High}, \text{Medium}\}$.
- **Average Under Pressure:** $\text{BPPI} \in [45.0, 60.0)$ with Reliability $\ge \text{Low}$.
- **Below Baseline Under Pressure:** $\text{BPPI} < 45.0$ with Reliability $\ge \text{Low}$.
- **Insufficient Evidence:** Reliability == Insufficient Data ($< 15$ high pressure balls).

---

## 6. Audit Conclusion & Phase Gate Sign-Off

The data pipeline, reference baselines, and delivery-level pressure scores are robust and verified. Implementation of Phase 6 may proceed.

