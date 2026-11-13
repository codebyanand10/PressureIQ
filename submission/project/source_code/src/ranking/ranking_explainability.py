"""Ranking explainability and narrative generation module for Phase 8.

Generates human-readable, transparent, and dashboard-ready explanation attributes:
- `ranking_explanation` (complete summary sentence)
- `key_strengths` (bullet points of exceptional metrics)
- `baseline_comparison` (metric delta against baseline)
- `reliability_summary` (sample size, matches, and uncertainty band)
- `pressure_exposure` (high vs extreme delivery distribution)
- `ranking_limitations` (caveats or areas of elevated variance)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def generate_batting_ranking_explanations(df: pd.DataFrame) -> pd.DataFrame:
    """Generate explainable narrative fields for ranked batters."""
    records = []

    for _, row in df.iterrows():
        pid = str(row["player_id"])
        name = str(row.get("player_name", "Batter"))
        rank = int(row.get("rank", 0))
        fbpr = float(row.get("final_fbpr", 0.0))
        bppi = float(row.get("bppi", 0.0))
        balls = int(row.get("balls_faced", 0))
        matches = int(row.get("matches_count", 0))
        inns = int(row.get("innings_count", 0))
        runs = int(row.get("total_runs", 0))
        sr = float(row.get("strike_rate", 0.0)) if pd.notna(row.get("strike_rate")) else 0.0
        base_sr = float(row.get("overall_strike_rate", 0.0)) if pd.notna(row.get("overall_strike_rate")) else 0.0
        sr_diff = float(row.get("strike_rate_difference", 0.0)) if pd.notna(row.get("strike_rate_difference")) else 0.0
        bnd_pct = float(row.get("boundary_percentage", 0.0)) if pd.notna(row.get("boundary_percentage")) else 0.0
        dot_pct = float(row.get("dot_ball_percentage", 0.0)) if pd.notna(row.get("dot_ball_percentage")) else 0.0
        ci_low = float(row.get("ci_lower_fbpr", 0.0)) if pd.notna(row.get("ci_lower_fbpr")) else 0.0
        ci_high = float(row.get("ci_upper_fbpr", 0.0)) if pd.notna(row.get("ci_upper_fbpr")) else 0.0
        rel = str(row.get("reliability_level", "Medium"))

        # Strengths
        strengths = []
        if sr_diff >= 10.0:
            strengths.append(f"Elevated strike rate (+{sr_diff:.1f} rpo above normal baseline)")
        elif sr_diff >= 0.0:
            strengths.append("Maintains scoring baseline under high pressure")
        if sr >= 150.0:
            strengths.append(f"Explosive pressure scoring ({sr:.1f} SR)")
        if bnd_pct >= 50.0:
            strengths.append(f"Elite boundary generation ({bnd_pct:.1f}% runs from boundaries)")
        if dot_pct <= 35.0:
            strengths.append(f"Strong strike rotation ({dot_pct:.1f}% dot ball rate)")
        if not strengths:
            strengths.append("Dependable middle-order scoring presence")

        # Baseline comparison
        base_comp = (
            f"Pressure SR {sr:.1f} vs Normal Baseline {base_sr:.1f} "
            f"({'+' if sr_diff >= 0 else ''}{sr_diff:.1f} diff)"
        )

        # Reliability
        rel_summary = f"{rel} Reliability ({balls} balls across {matches} matches, 95% CI: [{ci_low:.1f}, {ci_high:.1f}])"

        # Exposure
        ext_balls = int(row.get("extreme_pressure_balls", 0))
        exposure = f"{balls} high-pressure deliveries ({ext_balls} extreme-pressure deliveries across {inns} innings)"

        # Limitations
        limitations = []
        if matches < 6:
            limitations.append("Moderate sample volume across matches")
        if dot_pct > 45.0:
            limitations.append("High dot-ball accumulation in tight finishes")
        if float(row.get("strike_rate_variability", 0.0)) > 60.0:
            limitations.append("Performance variance across distinct innings")
        if not limitations:
            limitations.append("None identified; consistent multi-match contributions")

        # Dynamic sentence summary
        if sr_diff >= 5.0 and sr >= 140.0:
            summary = (
                f"{name} ranks #{rank} with an FBPR of {fbpr:.2f}, demonstrating clutch scoring acceleration "
                f"({sr:.1f} SR, {sr_diff:+.1f} vs baseline) across {matches} high-pressure matches."
            )
        else:
            summary = (
                f"{name} ranks #{rank} with an FBPR of {fbpr:.2f}, providing resilient scoring containment and baseline retention "
                f"({sr:.1f} SR across {balls} balls in {matches} matches)."
            )

        records.append({
            "player_id": pid,
            "player_name": name,
            "role": "batter",
            "rank": rank,
            "final_rating": fbpr,
            "ranking_explanation": summary,
            "key_strengths": "; ".join(strengths),
            "baseline_comparison": base_comp,
            "reliability_summary": rel_summary,
            "pressure_exposure": exposure,
            "ranking_limitations": "; ".join(limitations),
        })

    return pd.DataFrame(records)


def generate_bowling_ranking_explanations(df: pd.DataFrame) -> pd.DataFrame:
    """Generate explainable narrative fields for ranked bowlers."""
    records = []

    for _, row in df.iterrows():
        pid = str(row["player_id"])
        name = str(row.get("player_name", "Bowler"))
        rank = int(row.get("rank", 0))
        fbor = float(row.get("final_fbor", 0.0))
        bppi_b = float(row.get("bppi_b", 0.0))
        balls = int(row.get("legal_balls_bowled", 0))
        overs = float(row.get("overs_bowled", 0.0))
        matches = int(row.get("matches_bowled", 0))
        inns = int(row.get("innings_bowled", 0))
        wkts = int(row.get("wickets_credited", 0))
        econ = float(row.get("economy_rate", 0.0)) if pd.notna(row.get("economy_rate")) else 0.0
        base_econ = float(row.get("overall_economy_rate", 0.0)) if pd.notna(row.get("overall_economy_rate")) else 0.0
        econ_diff = float(row.get("economy_difference", 0.0)) if pd.notna(row.get("economy_difference")) else 0.0
        dot_pct = float(row.get("dot_ball_percentage", 0.0)) if pd.notna(row.get("dot_ball_percentage")) else 0.0
        role = str(row.get("bowling_role", "Multi-Phase Bowler"))
        ci_low = float(row.get("ci_lower_fbor", 0.0)) if pd.notna(row.get("ci_lower_fbor")) else 0.0
        ci_high = float(row.get("ci_upper_fbor", 0.0)) if pd.notna(row.get("ci_upper_fbor")) else 0.0
        rel = str(row.get("reliability_level", "Medium"))

        # Strengths
        strengths = []
        if econ <= 8.5:
            strengths.append(f"Superb run restriction ({econ:.2f} rpo under pressure)")
        if econ_diff <= -0.5:
            strengths.append(f"Outperforms normal baseline ({abs(econ_diff):.2f} rpo lower)")
        if dot_pct >= 40.0:
            strengths.append(f"Relentless dot-ball pressure ({dot_pct:.1f}% dot balls)")
        if wkts >= 8:
            strengths.append(f"Clutch breakthrough threat ({wkts} wickets)")
        if role == "Death-Overs Specialist":
            strengths.append("High-difficulty death overs execution")
        if not strengths:
            strengths.append("Dependable defensive containment")

        # Baseline comparison
        base_comp = (
            f"Pressure Economy {econ:.2f} vs Normal Baseline {base_econ:.2f} "
            f"({'+' if econ_diff > 0 else ''}{econ_diff:.2f} diff)"
        )

        # Reliability
        rel_summary = f"{rel} Reliability ({balls} legal balls across {matches} matches, 95% CI: [{ci_low:.1f}, {ci_high:.1f}])"

        # Exposure
        ext_balls = int(row.get("extreme_pressure_balls", 0))
        exposure = f"{balls} legal deliveries ({overs:.1f} overs, {ext_balls} extreme-pressure balls in {inns} innings)"

        # Limitations
        limitations = []
        if matches < 6:
            limitations.append("Moderate match sample size")
        if wkts < 3:
            limitations.append("Limited wicket breakthroughs under pressure")
        if float(row.get("economy_rate_variability", 0.0)) > 3.0:
            limitations.append("Spell-to-spell economy variability")
        if not limitations:
            limitations.append("None identified; consistent multi-spell containment")

        # Dynamic sentence summary
        if econ <= 8.5 and dot_pct >= 38.0:
            summary = (
                f"{name} ranks #{rank} with an FBOR of {fbor:.2f}, combining disciplined run restriction "
                f"({econ:.2f} rpo, {dot_pct:.1f}% dots) with {wkts} key breakthroughs across {matches} matches."
            )
        else:
            summary = (
                f"{name} ranks #{rank} with an FBOR of {fbor:.2f}, delivering baseline resilience and dependable defensive containment "
                f"({econ:.2f} rpo across {overs:.1f} overs in {matches} matches)."
            )

        records.append({
            "player_id": pid,
            "player_name": name,
            "role": "bowler",
            "rank": rank,
            "final_rating": fbor,
            "ranking_explanation": summary,
            "key_strengths": "; ".join(strengths),
            "baseline_comparison": base_comp,
            "reliability_summary": rel_summary,
            "pressure_exposure": exposure,
            "ranking_limitations": "; ".join(limitations),
        })

    return pd.DataFrame(records)

