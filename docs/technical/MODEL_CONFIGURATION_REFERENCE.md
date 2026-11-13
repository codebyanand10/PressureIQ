# PressureIQ — Model Configuration & Parameter Reference

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Document:** Model Hyperparameters & Configuration Mapping  
**Config File:** `config/settings.yaml`  
**Version:** 1.0.0  

---

## 1. Match State Configuration (`match_state`)

```yaml
match_state:
  default_t20_overs: 20
  default_super_over_overs: 1
  innings_phases:
    powerplay_end: 0.30       # Over 6 completed (6/20 = 0.30)
    middle_overs_end: 0.75     # Over 15 completed (15/20 = 0.75)
  validation:
    max_wickets: 10
    max_super_over_wickets: 2
    enforce_non_negative_runs: true
    enforce_non_negative_balls: true
```

---

## 2. Pressure Detection Engine Weights (`pressure`)

```yaml
pressure:
  batting_weights:
    rrr_pressure: 0.35
    wicket_pressure: 0.25
    time_pressure: 0.15
    match_closeness: 0.15
    match_importance: 0.10
  bowling_weights:
    target_defend_pressure: 0.30
    wicket_hazard_pressure: 0.25
    death_over_leverage: 0.20
    match_closeness: 0.15
    match_importance: 0.10
  thresholds:
    very_low_max: 20.0
    low_max: 40.0
    moderate_max: 60.0
    high_pressure_threshold: 60.0
    extreme_pressure_threshold: 80.0
```

---

## 3. Historical Baseline Settings (`baselines`)

```yaml
baselines:
  min_deliveries_overall: 30
  min_matches_overall: 2
  shrinkage:
    enabled: true
    method: "empirical_bayes"
    k_prior_weight: 25.0
```

---

## 4. Performance Engine Settings (`batting_pressure` & `bowling_pressure`)

```yaml
batting_pressure:
  high_pressure_cutoff: 60.0
  extreme_pressure_cutoff: 80.0
  bppi_weights:
    strike_rate_retention: 0.40
    average_retention: 0.25
    boundary_efficiency: 0.20
    dot_ball_control: 0.15

bowling_pressure:
  high_pressure_cutoff: 60.0
  extreme_pressure_cutoff: 80.0
  bppi_b_weights:
    economy_retention: 0.35
    wicket_taking: 0.30
    dot_ball_generation: 0.20
    boundary_prevention: 0.15
```

---

## 5. Unified Ranking Engine Settings (`rankings`)

```yaml
rankings:
  eligibility:
    min_balls_faced_batting: 40
    min_legal_balls_bowled: 48    # 8 overs
    min_high_pressure_matches: 2
  primary_weights:
    resilience_score: 0.35
    absolute_performance: 0.30
    consistency_score: 0.20
    context_difficulty: 0.15
  shrinkage:
    prior_cohort_rating: 50.0
    full_sample_threshold_batting: 100
    full_sample_threshold_bowling: 120
    max_shrinkage_penalty: 0.40
```

---

## 6. Statistical Validation Settings (`validation`)

```yaml
validation:
  bootstrap:
    resamples: 100
    random_seed: 42
    confidence_levels: [0.90, 0.95]
  sensitivity:
    scenarios:
      - "balanced"
      - "absolute_focused"
      - "baseline_focused"
      - "consistency_focused"
      - "reliability_focused"
      - "pressure_difficulty_focused"
    eligibility_multipliers: [0.5, 1.0, 1.5]
```

