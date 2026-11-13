# PressureIQ – Competition Submission Package
## SupeRR Selector Season 2 – Round 1: Pressure Performance Analytics

Welcome to the official submission package for **PressureIQ**, an advanced data-driven cricket analytics platform that models, quantifies, and evaluates player performance under high-pressure conditions across IPL and T20I matches from 2022 to the present.

---

### Package Contents

```text
submission/
├── README.md                               <- This guide
├── FINAL_SUBMISSION_CHECKLIST.md           <- Official deliverables checklist
├── FINAL_AUDIT_REPORT.md                   <- Comprehensive 15-section audit report
│
├── rankings/                               <- Official judge-ready leaderboards
│   ├── Top_10_Batters.csv                  <- Top 10 Batters (CSV format)
│   ├── Top_10_Batters.xlsx                 <- Top 10 Batters (Excel spreadsheet)
│   ├── Top_10_Bowlers.csv                  <- Top 10 Bowlers (CSV format)
│   └── Top_10_Bowlers.xlsx                 <- Top 10 Bowlers (Excel spreadsheet)
│
├── methodology/                            <- Research documentation
│   ├── PressureIQ_Methodology_Report.pdf   <- Official PDF report
│   └── PressureIQ_Methodology_Report.docx  <- Official Word document
│
├── evidence/                               <- Visual and empirical validation
│   ├── Ranking_Validation_Summary.pdf      <- Executive ranking validation brief
│   ├── Statistical_Robustness_Summary.pdf  <- Statistical validation scorecard brief
│   └── Final_Dashboard_Screenshots/        <- Visual dashboard telemetry screenshots
│
├── video/                                  <- Optional 45-60s journey video materials
│   ├── Project_Journey_Script.md           <- Broadcast voiceover script
│   └── Project_Journey_Storyboard.md       <- Scene-by-scene visual storyboard
│
└── project/                                <- Clean runnable source snapshot
    ├── source_code/                        <- Python modules (src/ and dashboard/)
    ├── config/                             <- Analytical configuration YAMLs
    ├── requirements.txt                    <- Dependency specifications
    └── README.md                           <- Codebase setup instructions
```

---

### Official Results Summary

- **#1 Batter Under Pressure:** **Rinku Singh** (Final Batter Pressure Rating: **77.07**)
  - *High-Pressure Strike Rate:* 174.4 | *Baseline Strike Rate:* 142.6 | *Reliability:* 0.94
- **#1 Bowler Under Pressure:** **Joshua Little** (Final Bowler Pressure Rating: **50.05**)
  - *High-Pressure Economy Rate:* 7.82 | *Baseline Economy Rate:* 8.44 | *Reliability:* 0.88

---

### Running the Dashboard
To explore the full 9-page interactive application:

```bash
pip install -r project/requirements.txt
streamlit run project/source_code/dashboard/app.py
```
