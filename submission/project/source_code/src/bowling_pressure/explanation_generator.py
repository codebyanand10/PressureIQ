"""Explanation generator module for bowling under pressure.

Produces dynamic, explainable narrative summaries and diagnostic attributes for each bowler:
- `pressure_performance_summary`
- `strengths_under_pressure`
- `weaknesses_under_pressure`
- `dominant_performance_factor`
- `classification_reason`

Produces `bowler_pressure_explanations.parquet`.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_bowler_explanations(
    classified_df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate explainable narrative fields and diagnostic factors for every bowler.

    Args:
        classified_df: Output from bowler_classifier with metrics, BPPI-B, and classifications.

    Returns:
        DataFrame representing `bowler_pressure_explanations.parquet`.
    """
    logger.info("Generating narrative performance explanations across %d bowlers...", len(classified_df))

    explanation_records: List[Dict[str, str]] = []

    for _, row in classified_df.iterrows():
        pid = str(row["player_id"])
        name = str(row.get("player_name", "Bowler"))
        cls = str(row.get("bowler_classification", "Unclassified"))
        bppi = float(row.get("bppi_b", 50.0))
        lb = int(row.get("legal_balls_bowled", 0))
        overs = float(row.get("overs_bowled", 0.0))
        runs = int(row.get("runs_conceded", 0))
        wkts = int(row.get("wickets_credited", 0))
        econ = float(row.get("economy_rate", 0.0)) if pd.notna(row.get("economy_rate")) else 0.0
        econ_ret = float(row.get("economy_retention", 100.0)) if pd.notna(row.get("economy_retention")) else 100.0
        econ_diff = float(row.get("economy_difference", 0.0)) if pd.notna(row.get("economy_difference")) else 0.0
        dot_diff = float(row.get("dot_ball_difference", 0.0)) if pd.notna(row.get("dot_ball_difference")) else 0.0
        bnd_diff = float(row.get("boundary_prevention_difference", 0.0)) if pd.notna(row.get("boundary_prevention_difference")) else 0.0
        wkt_diff = float(row.get("wicket_taking_difference", 0.0)) if pd.notna(row.get("wicket_taking_difference")) else 0.0
        rel = str(row.get("reliability_level", "Low"))

        strengths: List[str] = []
        weaknesses: List[str] = []

        # Evaluate Strengths
        if econ_diff <= -0.5:
            strengths.append(f"Maintains disciplined economy ({econ:.2f} rpo, {abs(econ_diff):.2f} below normal baseline)")
        elif econ_ret >= 95.0:
            strengths.append(f"Preserves normal economy efficiency ({econ_ret:.1f}% baseline retention)")

        if dot_diff >= 4.0:
            strengths.append(f"Elevated dot-ball frequency (+{dot_diff:.1f}% dot balls)")

        if bnd_diff <= -4.0:
            strengths.append(f"Restricts boundary scoring effectively ({abs(bnd_diff):.1f}% fewer boundary runs)")

        if wkt_diff >= 0.02:
            strengths.append(f"Heightened wicket-taking threat under pressure ({wkts} wickets)")

        # Evaluate Weaknesses
        if econ_diff >= 1.0:
            weaknesses.append(f"Run concession increases under pressure ({econ:.2f} rpo, +{econ_diff:.2f} above baseline)")

        if dot_diff <= -5.0:
            weaknesses.append(f"Dot-ball percentage declines by {abs(dot_diff):.1f}% under pressure")

        if bnd_diff >= 5.0:
            weaknesses.append("Concedes a higher percentage of runs in boundary strokes")

        if wkts == 0 and lb >= 24:
            weaknesses.append("Unable to produce breakthrough wickets during pressure spells")

        # Determine Dominant Factor
        components = {
            "Economy Discipline": abs(econ_diff) * 10.0,
            "Dot Ball Generation": abs(dot_diff) * 2.0,
            "Boundary Prevention": abs(bnd_diff) * 2.0,
            "Wicket Taking Impact": abs(wkt_diff) * 500.0,
        }
        dominant_factor = max(components, key=components.get) if lb >= 18 else "Sample Size Scarcity"

        # Generate Narrative Summary
        if cls == "Insufficient Evidence":
            summary = (
                f"{name} has delivered only {lb} legal balls ({overs:.1f} overs, {runs} runs), "
                "which is insufficient to establish a statistically reliable bowling pressure rating."
            )
            reason = f"Sample volume ({lb} balls) below the statistical minimum threshold of 18 balls."
            strengths_str = "None identified due to sample constraints"
            weaknesses_str = "None identified due to sample constraints"

        elif cls == "Elite Under Pressure":
            s_text = "; ".join(strengths[:2]) if strengths else "Outstanding overall control"
            summary = (
                f"{name} demonstrates elite high-pressure bowling performance (BPPI-B: {bppi:.1f}), "
                f"bowling {overs:.1f} overs with {s_text}."
            )
            reason = (
                f"BPPI-B ({bppi:.1f} >= 75.0) supported by {rel} sample reliability "
                f"({lb} balls across {row.get('matches_bowled', 0)} matches)."
            )
            strengths_str = "; ".join(strengths) if strengths else "Exceptional high-pressure containment"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "No significant technical weaknesses detected"

        elif cls == "Strong Under Pressure":
            s_text = "; ".join(strengths[:2]) if strengths else "Strong baseline containment"
            summary = (
                f"{name} performs strongly under pressure (BPPI-B: {bppi:.1f}), "
                f"effectively controlling scoring output across {overs:.1f} overs."
            )
            reason = (
                f"BPPI-B ({bppi:.1f} in [60.0, 75.0)) with {rel} reliability evidence."
            )
            strengths_str = "; ".join(strengths) if strengths else "Dependable pressure containment"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "Moderate variability under pressure"

        elif cls == "Average Under Pressure":
            summary = (
                f"{name} bowls at approximately their normal baseline under pressure "
                f"(BPPI-B: {bppi:.1f}, {econ_ret:.1f}% economy retention across {overs:.1f} overs)."
            )
            reason = f"BPPI-B ({bppi:.1f} in [45.0, 60.0)) matches expected historical baseline bowling."
            strengths_str = "; ".join(strengths) if strengths else "Performance parity with standard baseline"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "Limited wicket threat in pressure climaxes"

        else:  # Below Baseline
            w_text = "; ".join(weaknesses[:2]) if weaknesses else "Elevated run concession"
            summary = (
                f"{name} exhibits bowling performance degradation under high pressure (BPPI-B: {bppi:.1f}), "
                f"characterized by {w_text} across {overs:.1f} overs."
            )
            reason = f"BPPI-B ({bppi:.1f} < 45.0) reflects measurable decline relative to standard baseline."
            strengths_str = "; ".join(strengths) if strengths else "Occasional boundary prevention"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "Sub-baseline run restriction"

        explanation_records.append({
            "player_id": pid,
            "player_name": name,
            "bowler_classification": cls,
            "bppi_b": round(bppi, 2),
            "pressure_performance_summary": summary,
            "strengths_under_pressure": strengths_str,
            "weaknesses_under_pressure": weaknesses_str,
            "dominant_performance_factor": dominant_factor,
            "classification_reason": reason,
        })

    exp_df = pd.DataFrame(explanation_records)
    logger.info("Generated bowling performance explanations for %d bowlers.", len(exp_df))
    return exp_df

