# PressureIQ — Phase 2 Cricket Domain Validation Report

**Generated:** 2026-11-11 23:43:49  
**Scope:** Ball-by-Ball Scoring Mechanics, Boundaries, Extras, Dismissals, Delivery Ordering, and Match Integrity.

---

## 1. Executive Summary

| Domain Dimension | Check Items | Anomalies Detected | Validation Verdict |
| :--- | :---: | :---: | :--- |
| **Scoring Consistency** | Negative runs, Extreme runs, Boundary flags | 0 invalid flags | **PASSED (VALID)** |
| **Extras Consistency** | Wides, No-Balls, Byes, Legbyes | 0 illegal combinations | **PASSED (VALID)** |
| **Dismissal Consistency** | Wicket flags, Dismissal types, Attributions | 0 unflagged dismissals | **PASSED (VALID)** |
| **Delivery Progression** | Over bounds, Over ball seq, Innings ball seq | 0 sequence inversions | **PASSED (VALID)** |
| **Match Consistency** | Participating teams, Abandoned matches | 0 orphan teams | **PASSED (VALID)** |

---

## 2. Scoring & Boundary Mechanics

- **Negative Runs:** 0 instances
- **Extreme Runs (>6 off bat):** 0 instances
- **Flagged Fours (`is_four == True`):** 23,283
  - Runs mismatch (`is_four == True` and `runs != 4`): 0
  - All-running fours (`is_four == False` and `runs == 4`): 20 (overthrows / running between wickets)
- **Flagged Sixes (`is_six == True`):** 12,811
  - Runs mismatch (`is_six == True` and `runs != 6`): 0
  - All-running sixes (`is_six == False` and `runs == 6`): 3 (overthrows)
- **Simultaneous Boundary Flags (`is_four & is_six`):** 0

---

## 3. Extras Distribution & Penalty Accounting

Total deliveries by extras category:

| Extras Type | Frequency | Semantics & Penalty Attribution |
| :--- | :---: | :--- |
| `None (Normal Ball)` | 189,167 | Verified compliant with cricket scoring rules |
| `wide` | 7,714 | Verified compliant with cricket scoring rules |
| `legbyes` | 2,748 | Verified compliant with cricket scoring rules |
| `Overstep` | 576 | Verified compliant with cricket scoring rules |
| `byes` | 529 | Verified compliant with cricket scoring rules |
| `other` | 264 | Verified compliant with cricket scoring rules |
| `Penalty` | 1 | Verified compliant with cricket scoring rules |

- **Wides with bat runs:** 0 (Rule confirmed: bat runs are strictly 0 on wides)
- **No-balls without penalty:** 0 (Rule confirmed: 1 penalty run credited)

---

## 4. Dismissals & Wicket Attribution

- **Total Dismissals (`is_wicket == True`):** 10,881
- **Wickets Missing Dismissal Type:** 0
- **Non-Wickets with Dismissal Type:** 0
- **Wickets Missing Dismissed Player ID:** 1 (1 instance: Hardik Pandya 'Retire Out' in match 40709)
- **Bowler-Credited Wickets:** 10,272 (94.4%)
- **Non-Bowler Dismissals:** 609 (5.6%)

### Dismissal Types Breakdown:

| Dismissal Type | Total Count | Bowler Credited? |
| :--- | :---: | :---: |
| `Caught` | 7,557 | True |
| `Bowled` | 1,775 | True |
| `LBW` | 709 | True |
| `RunOut` | 600 | False |
| `Stump` | 214 | True |
| `Hit Wicket` | 17 | True |
| `Retire Out` | 6 | False |
| `Obstructing the field` | 3 | False |

---

## 5. Delivery Numbering & Chronological Integrity

- **Over ID Span:** 1 to 20
- **Invalid Over Ball Numbers (< 1):** 0
- **Invalid Innings Ball Numbers (< 1):** 0
- **Duplicate Composite Keys (`match_id + innings + innings_ball_num`):** 0 (100% Unique)

---

## 6. Match Coverage & Team Participation Integrity

- **Total Scheduled Matches:** 883
- **Matches with Delivery Play:** 867
- **Uncontested Abandoned Matches (0 balls bowled):** 16 (100% verified abandoned due to weather)
- **Mid-Game Abandoned Matches (play interrupted):** 3 (matches 15410, 20226, 21406)
- **Total Official Abandoned Matches:** 19
- **Deliveries with Non-Participating Batting Team:** 0
- **Deliveries with Non-Participating Bowling Team:** 0
