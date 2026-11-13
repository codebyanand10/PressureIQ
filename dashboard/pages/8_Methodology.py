"""PressureIQ Page 8: Scientific Methodology & Mathematical Architecture.

Comprehensive transparent technical documentation detailing the 11-step end-to-end
analytical pipeline with exact mathematical formulas, weights, and shrinkage equations.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.header import render_header
from dashboard.components.sidebar import render_sidebar


def main() -> None:
    st.set_page_config(page_title="Methodology | PressureIQ", page_icon="📐", layout="wide")

    css_path = PROJECT_ROOT / "dashboard" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header(subtitle="Scientific Methodology & Mathematical Architecture")

    st.markdown(
        """
        ### 📐 End-to-End Analytics Architecture
        **PressureIQ** operates on an 11-phase mathematical pipeline transforming raw, ball-by-ball tournament logs into scientifically defensible, shrinkage-adjusted player pressure ratings.
        """
    )

    # 11-Phase Accordion / Expansion
    with st.expander("1. Data Sources & Coverage Scope", expanded=True):
        st.markdown(
            """
            - **Temporal Coverage:** 2022 to present (matches completed post-January 1, 2022).
            - **Tournament Environments:** Indian Premier League (IPL) and Men's T20 Internationals (T20I).
            - **Delivery Records:** 200,999 ball-by-ball delivery rows across 988 verified matches.
            - **Integrity Rule:** No future delivery lookahead or external match prediction leakage.
            """
        )

    with st.expander("2. Preprocessing, Data Cleaning & Referential Integration"):
        st.markdown(
            """
            - Harmonized multi-source competition player IDs, team abbreviations, and match identifiers.
            - Resolved delivery numbering inconsistencies, illegal deliveries (wides, no-balls), and extras accounting.
            - Strict dismissal mapping: run-outs and obstructing-the-field dismissals are never credited against bowlers.
            """
        )

    with st.expander("3. Match-State Reconstruction Engine"):
        st.markdown(
            """
            Reconstructs the exact situational context immediately prior to and after every single ball:
            - **Pre-Delivery State:** Current score, wickets lost, legal balls bowled, and balls remaining.
            - **Chasing Context:** Exact target score, runs required, and Required Run Rate ($RRR$).
            - **First Innings Context:** Dynamic projected totals based on historical scoring par at that phase and wicket count.
            """
        )

    with st.expander("4. Pressure Detection Engine & Weighting Model", expanded=True):
        st.markdown(
            r"""
            Quantifies the multidimensional pressure ($P \in [0, 100]$) experienced at every delivery:
            
            $$\\text{Batting Pressure} = 0.35 \\cdot P_{\\text{RRR}} + 0.25 \\cdot P_{\\text{Wicket}} + 0.15 \\cdot P_{\\text{Time}} + 0.15 \\cdot P_{\\text{Closeness}} + 0.10 \\cdot P_{\\text{Importance}}$$
            
            $$\\text{Bowling Pressure} = 0.30 \\cdot P_{\\text{Defend}} + 0.25 \\cdot P_{\\text{Wicket Hazard}} + 0.20 \\cdot P_{\\text{Death Leverage}} + 0.15 \\cdot P_{\\text{Closeness}} + 0.10 \\cdot P_{\\text{Importance}}$$
            
            **Validated Pressure Tiers:**
            - **Very Low:** $0 \\le P < 20$
            - **Low:** $20 \\le P < 40$
            - **Moderate:** $40 \\le P < 60$
            - **High:** $60 \\le P < 80$ (High-Pressure Threshold)
            - **Extreme:** $80 \\le P \\le 100$
            """
        )

    with st.expander("5. Player Baseline Calculation & Empirical Bayes Shrinkage"):
        st.markdown(
            """
            Establishes historical baseline performance across all normal deliveries for every candidate.
            To avoid sample-size distortion, raw historical metrics are shrunken toward competition cohort priors:
            
            $$\\theta_{\\text{shrunk}} = (1 - B_i) \\cdot \\bar{x}_i + B_i \\cdot \\mu_{\\text{cohort}}$$
            
            $$B_i = \\frac{\\sigma^2 / n_i}{\\sigma^2 / n_i + \\tau^2}$$
            
            Where $\\tau^2$ is the between-player variance and $\\sigma^2 / n_i$ is estimation error variance.
            """
        )

    with st.expander("6. Batting Performance Under Pressure (BPPI)"):
        st.markdown(
            """
            The **Batter Pressure Performance Index (BPPI)** evaluates how well a batter maintains their scoring capability:
            
            $$\\text{BPPI} = 0.40 \\cdot S_{\\text{SR Retention}} + 0.25 \\cdot S_{\\text{Avg Retention}} + 0.20 \\cdot S_{\\text{Boundary Eff}} + 0.15 \\cdot S_{\\text{Dot Control}}$$
            """
        )

    with st.expander("7. Bowling Performance Under Pressure (BPPI-B)"):
        st.markdown(
            """
            The **Bowler Pressure Performance Index (BPPI-B)** quantifies containment and breakthrough capacity:
            
            $$\\text{BPPI-B} = 0.35 \\cdot S_{\\text{Econ Retention}} + 0.30 \\cdot S_{\\text{Wicket Taking}} + 0.20 \\cdot S_{\\text{Dot Generation}} + 0.15 \\cdot S_{\\text{Boundary Restriction}}$$
            """
        )

    with st.expander("8. Unified Rating Calculation (FBPR & FBOR)", expanded=True):
        st.markdown(
            """
            The final unified ratings synthesize four core pillars on a normalized $0 - 100$ scale:
            
            **Final Batter Pressure Rating (FBPR):**
            $$\\text{FBPR} = 0.35 \\cdot S_{\\text{Resilience (BPPI)}} + 0.30 \\cdot S_{\\text{Absolute Execution}} + 0.20 \\cdot S_{\\text{Consistency}} + 0.15 \\cdot S_{\\text{Context Difficulty}}$$
            
            **Final Bowler Pressure Rating (FBOR):**
            $$\\text{FBOR} = 0.35 \\cdot S_{\\text{Resilience (BPPI-B)}} + 0.30 \\cdot S_{\\text{Absolute Execution}} + 0.20 \\cdot S_{\\text{Consistency}} + 0.15 \\cdot S_{\\text{Role Leverage}}$$
            """
        )

    with st.expander("9. Eligibility Exposure Thresholds"):
        st.markdown(
            """
            To qualify for official ranking:
            - **Batters:** Minimum of **40 legal balls faced** under high or extreme pressure ($P \\ge 60$).
            - **Bowlers:** Minimum of **48 legal deliveries bowled** (8 overs) under high or extreme pressure ($P \\ge 60$).
            - Must have established historical baseline records and valid registration data.
            """
        )

    with st.expander("10. Statistical Reliability & Bayesian Uncertainty"):
        st.markdown(
            """
            Every candidate is assigned a Bayesian shrinkage coefficient and 95% Confidence Interval:
            
            $$CI_{95} = [\\text{Rating} - 1.96 \\cdot SE_i, \\; \\text{Rating} + 1.96 \\cdot SE_i]$$
            
            **Reliability Classifications:**
            - **High:** $n_i \\ge 80$ deliveries, $SE_i < 3.5$, $CI_{95} \\text{ width} < 14.0$
            - **Medium:** $40 \\le n_i < 80$ deliveries, $3.5 \\le SE_i < 6.0$
            - **Provisional:** Low sample or wide CI; flagged with operational caveat.
            """
        )

    with st.expander("11. Empirical Validation & Robustness Verification"):
        st.markdown(
            """
            - **Match-Level Block Bootstrap:** 100 full iterations resampling entire matches to preserve intra-game correlation.
            - **Leave-One-Match-Out (LOMO) Jackknife:** Iterative dropping of individual games to identify single-match leverage.
            - **Sensitivity Analysis:** Tested across 6 weight variations and $\\pm 50\\%$ eligibility threshold shifts.
            - **Exhaustive Leakage Audit:** 12 automated checks ensuring 0 future-state contamination.
            """
        )


if __name__ == "__main__":
    main()

