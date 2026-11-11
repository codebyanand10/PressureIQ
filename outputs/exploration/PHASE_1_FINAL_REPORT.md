# PressureIQ — Phase 1 Final Exploration Report
## Dataset Exploration, Schema Discovery & Data Quality Assessment

**Project:** PressureIQ  
**Title:** AI-Powered Cricket Pressure Performance Analytics and Player Ranking System  
**Competition:** SupeRR Selector Season 2 — Round 1  
**Author:** PressureIQ Data Engineering Team  
**Date of Execution:** 2026-11-11 22:28:10  
**Status:** **PHASE 1 COMPLETE**  

---

## 1. Executive Summary

Phase 1 conducted a comprehensive, evidence-based exploration and diagnostic audit of all six competition datasets provided for SupeRR Selector Season 2. Covering **883 matches**, **200,999 delivery events**, **1,217 players**, and **38 teams** spanning **2022 to 2026**, this phase establishes the definitive foundation for dynamic pressure index modeling and player ranking.

No data was modified, cleaned, or transformed during this phase. Every observation is grounded in reproducible empirical checks.

---

## 2. Dataset Inventory Summary

| Dataset File | File Size (MB) | Rows | Columns | Duplicate Rows | Missing Values (%) | Primary / Composite Key |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `competitions.csv` | 0.007 | 141 | 4 | 0 | 0.00% | `comp_id` |
| `teams.csv` | 0.007 | 353 | 3 | 0 | 0.00% | `comp_id + team_id` |
| `competition_team_player_mapping.csv` | 0.442 | 6,413 | 6 | 0 | 0.00% | `comp_id + team_id + player_id` |
| `matches.csv` | 0.118 | 883 | 22 | 0 | 13.56% | `match_id` |
| `playing_eleven.csv` | 0.922 | 28,381 | 9 | 0 | 13.60% | `match_id + team_id + player_id`* |
| `ball_by_ball.csv` | 39.169 | 200,999 | 33 | 0 | 6.07% | `match_id + innings + innings_ball_num` |

(*Note: 40 duplicate composite key instances detected in playing_eleven.csv)

---

## 3. Primary & Composite Key Validation

1. **`competitions.csv` (`comp_id`):** 100% unique, zero nulls. Valid primary key.
2. **`teams.csv` (`comp_id + team_id`):** 100% unique, zero nulls. Valid composite key.
3. **`competition_team_player_mapping.csv` (`comp_id + team_id + player_id`):** 100% unique, zero nulls. Valid composite key.
4. **`matches.csv` (`match_id`):** 100% unique, zero nulls. Valid primary key.
5. **`playing_eleven.csv` (`match_id + team_id + player_id`):** **40 duplicate key pairs (75 rows)**. Players recorded with differing batting orders in single matches. Violation logged for Phase 2 deduplication.
6. **`ball_by_ball.csv` (`match_id + innings + innings_ball_num`):** 100% unique, zero nulls across 200,999 rows. Valid composite key.

---

## 4. Match Coverage Analysis

- **`matches.csv`:** 883 unique matches.
- **`ball_by_ball.csv`:** 867 unique matches.
- **`playing_eleven.csv`:** 880 unique matches.
- **Common across all 3:** 867 matches.
- **Explanation:** Exactly 16 matches in `matches.csv` have zero ball-by-ball deliveries. All 16 were officially **Abandoned** due to weather without a ball bowled. 3 of these were abandoned prior to team lineup submission. Zero orphan records exist.

---

## 5. Competition & Seasonal Breakdown

- **Formats:** 134 T20I competitions (bilateral series & multi-nation tournaments), 7 domestic/regional T20 leagues.
- **Indian Premier League (IPL):** 5 full editions included (`comp_id`: 1358 [IPL 2022], 1715 [IPL 2023], 2193 [IPL 2024], 2725 [IPL 2025], 3298 [IPL 2026]).
- **Other T20 Leagues:** Mens Emerging Asia Cup 2024 (`comp_id 2670`) and Asia Cup Rising Stars 2025 (`comp_id 3289`).
- **Knockout Matches:** 31 playoff / knockout / final fixtures clearly tagged via `knock_out == 1`.

---

## 6. Cricket Delivery Mechanics & Scoring Semantics

1. **Batter Runs vs Extras:**
   - `runs` records **exclusively runs scored off the bat**.
   - On all 7,714 wides, `runs == 0`, and the wide penalty/extra is captured in `extras1_runs`.
   - On no-balls (`Overstep`), `runs` captures runs struck off the bat, `extras1_runs == 1` records the penalty, and `extras_2_runs` captures any additional byes/overthrows.
   - **Total delivery team runs:** `runs + extras1_runs + extras_2_runs`.
2. **Delivery Progression:**
   - `overid`: 1 to 20 (1-indexed).
   - `over_ball_num`: Increments sequentially on **all** deliveries (reaching up to 13 in heavily penalized overs).
   - `innings_ball_num`: Increments sequentially across the innings.
   - **Legal delivery criterion:** A delivery is legal if `extras_type` is NOT in `['wide', 'Overstep']`.
3. **Dismissals:**
   - 10,881 total wickets.
   - **Bowler-credited wickets:** 10,272 (94.4%) — Caught (7,557), Bowled (1,775), LBW (709), Stumped (214), Hit Wicket (17).
   - **Non-bowler dismissals:** 609 (5.6%) — Run Out (600), Retired Out (6), Obstructing the field (3).

---

## 7. DLS Rain Adjustments

- 25 matches feature rain-revised parameters.
- **Critical finding:** `first_inn_revised_overs` and `second_inn_revised_overs` record **legal balls** (e.g. 114, 90, 48, 42), not decimal overs. Must be divided by 6 to yield allocated overs for required run rate calculations.

---

## 8. Data Availability Matrix for Downstream Phases

All 15 analytical dimensions required for Phase 3 (Match State), Phase 4 (Pressure Index), Phase 6/7 (Batting/Bowling Engines), and Phase 8 (Rankings) are either **AVAILABLE** or **DERIVABLE** from verified fields.

---

## 9. Recommendations for Phase 2 (Cleaning & Integration)

1. **Lineup Deduplication:** Resolve the 40 duplicate player instances in `playing_eleven.csv`.
2. **Squad Filter:** Enforce `is_played == True` to filter out non-playing bench reserves.
3. **Speed Radar Nulls:** Recode `bowl_speed == 0` to `NaN`.
4. **Typo Harmonization:** Standardize `Obstracting the field` to `Obstructing the field`.
5. **DLS Allocation Conversion:** Store both `revised_balls` and `revised_overs = revised_balls / 6.0`.
6. **Optimized Columnar Caching:** Export validated merged tables to `data/processed/` in Parquet format.
