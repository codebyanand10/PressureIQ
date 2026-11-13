# PressureIQ — Phase 7 Pre-Implementation Audit Report
## Bowling Performance Under Pressure Engine

**Project:** PressureIQ  
**Phase:** Phase 7 — Bowling Performance Under Pressure Engine  
**Author:** Senior Cricket Data Scientist, Sports Statistician, and Python Developer  
**Audit Date:** 2026-11-12  
**Status:** **APPROVED — ALL PRE-CONDITIONS SATISFIED**

---

## 1. Executive Summary

Phase 7 implements the **Bowling Performance Under Pressure Engine**, evaluating individual bowling performance across granular match-pressure categories and rigorously comparing it against established historical bowling baselines (Overall Baseline, Low-Pressure Baseline, and Contextual Baselines from Phase 5).

This mandatory pre-implementation audit inspects all Phase 1–6 outputs, verifies input dataset integrity, schema consistency, bowler ID referential fidelity, pressure category boundaries, empirical distributions, and formalizes the mathematical, statistical, and domain methodologies for Phase 7.

---

## 2. Input Dataset Audit & Verification

All 8 required upstream datasets have been inspected and confirmed present, valid, and unmodified:

| Dataset | Path | Records | File Size | Integrity Status |
| :--- | :--- | :---: | :---: | :---: |
| **Match State Reconstructed** | `data/processed/match_state_reconstructed.parquet` | 200,999 | 6.75 MB | Verified (Phase 3) |
| **Pressure Scores** | `data/processed/pressure/pressure_scores.parquet` | 200,999 | 9.27 MB | Verified (Phase 4) |
| **Player Registry** | `data/processed/baselines/player_registry.parquet` | 1,217 | 0.08 MB | Verified (Phase 5) |
| **Bowling Overall Baseline** | `data/processed/baselines/bowling_overall_baseline.parquet` | 647 | 0.06 MB | Verified (Phase 5) |
| **Bowling Low-Pressure Baseline** | `data/processed/baselines/bowling_low_pressure_baseline.parquet` | 526 | 0.05 MB | Verified (Phase 5) |
| **Bowling Contextual Baseline** | `data/processed/baselines/bowling_contextual_baseline.parquet` | 3,683 | 0.18 MB | Verified (Phase 5) |
| **Baseline Reliability** | `data/processed/baselines/baseline_reliability.parquet` | 1,535 | 0.03 MB | Verified (Phase 5) |
| **Batter Pressure Performance Index** | `data/processed/batting_pressure/batter_pressure_performance_index.parquet` | 667 | 0.20 MB | Verified (Phase 6) |

---

## 3. Verified Bowling Scoring & Attribution Axioms

1. **Bowler-Conceded Runs Axiom:**
   - Runs off bat (`batter_runs`) are charged to the bowler.
   - Bowler extras (`wides`, `overstep`, other no-balls) are charged to the bowler.
   - Field extras (`byes`, `leg-byes`) are strictly **EXCLUDED** from bowler-conceded runs.
   - Vectorized formula: `bowler_runs = batter_runs + (extras_runs if extras_type in ['wide', 'Overstep', 'other'] else 0)`.

2. **Bowler-Credited Wickets Axiom:**
   - Only wickets credited to the bowler (`Bowled`, `Caught`, `LBW`, `Stumped`, `Hit Wicket`) count towards the bowler's wicket tally.
   - Non-bowler dismissals (`Run Out`, `Retired Out`, `Obstructing the Field`) are strictly **EXCLUDED**.

3. **Legal Deliveries & Overs:**
   - `legal_balls_bowled = count(is_legal_delivery == True)`.
   - `overs_bowled = legal_balls_bowled / 6.0`.
   - Wides and no-balls do not increment legal balls.

4. **Rate Metrics & Undefined Values:**
   - `economy_rate = (runs_conceded * 6.0) / legal_balls_bowled` (Null if legal balls $== 0$).
   - `bowling_average = runs_conceded / wickets_credited` (Null if wickets $== 0$, never zero).
   - `bowling_strike_rate = legal_balls_bowled / wickets_credited` (Null if wickets $== 0$).
   - `dot_ball_percentage = (dot_balls / legal_balls_bowled) * 100.0`.

---

## 4. Empirical Bowling Pressure Distribution Audit

Across all 200,999 historical deliveries in the dataset:

| Pressure Category | Score Range | Deliveries | Volume % | Unique Bowlers |
| :--- | :---: | :---: | :---: | :---: |
| **Very Low** | $[0.0, 19.99]$ | 11,166 | 5.56% | 313 |
| **Low** | $[20.0, 39.99]$ | 59,239 | 29.47% | 522 |
| **Moderate** | $[40.0, 59.99]$ | 80,691 | 40.14% | 595 |
| **High** | $[60.0, 79.99]$ | 47,015 | 23.39% | 557 |
| **Extreme** | $[80.0, 100.0]$ | 2,888 | 1.44% | 267 |
| **Combined High + Extreme** | $[60.0, 100.0]$ | **49,903** | **24.83%** | **559** |

### High-Pressure Sample Distribution among Bowlers
Among the 559 bowlers who bowled under High or Extreme pressure ($\ge 60.0$):
- $\ge 120$ legal balls (20+ overs under high pressure): **127 bowlers** (High Reliability candidates)
- $\ge 48$ legal balls (8+ overs under high pressure): **237 bowlers** (Medium Reliability candidates)
- $\ge 18$ legal balls (3+ overs under high pressure): **390 bowlers** (Low Reliability candidates)
- $< 18$ legal balls: **169 bowlers** (Insufficient Data)

---

## 5. Proposed Phase 7 Methodology

### 5.1 Bowling Metrics per Pressure Category
For each bowler in each of the 5 categories (and combined High+Extreme):
1. **Basic:** `matches_bowled`, `innings_bowled`, `legal_balls_bowled`, `overs_bowled`, `runs_conceded`, `wickets_credited`, `economy_rate`, `bowling_average`, `bowling_strike_rate`.
2. **Run Control:** `dot_balls`, `dot_ball_percentage`, `fours_conceded`, `sixes_conceded`, `boundaries_conceded`, `boundary_percentage_conceded`, `scoring_delivery_percentage`.
3. **Wicket Taking:** `wickets_per_legal_ball`, `wickets_per_over`.
4. **Consistency:** Spell-level and innings-level variability in runs conceded per over.

### 5.2 Baseline Comparison Differentials
High-pressure bowling performance ($\ge 60.0$) is benchmarked against both **Overall Baseline** and **Low-Pressure Baseline**:
- **Economy Difference:** $\Delta_{\text{Econ}} = \text{Econ}_{\text{HP}} - \text{Econ}_{\text{base}}$ (negative is favorable).
- **Economy Retention:** $\text{Ret}_{\text{Econ}} = \left(\frac{\text{Econ}_{\text{base}}}{\text{Econ}_{\text{HP}}}\right) \times 100$ (higher is favorable).
- **Bowling Average Difference:** $\Delta_{\text{Avg}} = \text{Avg}_{\text{HP}} - \text{Avg}_{\text{base}}$ (negative is favorable).
- **Bowling Strike Rate Difference:** $\Delta_{\text{SR}} = \text{SR}_{\text{HP}} - \text{SR}_{\text{base}}$ (negative is favorable).
- **Dot-Ball % Difference:** $\Delta_{\text{Dot}} = \text{Dot\%}_{\text{HP}} - \text{Dot\%}_{\text{base}}$ (positive is favorable).
- **Boundary Prevention Difference:** $\Delta_{\text{Bnd}} = \text{Bnd\%}_{\text{HP}} - \text{Bnd\%}_{\text{base}}$ (negative is favorable).
- **Wicket-Taking Rate Difference:** $\Delta_{\text{WktRate}} = \text{WktRate}_{\text{HP}} - \text{WktRate}_{\text{base}}$ (positive is favorable).

### 5.3 Bowling Pressure Performance Index (BPPI-B)
A normalized 0–100 index measuring bowling effectiveness under high pressure relative to baseline expectations:
$$\text{BPPI-B} = \sum_{j=1}^5 w_j \cdot S_j$$
Where components $S_j \in [0, 100]$:
1. **Economy Rate Retention ($w_1 = 0.30$):** Run restriction relative to baseline economy.
2. **Wicket-Taking Effectiveness ($w_2 = 0.25$):** Strike rate / wicket rate uplift in pressure situations.
3. **Dot-Ball Generation ($w_3 = 0.20$):** Ability to produce scoreless balls under duress.
4. **Boundary Prevention ($w_4 = 0.15$):** Concession rate suppression of fours and sixes.
5. **Bowling Average Retention ($w_5 = 0.10$):** Run cost per wicket relative to shrunk baseline average.

### 5.4 Bowling Role Classification
Using verified historical usage and metadata:
- **Powerplay Specialist:** $\ge 40\%$ of pressure overs bowled in the Powerplay (overs 1–6).
- **Middle-Overs Specialist:** $\ge 40\%$ of pressure overs bowled in Middle overs (overs 7–15).
- **Death-Overs Specialist:** $\ge 40\%$ of pressure overs bowled in Death overs (overs 16–20).
- **Multi-Phase Bowler:** Substantial volume across multiple phases without exceeding 40% in a single phase.
- **Pace vs Spin:** Verified bowling style metadata mapped directly from delivery radar/type records.

### 5.5 Statistical Reliability & Bootstrap Validation
- Deliveries bowled by a player in the same match/spell are correlated.
- **Match-level block bootstrap resampling (500 resamples)** is executed to generate $95\%$ confidence intervals for economy rate and BPPI-B.
- Reliability tiers:
  - **High:** $\ge 120$ legal balls (20+ overs), $\ge 5$ matches, baseline reliability $\ge$ Medium.
  - **Medium:** $\ge 48$ legal balls (8+ overs), $\ge 3$ matches.
  - **Low:** $\ge 18$ legal balls (3+ overs), $\ge 2$ matches.
  - **Insufficient Data:** $< 18$ legal balls.

### 5.6 Bowler Classification Tiers
- **Elite Under Pressure:** $\text{BPPI-B} \ge 75.0$, High/Medium reliability, $\ge 48$ legal balls.
- **Strong Under Pressure:** $\text{BPPI-B} \in [60.0, 75.0)$, High/Medium reliability, $\ge 48$ legal balls.
- **Average Under Pressure:** $\text{BPPI-B} \in [45.0, 60.0)$, baseline parity.
- **Below Baseline Under Pressure:** $\text{BPPI-B} < 45.0$, measurable performance decline.
- **Insufficient Evidence:** Reliability == Insufficient Data ($< 18$ legal balls).

---

## 6. Audit Conclusion & Phase Gate Sign-Off

All datasets, baselines, and scoring rules for bowling under pressure are fully audited, verified, and ready. Implementation of Phase 7 may proceed.

