# PressureIQ — Match Coverage Discrepancy Investigation

## Executive Findings

- **Total Matches in `matches.csv`:** 883
- **Total Matches in `ball_by_ball.csv`:** 867
- **Total Matches in `playing_eleven.csv`:** 880
- **Matches in all 3 datasets:** 867 (867 matches)
- **Matches in `ball_by_ball.csv` but absent in `matches.csv`:** 0 (Zero orphans)
- **Matches in `playing_eleven.csv` but absent in `matches.csv`:** 0 (Zero orphans)

### Explanation of Discrepancies

1. **The 16 Matches Missing from `ball_by_ball.csv`:**
   - Every single one of the 16 matches has `result == 'Match Abandoned'`.
   - **Root Cause:** Matches were formally called off due to adverse weather without a single delivery bowled.
2. **The 3 Matches Missing from `playing_eleven.csv`:**
   - Match IDs: `36210` (England v South Africa, 2025-09-14), `41503` (Ireland v West Indies, 2025-06-14), and `48513` (Sri Lanka v Pakistan, 2026-01-10).
   - **Root Cause:** Abandoned prior to official team lineup submission and toss.
