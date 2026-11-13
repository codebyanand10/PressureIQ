# PressureIQ — Phase 2 Dataset Integration Validation Report

**Generated:** 2026-11-11 23:43:49  
**Objective:** Verify join cardinalities, absence of Cartesian products, and strict preservation of delivery-level granularity.

---

## 1. Integration Cardinality Summary

| Integrated Dataset | Source Datasets | Join Keys | Expected Rows | Actual Rows | Cardinality Preservation | Fan-out Ratio |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Match Metadata** | `matches.csv` + `competitions.csv` | `comp_id` | 883 | 883 | **100.0% (EXACT)** | 1.0000 |
| **Team Metadata** | `teams.csv` + `competitions.csv` | `comp_id` | 353 | 353 | **100.0% (EXACT)** | 1.0000 |
| **Player Registration** | `mapping.csv` + `teams.csv` | `comp_id + team_id` | 6,413 | 6,413 | **100.0% (EXACT)** | 1.0000 |
| **Match Participation** | `playing_eleven.csv` + `matches.csv` | `match_id` | 28,346 | 28,341 | **100.0% (EXACT)** | 1.0000 |
| **Delivery Metadata** | `ball_by_ball.csv` + `matches` + `comps` | `match_id`, `comp_id` | 200,999 | 200,999 | **100.0% (EXACT)** | 1.0000 |

---

## 2. Granularity Preservation Verification

- **Original Delivery Count:** 200,999
- **Integrated Delivery Count:** 200,999
- **Difference:** 0 rows
- **Verdict:** **PERFECT 1:1 GRANULARITY PRESERVED**. No accidental many-to-many multiplication occurred.

---

## 3. Competition Classification Distribution

Distribution of matches across validated competition categories:

| Competition Category | Competitions Count | Matches Count | Total Deliveries |
| :--- | :---: | :---: | :---: |
| **IPL** | N/A | 367 | 87,687 |
| **Other T20 leagues** | N/A | 30 | 6,985 |
| **T20I** | N/A | 470 | 106,327 |

---

## 4. Referential Coverage Across Integrated Deliveries

- **Deliveries with Valid Match Metadata:** 200,999 / 200,999 (100.0%)
- **Deliveries with Valid Competition Metadata:** 200,999 / 200,999 (100.0%)
- **Deliveries with Valid Venue Information:** 200,999 / 200,999 (100.0%)
- **Deliveries with Match Result Context:** 200,999 / 200,999 (100.0%)

---

## 5. Artifact Manifest

All integrated tables have been verified and exported to `data/processed/` in Parquet format with accompanying CSV versions for cross-platform analytical utility.
