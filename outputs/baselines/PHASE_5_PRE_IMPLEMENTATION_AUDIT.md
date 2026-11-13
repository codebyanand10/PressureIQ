# PressureIQ — Phase 5 Pre-Implementation Audit Report
## Player Baseline Calculation Engine — Pre-Implementation Verification

**Project:** PressureIQ — AI-Powered Cricket Pressure Performance Analytics  
**Phase:** Phase 5 — Player Baseline Calculation Engine  
**Author:** Senior Cricket Data Scientist & Sports Statistician  
**Date:** 2026-11-12  
**Status:** **AUDIT PASSED — READY FOR IMPLEMENTATION**  

---

## 1. Executive Summary

This Pre-Implementation Audit examines the data readiness, referential integrity, and statistical framework required to construct normal historical performance baselines for batters and bowlers in **Phase 5**.

Historical performance baselines provide the foundational reference anchors against which pressure-induced deviations will be measured in subsequent phases (Phases 6–8). The audit confirms that delivery-level records, pressure scores, playing XI registries, and tournament mappings from 2022 to 2026 are structurally intact and mathematically prepared for baseline construction.

---

## 2. Input Datasets & Artifact Verification

| Dataset Path | Format | Record Count | Unique Entities | Verification Status | Analytical Role |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `data/processed/pressure/pressure_scores.parquet` | Parquet | 200,999 | 867 matches | Verified (100% Valid) | Ball-by-ball events, player actions, pressure levels |
| `data/processed/cleaned_matches.csv` | CSV | 883 | 883 matches | Verified SHA256 | Match dates, formats, stages, knockouts |
| `data/processed/cleaned_competitions.csv` | CSV | 141 | 141 comps | Verified SHA256 | Tournament taxonomy (IPL vs T20I vs Domestic) |
| `data/processed/cleaned_teams.csv` | CSV | 353 | 38 teams | Verified SHA256 | Franchise and national team metadata |
| `data/processed/cleaned_playing_eleven.csv` | CSV | 28,341 | 1,082 players | Verified (Deduplicated) | Official match appearances, batting orders, impact roles |
| `data/processed/cleaned_competition_team_player_mapping.csv` | CSV | 6,413 | 1,217 players | Verified SHA256 | Master player registration catalog |

---

## 3. Player Universe & Participation Audit

| Player Cohort | Count | Analytical Treatment |
| :--- | :---: | :--- |
| **Master Registered Players** (`cleaned_competition_team_player_mapping.csv`) | **1,217** | Base registry universe across all squads |
| **Named in Playing XI** (`cleaned_playing_eleven.csv`) | **1,082** | Selected in at least one match lineup |
| **Active Strikers** (faced $\ge 1$ ball in ball-by-ball) | **888** | Eligible for batting baseline evaluation |
| **Active Bowlers** (bowled $\ge 1$ ball in ball-by-ball) | **647** | Eligible for bowling baseline evaluation |
| **Total Active On-Field Participants** (Batted or Bowled) | **958** | Primary baseline evaluation population |
| **Bench / Non-participating Registered Reserves** | **259** | Maintained in registry with zero on-field volume |

*Domain Rule Enforced:* A player is never credited with a batting innings or bowling appearance solely because they appeared on the team sheet. Baseline calculations require verified on-field events.

---

## 4. Verified Scoring & Attribution Semantics

### 4.1 Batting Metrics
- **Batter Runs:** Credited strictly from `batter_runs` (runs off the bat). Byes, leg-byes, and penalty extras are completely excluded.
- **Balls Faced:** A ball is counted as a ball faced iff `extras_type != 'wide'`. No-balls (`Overstep`, `other`), byes, leg-byes, and legal deliveries all increment balls faced.
- **Batting Average:** $\frac{\text{Total Batter Runs}}{\text{Dismissals}}$. Players with zero dismissals are preserved with raw average as $\text{NaN}$ and flagged with `ZERO_DISMISSALS`.
- **Strike Rate:** $\frac{\text{Total Batter Runs}}{\text{Balls Faced}} \times 100.0$.
- **Boundary Percentages:** Fours (`is_four == True`) and Sixes (`is_six == True`) aggregated separately and combined into `boundary_runs`.

### 4.2 Bowling Metrics
- **Bowler Conceded Runs:** $\text{batter\_runs} + \text{wides} + \text{no-balls}$. Byes and leg-byes are fielding extras and are strictly charged to the team, NOT the bowler.
- **Bowler Credited Wickets:** Bowler is credited strictly for dismissals where `dismissal_type` $\in$ `['Bowled', 'Caught', 'LBW', 'Stumped', 'Hit Wicket']`. Run Outs, Retired Out, and Obstructing the field are non-bowler wickets and are omitted from bowler tally.
- **Legal Balls Bowled:** Credited strictly when `is_legal_delivery == True` (illegal deliveries: `wide`, `Overstep`, `other` are excluded).
- **Economy Rate:** $\frac{\text{Runs Conceded} \times 6.0}{\text{Legal Balls Bowled}}$.
- **Bowling Average & Strike Rate:** $\frac{\text{Runs Conceded}}{\text{Wickets Credited}}$ and $\frac{\text{Legal Balls Bowled}}{\text{Wickets Credited}}$.

---

## 5. Low-Pressure Baseline Definition

- **Separation of Baselines:** The engine generates two distinct reference baselines:
  1. `overall_baseline`: All eligible deliveries (200,999 events).
  2. `low_pressure_baseline`: Deliveries occurring under low-pressure match states ($\text{pressure\_score} < 40.0$).
- **Empirical Volume Availability:**
  - Batting low-pressure deliveries ($< 40.0$): **121,330 deliveries** (60.36% of all balls).
  - Bowling low-pressure deliveries ($< 40.0$): **70,405 deliveries** (35.03% of all balls).
- Both reference sets are strictly kept separate. Under-pressure performance differences are explicitly deferred to Phase 6 and Phase 7.

---

## 6. Small-Sample Shrinkage & Statistical Reliability

- **Shrinkage Methodology:** Empirical Bayes / James-Stein shrinkage towards competition-specific role baselines:
  $$\hat{\theta}_i = w_i \cdot X_i + (1 - w_i) \cdot \mu_{\text{reference}}$$
  where $w_i = \frac{N_i}{N_i + K}$, with $K$ calibrated to metric variance (e.g., $K=60$ for strike rate, $K=120$ for bowling economy).
- **Metric-Specific Reliability Standards:**
  - Batting: High ($\ge 150$ balls faced, $\ge 5$ dismissals), Medium ($60–149$ balls), Low ($20–59$ balls), Insufficient ($< 20$ balls).
  - Bowling: High ($\ge 120$ legal balls, $\ge 5$ wickets), Medium ($48–119$ balls), Low ($18–47$ balls), Insufficient ($< 18$ balls).

---

## 7. Audit Conclusion & Approval

All prerequisite data assets, scoring definitions, and mathematical structures are validated and complete.

Proceed to configuration extension in `config/settings.yaml`, building the `src/baselines/` module suite, and constructing the comprehensive test harness.

