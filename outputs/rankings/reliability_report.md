# PressureIQ — Phase 8 Statistical Reliability Report

## 1. Reliability Architecture
To prevent small-sample anomalies from inflating rankings, Phase 8 couples **match-level block bootstrap resampling (500 resamples)** with **Empirical Bayes shrinkage** towards the cohort median:
$$\lambda = \frac{N}{N + N_0}$$
$$Rating_{\text{final}} = \lambda \cdot Rating_{\text{raw}} + (1 - \lambda) \cdot \mu_{\text{prior}}$$

## 2. Sample Uncertainty Bands
- **Batters Mean CI Width:** 27.20 points
- **Bowlers Mean CI Width:** 16.53 points