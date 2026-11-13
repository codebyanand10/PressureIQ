"""Explanation generator module for batting under pressure.

Produces dynamic, explainable narrative summaries and diagnostic attributes for each batter:
- `pressure_performance_summary`
- `strengths_under_pressure`
- `weaknesses_under_pressure`
- `dominant_performance_factor`
- `classification_reason`

Produces `batter_pressure_explanations.parquet`.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_batter_explanations(
    classified_df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate explainable narrative fields and diagnostic factors for every batter.

    Args:
        classified_df: Output from batter_classifier with metrics, BPPI, and classifications.

    Returns:
        DataFrame representing `batter_pressure_explanations.parquet`.
    """
    logger.info("Generating narrative performance explanations across %d batters...", len(classified_df))

    explanation_records: List[Dict[str, str]] = []

    for _, row in classified_df.iterrows():
        pid = str(row["player_id"])
        name = str(row.get("player_name", "Batter"))
        cls = str(row.get("batter_classification", "Unclassified"))
        bppi = float(row.get("bppi", 50.0))
        bf = int(row.get("balls_faced", 0))
        runs = int(row.get("total_runs", 0))
        sr = float(row.get("strike_rate", 0.0)) if pd.notna(row.get("strike_rate")) else 0.0
        sr_ret = float(row.get("strike_rate_retention", 100.0)) if pd.notna(row.get("strike_rate_retention")) else 100.0
        bnd_diff = float(row.get("boundary_percentage_difference", 0.0)) if pd.notna(row.get("boundary_percentage_difference")) else 0.0
        dot_diff = float(row.get("dot_ball_difference", 0.0)) if pd.notna(row.get("dot_ball_difference")) else 0.0
        dism_diff = float(row.get("dismissal_risk_difference", 0.0)) if pd.notna(row.get("dismissal_risk_difference")) else 0.0
        rel = str(row.get("reliability_level", "Low"))

        strengths: List[str] = []
        weaknesses: List[str] = []

        # Evaluate Strengths
        if sr_ret >= 115.0:
            strengths.append(f"Accelerates scoring rate by +{sr_ret - 100.0:.1f}% under high pressure (SR: {sr:.1f})")
        elif sr_ret >= 95.0:
            strengths.append(f"Preserves normal strike rate efficiency ({sr_ret:.1f}% retention)")

        if bnd_diff >= 5.0:
            strengths.append(f"Higher boundary frequency (+{bnd_diff:.1f}% boundary runs)")

        if dot_diff <= -5.0:
            strengths.append(f"Controls dot balls effectively ({abs(dot_diff):.1f}% fewer dot balls)")

        if dism_diff <= -0.02:
            strengths.append("High wicket preservation when under extreme match duress")

        # Evaluate Weaknesses
        if sr_ret < 85.0:
            weaknesses.append(f"Scoring pace drops under pressure ({sr_ret:.1f}% baseline retention)")

        if dot_diff >= 5.0:
            weaknesses.append(f"Dot ball percentage rises by +{dot_diff:.1f}% under pressure")

        if dism_diff >= 0.02:
            weaknesses.append("Elevated dismissal vulnerability during high-pressure situations")

        if bnd_diff <= -5.0:
            weaknesses.append("Struggles to find boundaries during critical match stages")

        # Determine Dominant Factor
        components = {
            "Strike Rate Acceleration": abs(sr_ret - 100.0),
            "Boundary Efficiency": abs(bnd_diff) * 2.0,
            "Dot Ball Control": abs(dot_diff) * 2.0,
            "Wicket Vulnerability": abs(dism_diff) * 500.0,
        }
        dominant_factor = max(components, key=components.get) if bf >= 15 else "Sample Size Scarcity"

        # Generate Narrative Summary
        if cls == "Insufficient Evidence":
            summary = (
                f"{name} has faced only {bf} high-pressure deliveries ({runs} runs), "
                "which is insufficient to establish a statistically reliable pressure rating."
            )
            reason = f"Sample size ({bf} balls) below the statistical minimum threshold of 15 balls."
            strengths_str = "None identified due to sample constraints"
            weaknesses_str = "None identified due to sample constraints"

        elif cls == "Elite Under Pressure":
            s_text = "; ".join(strengths[:2]) if strengths else "Exceptional overall consistency"
            summary = (
                f"{name} demonstrates elite high-pressure performance (BPPI: {bppi:.1f}), "
                f"facing {bf} balls with {s_text}."
            )
            reason = (
                f"BPPI ({bppi:.1f} >= 75.0) supported by {rel} sample reliability "
                f"({bf} balls across {row.get('matches_count', 0)} matches)."
            )
            strengths_str = "; ".join(strengths) if strengths else "High-pressure scoring composure"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "No significant technical weaknesses detected"

        elif cls == "Strong Under Pressure":
            s_text = "; ".join(strengths[:2]) if strengths else "Strong baseline retention"
            summary = (
                f"{name} performs strongly under pressure (BPPI: {bppi:.1f}), "
                f"effectively maintaining scoring output across {bf} balls."
            )
            reason = (
                f"BPPI ({bppi:.1f} in [60.0, 75.0)) with {rel} reliability evidence."
            )
            strengths_str = "; ".join(strengths) if strengths else "Dependable scoring consistency"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "Moderate variability under pressure"

        elif cls == "Average Under Pressure":
            summary = (
                f"{name} performs at approximately their normal baseline under pressure "
                f"(BPPI: {bppi:.1f}, {sr_ret:.1f}% SR retention across {bf} balls)."
            )
            reason = f"BPPI ({bppi:.1f} in [45.0, 60.0)) matches expected historical baseline performance."
            strengths_str = "; ".join(strengths) if strengths else "Performance parity with standard baseline"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "Limited acceleration in pressure climaxes"

        else:  # Below Baseline
            w_text = "; ".join(weaknesses[:2]) if weaknesses else "Reduced scoring pace"
            summary = (
                f"{name} exhibits performance degradation under high pressure (BPPI: {bppi:.1f}), "
                f"characterized by {w_text} across {bf} balls."
            )
            reason = f"BPPI ({bppi:.1f} < 45.0) reflects measurable decline relative to standard baseline."
            strengths_str = "; ".join(strengths) if strengths else "Occasional boundary release"
            weaknesses_str = "; ".join(weaknesses) if weaknesses else "Sub-baseline scoring efficiency"

        explanation_records.append({
            "player_id": pid,
            "player_name": name,
            "batter_classification": cls,
            "bppi": round(bppi, 2),
            "pressure_performance_summary": summary,
            "strengths_under_pressure": strengths_str,
            "weaknesses_under_pressure": weaknesses_str,
            "dominant_performance_factor": dominant_factor,
            "classification_reason": reason,
        })

    exp_df = pd.DataFrame(explanation_records)
    logger.info("Generated performance explanations for %d batters.", len(exp_df))
    return exp_df

