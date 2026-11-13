# PressureIQ — Complete Data Dictionary & Schema Specification

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Document:** Data Dictionary & Schema Manual  
**Version:** 1.0.0  
**Target Submission:** SupeRR Selector Season 2 — Round 1

---

## 1. Raw Competition Datasets (Phase 1 & Phase 2)

### 1.1 `competitions.csv`
- **Description:** Tournament metadata covering IPL and T20 International competitions.
- **Record Count:** 6 rows, 4 columns.
- **Primary Key:** `comp_id`

| Column Name | Data Type | Nullable | Description / Valid Values |
| :--- | :---: | :---: | :--- |
| `comp_id` | `VARCHAR` | No | Unique competition identifier (e.g. `IPL`, `T20I`). |
| `comp_name` | `VARCHAR` | No | Full human-readable tournament name. |
| `match_format` | `VARCHAR` | No | Match format (`T20`). |
| `competition_type` | `VARCHAR` | No | `LEAGUE` (IPL) or `INTERNATIONAL` (T20I). |

---

### 1.2 `teams.csv`
- **Description:** Team entity definitions for franchise clubs and international sides.
- **Record Count:** 38 rows, 4 columns.
- **Primary Key:** `team_id`

| Column Name | Data Type | Nullable | Description / Valid Values |
| :--- | :---: | :---: | :--- |
| `team_id` | `VARCHAR` | No | Unique team identifier code (e.g. `CSK`, `IND`, `RR`). |
| `team_name` | `VARCHAR` | No | Official team title. |
| `team_short_name` | `VARCHAR` | Yes | Abbreviated 2-4 character display label. |
| `team_type` | `VARCHAR` | No | Category (`FRANCHISE` or `NATIONAL`). |

---

### 1.3 `matches.csv`
- **Description:** Match fixture details, dates, venues, toss outcomes, and results.
- **Record Count:** 988 cleaned rows (after removing 4 abandoned games without legal deliveries).
- **Primary Key:** `match_id`

| Column Name | Data Type | Nullable | Description / Valid Values |
| :--- | :---: | :---: | :--- |
| `match_id` | `VARCHAR` | No | Unique match identifier. |
| `comp_id` | `VARCHAR` | No | Foreign key referencing `competitions.comp_id`. |
| `season` | `VARCHAR` | No | Tournament year / season (e.g. `2022`, `2023`, `2024`). |
| `match_date` | `DATE` | No | Fixture date (YYYY-MM-DD). |
| `team1_id` | `VARCHAR` | No | Foreign key referencing batting/home team. |
| `team2_id` | `VARCHAR` | No | Foreign key referencing bowling/away team. |
| `toss_winner_team_id`| `VARCHAR` | No | Team winning the pre-match coin toss. |
| `toss_decision` | `VARCHAR` | No | Choice (`bat` or `field`). |
| `venue` | `VARCHAR` | No | Stadium and city title. |
| `city` | `VARCHAR` | Yes | Host city. |
| `winner_team_id` | `VARCHAR` | Yes | Match winner (null for tie/abandoned). |
| `win_by_runs` | `INTEGER` | Yes | Run margin if defending team won. |
| `win_by_wickets` | `INTEGER` | Yes | Wicket margin if chasing team won. |
| `stage` | `VARCHAR` | No | Tournament stage (`LEAGUE`, `QUALIFIER`, `FINAL`). |
| `is_knockout` | `BOOLEAN` | No | True if elimination or playoff fixture. |

---

### 1.4 `playing_eleven.csv`
- **Description:** Roster of 11 named players fielded by each team per fixture.
- **Record Count:** 21,736 rows, 4 columns.
- **Composite Key:** `(match_id, team_id, player_id)`

| Column Name | Data Type | Nullable | Description / Valid Values |
| :--- | :---: | :---: | :--- |
| `match_id` | `VARCHAR` | No | Foreign key referencing `matches.match_id`. |
| `team_id` | `VARCHAR` | No | Foreign key referencing `teams.team_id`. |
| `player_id` | `VARCHAR` | No | Master player identifier. |
| `is_captain` | `BOOLEAN` | No | True if player was designated team captain. |

---

### 1.5 `competition_team_player_mapping.csv`
- **Description:** Player tournament registration contracts across seasons.
- **Record Count:** 4,120 rows, 5 columns.
- **Composite Key:** `(comp_id, season, team_id, player_id)`

---

### 1.6 `ball_by_ball.csv` / `cleaned_ball_by_ball.parquet`
- **Description:** Granular ball-by-ball delivery log for all matches.
- **Record Count:** 200,999 rows, 35 columns.
- **Composite Key:** `(match_id, innings, overid, over_ball_num)`

| Column Name | Data Type | Nullable | Description / Valid Values |
| :--- | :---: | :---: | :--- |
| `match_id` | `VARCHAR` | No | Foreign key referencing `matches.match_id`. |
| `innings` | `INTEGER` | No | Innings number (1, 2, or super over 3/4). |
| `overid` | `INTEGER` | No | Zero-indexed completed overs ($0 \le o \le 19$). |
| `over_ball_num` | `INTEGER` | No | Delivery sequence number within the over ($1, 2, \dots$). |
| `batting_team_id` | `VARCHAR` | No | Team currently batting. |
| `bowling_team_id` | `VARCHAR` | No | Team currently fielding. |
| `striker_id` | `VARCHAR` | No | Player facing the delivery. |
| `non_striker_id` | `VARCHAR` | No | Partner at the non-striker's crease. |
| `bowler_id` | `VARCHAR` | No | Bowler delivering the ball. |
| `batter_runs` | `INTEGER` | No | Runs off the bat ($0, 1, 2, 3, 4, 6$). |
| `extras_runs` | `INTEGER` | No | Conceded extras on the delivery. |
| `extras_type` | `VARCHAR` | Yes | Type (`wides`, `noballs`, `byes`, `legbyes`, null). |
| `is_legal_delivery`| `BOOLEAN` | No | True if delivery counts against over limit. |
| `is_wicket` | `BOOLEAN` | No | True if dismissal occurred on delivery. |
| `dismissal_type` | `VARCHAR` | Yes | Method of dismissal (bowled, caught, run out, lbw, etc.). |
| `dismissed_player_id`| `VARCHAR` | Yes | Player dismissed. |

---

## 2. Reconstructed Match State & Pressure Datasets (Phases 3 & 4)

### 2.1 `match_state_reconstructed.parquet`
- **Description:** Reconstructed situation immediately prior to and after each ball.
- **Key Columns Added:**
  - `runs_before`, `runs_after`: Cumulative innings score.
  - `wickets_before`, `wickets_after`: Cumulative wickets lost.
  - `legal_balls_bowled_before`, `legal_balls_remaining_before`: Ball countdown.
  - `target_score`: Chasing target score ($T = \text{inn1\_total} + 1$).
  - `runs_required_before`: $T - \text{runs\_before}$.
  - `required_run_rate_before`: $\frac{R_{\text{req}}}{B_{\text{rem}} / 6}$ (strictly null in 1st innings).
  - `current_run_rate_before`: $\frac{R_{\text{scored}}}{B_{\text{bowled}} / 6}$.
  - `innings_phase_before`: `POWERPLAY` ($o < 6$), `MIDDLE_OVERS` ($6 \le o < 16$), `DEATH_OVERS` ($o \ge 16$).

### 2.2 `pressure_scores.parquet`
- **Description:** Ball-by-ball continuous pressure scores ($0–100$) and categorical tiers.
- **Record Count:** 200,999 rows.
- **Key Columns Added:**
  - `batting_pressure_score`: Continuous batting difficulty score ($[0, 100]$).
  - `bowling_pressure_score`: Continuous defensive bowling pressure score ($[0, 100]$).
  - `batting_pressure_level`: Categorical tier (`Very Low`, `Low`, `Moderate`, `High`, `Extreme`).
  - `dominant_pressure_factor`: Primary driver (e.g. `RRR`, `Wickets`, `Time`, `ParDeficit`).

---

## 3. Player Baseline Datasets (Phase 5)

### 3.1 `batting_overall_baseline.parquet` (545 rows)
- **Key Columns:** `player_id`, `balls_faced`, `total_runs`, `overall_strike_rate`, `overall_batting_average`, `overall_shrunk_strike_rate`, `overall_shrunk_batting_average`, `overall_boundary_percentage`, `overall_dot_ball_percentage`.

### 3.2 `bowling_overall_baseline.parquet` (486 rows)
- **Key Columns:** `player_id`, `legal_balls_bowled`, `runs_conceded`, `wickets_credited`, `overall_economy_rate`, `overall_bowling_average`, `overall_shrunk_economy_rate`, `overall_dot_ball_percentage`.

---

## 4. Official Ranking Datasets (Phase 8)

### 4.1 `batter_ratings.parquet` (170 rows)
- **Key Columns:**
  - `rank`: Official integer rank (#1 to #170).
  - `player_id`, `player_name`: Identity fields.
  - `final_fbpr`: Final Batter Pressure Rating ($0–100$ scale).
  - `ci_lower_fbpr`, `ci_upper_fbpr`: 95% Bayesian Confidence Interval.
  - `bppi`: Batter Pressure Performance Index ($0–100$).
  - `strike_rate`: High-pressure strike rate ($P \ge 60$).
  - `strike_rate_difference`: Delta vs baseline ($SR_{\text{HP}} - SR_{\text{Base}}$).
  - `boundary_percentage`: % high-pressure runs from 4s and 6s.
  - `dot_ball_percentage`: % high-pressure non-scoring deliveries.
  - `balls_faced`: High-pressure exposure volume ($n_i \ge 40$).
  - `reliability_level`: `High`, `Medium`, or `Provisional`.
  - `ranking_explanation`, `key_strengths`, `baseline_comparison`, `ranking_limitations`: Narrative explanations.

### 4.2 `bowler_ratings.parquet` (232 rows)
- **Key Columns:**
  - `rank`: Official integer rank (#1 to #232).
  - `player_id`, `player_name`: Identity fields.
  - `final_fbor`: Final Bowler Pressure Rating ($0–100$ scale).
  - `ci_lower_fbor`, `ci_upper_fbor`: 95% Bayesian Confidence Interval.
  - `bppi_b`: Bowler Pressure Performance Index ($0–100$).
  - `economy_rate`: High-pressure economy rate ($P \ge 60$).
  - `economy_difference`: Delta vs baseline ($Econ_{\text{Base}} - Econ_{\text{HP}}$).
  - `wickets_credited`: Wickets taken under high pressure (excludes run-outs).
  - `legal_balls_bowled`: High-pressure legal ball count ($n_i \ge 48$).
  - `bowling_role`: Phase classification (`Death`, `Powerplay`, `Middle`, `Multi-Phase`).
  - `primary_bowling_style`: `Pace` or `Spin`.
  - `reliability_level`: `High`, `Medium`, or `Provisional`.

---

## 5. Statistical Validation Datasets (Phase 9)

### 5.1 `robustness_scorecard.parquet` (10 rows)
- **Columns:** `dimension`, `batting_result`, `bowling_result`, `supporting_evidence`, `operational_impact`.
- **Dimensions:** Bootstrap Reliability, Top-10 Stability, Weight Sensitivity, Eligibility Sensitivity, Pressure Model Sensitivity, Competition Fairness, Role Fairness, Sample-Size Reliability, Baseline Sensitivity, Data Leakage Audit. All evaluate to `PASS`.

### 5.2 `batting_bootstrap_results.parquet` & `bowling_bootstrap_results.parquet`
- **Columns:** `player_id`, `official_rank`, `official_rating`, `bootstrap_mean`, `ci_90_lower`, `ci_90_upper`, `ci_95_lower`, `ci_95_upper`, `median_bootstrap_rank`, `best_bootstrap_rank`, `worst_bootstrap_rank`, `prob_in_top_10`, `prob_in_top_5`.

### 5.3 `leakage_audit.parquet` (12 rows)
- **Columns:** `check_id`, `test_performed`, `data_fields_examined`, `result` (`PASS`), `severity`, `evidence`.

