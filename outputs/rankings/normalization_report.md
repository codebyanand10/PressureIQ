# PressureIQ — Phase 8 Normalization and Weighting Methodology

## 1. Principles
- Metric directionality is strictly preserved: higher is better for strike rate, boundary %, dot balls; lower is better for economy and bowling average.
- Extreme single-match outliers are bounded through robust linear scaling with domain-informed clipping thresholds.
- Missing averages due to zero dismissals or zero wickets are safely handled without imputing artificial zeros.

## 2. Weight Profiles
```json
{
  "primary": {
    "quality_and_resilience": 0.5,
    "absolute_performance": 0.2,
    "consistency": 0.15,
    "pressure_context": 0.15
  },
  "balanced": {
    "quality_and_resilience": 0.4,
    "absolute_performance": 0.3,
    "consistency": 0.15,
    "pressure_context": 0.15
  },
  "baseline_focused": {
    "quality_and_resilience": 0.6,
    "absolute_performance": 0.15,
    "consistency": 0.15,
    "pressure_context": 0.1
  },
  "absolute_focused": {
    "quality_and_resilience": 0.3,
    "absolute_performance": 0.45,
    "consistency": 0.15,
    "pressure_context": 0.1
  }
}
```