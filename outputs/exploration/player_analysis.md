# PressureIQ — Player, Team, and Playing XI Audit

## Key Findings

1. **Player Population:**
   - 1,217 players registered in tournament squads.
   - 1,082 players appeared on team match sheets.
   - 959 players actually took active part on field (faced a ball, bowled, or were dismissed).
   - 135 players remained exclusively on the squad bench.
   - 123 active squad members never faced a delivery or bowled in their recorded matches.

2. **Homonym Handling:**
   - 7 player names appear under multiple IDs (e.g. *Abdul Samad*, *Haider Ali*, *Basil Hameed*). These represent distinct international vs domestic players or duplicate registry entries, and must **never** be merged without explicit validation.
   - Exactly zero player IDs have multiple names.

3. **Playing XI Scope:**
   - `playing_eleven.csv` contains entire registered squads (ranging from 11 to 27 players per match). Filtering on `is_played == True` isolates the true playing eleven (19,714 records).
   - 40 duplicate composite key instances exist in `playing_eleven.csv` (e.g., match 13613).
