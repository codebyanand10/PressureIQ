# PressureIQ — Delivery Field Semantics & Mechanics

## 1. Run Attribution Rules
- `runs` represents **strictly batter runs scored off the bat**.
- On all 7,714 `wide` deliveries, `runs == 0`.
- On `Overstep` (no-ball) deliveries, `runs` records batter runs off the bat, while `extras1_runs` records the 1 penalty run.
- **Total Team Score Equation:**
  $$\text{Total Team Runs} = \text{runs} + \text{extras1\_runs} + \text{extras\_2\_runs}$$

## 2. Boundaries vs Runs
- `is_four == True`: 23,283 deliveries.
- `is_six == True`: 12,811 deliveries.
- 20 deliveries have `runs == 4` with `is_four == False` (all-running 4s or overthrows).
- 3 deliveries have `runs == 6` with `is_six == False` (all-running 6s / overthrows).

## 3. Delivery Numbering
- `overid`: 1-indexed (1 to 20).
- `over_ball_num`: Increments on **every** ball bowled (legal or illegal), reaching up to 13 in heavily penalized overs.
- `innings_ball_num`: Increments on every ball bowled in the innings.
- **Legal Delivery Definition:** A delivery is legal if and only if `extras_type` is NOT `wide` and NOT `Overstep`. Byes and Leg-byes are legal deliveries.
