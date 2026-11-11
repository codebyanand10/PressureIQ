# PressureIQ — DLS and Match Context Investigation

## Critical Discovery: Units of Revised Overs Columns

In `matches.csv`:
- `first_inn_revised_overs` (non-null in 25 matches)
- `second_inn_revised_overs` (non-null in 25 matches)
- `revised_target` (non-null in 23 matches)

### Evidence-Backed Discovery
Despite being named `revised_overs`, the numbers stored represent **LEGAL BALLS**, not overs:
- `114.0` legal balls = 19 overs ($19 \times 6 = 114$)
- `90.0` legal balls = 15 overs ($15 \times 6 = 90$)
- `48.0` legal balls = 8 overs ($8 \times 6 = 48$)
- `42.0` legal balls = 7 overs ($7 \times 6 = 42$)

**Implication for Phase 3 (Match State Reconstruction):**
When reconstructing the target and required run rate (RRR) under rain-affected conditions, algorithms must divide `second_inn_revised_overs` by 6.0 to obtain allocated overs.
