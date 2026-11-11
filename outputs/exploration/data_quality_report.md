# PressureIQ — Data Quality & Anomaly Diagnostic Report

**Project:** PressureIQ  
**Phase:** Phase 1 (Data Quality Assessment)  
**Competition:** SupeRR Selector Season 2 — Round 1  
**Generated:** 2026-11-11 22:28:10  

---

## 1. Executive Summary of Data Anomalies

During Phase 1 exploration of the 6 raw competition CSV files, several critical data quality anomalies, structural edge cases, and schema subtleties were discovered. None of these prevent successful modeling, but all require explicit handling in Phase 2 (Cleaning & Integration) and Phase 3 (Match State Reconstruction).

---

## 2. Key Violations & Duplicate Records

### A. Playing XI Composite Key Violations (`playing_eleven.csv`)
- **Key Defined:** `(match_id, team_id, player_id)`
- **Finding:** **40 duplicate key instances** representing **75 total rows** in `playing_eleven.csv`.
- **Observed Behavior:** In match `13613` and others, the same player appears twice under the same team with different `batting_order` assignments (e.g. Player 223 with batting order 5.0 and 6.0; Player 250 with batting order 2.0 and 4.0).
- **Phase 2 Remediation:** Deduplicate player records by retaining the official playing order or corroborating with delivery appearance in `ball_by_ball.csv`.

---

## 3. Referential Integrity Anomalies

### A. Match Count Differences Across Files
- `matches.csv`: 883 matches
- `ball_by_ball.csv`: 867 matches (16 matches missing)
- `playing_eleven.csv`: 880 matches (3 matches missing)
- **Root Cause Confirmed:**
  - All 16 missing matches in `ball_by_ball.csv` have `result == 'Match Abandoned'`. No ball was ever bowled.
  - The 3 matches missing in `playing_eleven.csv` (`36210`, `41503`, `48513`) were abandoned before lineups/toss were logged.
- **Referential Verdict:** Zero orphan deliveries exist. Integrity is 100% intact among matches with completed play.

### B. Players in Deliveries Absent from Lineups
- Two player IDs (`36153` and `39444`) appear in `ball_by_ball.csv` (matches 37087, 37092, 37095 in Mens Emerging Asia Cup) but are absent from `playing_eleven.csv`.
- In `competition_team_player_mapping.csv`, `36153` corresponds to **Syed Haider** and `39444` to **Basil Hameed**.
- **Root Cause:** Concussion substitutes or unrecorded match squad changes in regional tournament scoring.

---

## 4. Cricket Semantics & Column Subtleties

### A. DLS Revised Overs Unit Mislabeling
- In `matches.csv`, columns `first_inn_revised_overs` and `second_inn_revised_overs` store values such as `114.0`, `90.0`, `48.0`, `42.0`.
- **Finding:** These are **LEGAL BALLS**, not overs (114 balls = 19 overs, 90 balls = 15 overs, 48 balls = 8 overs).
- **Phase 3 Remediation:** Divide by 6.0 before calculating required run rates.

### B. Bowl Speed Missingness
- `bowl_speed` in `ball_by_ball.csv` has zero nulls, but **77,861 deliveries (38.74%) have `bowl_speed == 0`**.
- Speed radar was not active or installed across all venues. 0 must be treated as `NaN` rather than 0 km/h.

### C. Dismissal Type Typo
- `Obstracting the field` (2 rows) vs `Obstructing the field` (1 row).
- Must be normalized to standard string in Phase 2.

### D. Bench Reserves in Playing Eleven
- `playing_eleven.csv` contains entire registered squads (11 to 27 players per match).
- Active match participants must be filtered using `is_played == True` (19,714 records), as `is_played == False` denotes bench reserves.
