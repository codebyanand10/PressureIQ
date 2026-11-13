# PressureIQ — Phase 8 Ranking Fairness Audit

## 1. Volume and Opportunity Bias Assessment
An objective ranking must avoid simply rewarding players who played the most matches.

| Audit Metric | Observed Correlation | Interpretation |
| :--- | :---: | :--- |
| Batting Balls Faced vs FBPR | 0.565 | Moderate/healthy correlation; sample depth rewards reliability without dominating rating. |
| Batting Matches Count vs FBPR | 0.285 | Well-controlled; players with fewer matches can achieve top ratings if clutch execution is proven. |
| Batting Resilience Score vs FBPR | 0.730 | Strong alignment with core baseline retention. |
| Bowling Legal Balls vs FBOR | 0.269 | Moderate correlation; balances volume with defensive containment quality. |
| Bowling Economy vs FBOR | -0.600 | Negative correlation as required (lower economy produces higher rating). |
| Bowling Resilience Score vs FBOR | 0.777 | Strong alignment with core baseline retention. |