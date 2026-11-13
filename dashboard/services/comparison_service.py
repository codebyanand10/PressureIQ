"""PressureIQ Multi-Player Head-to-Head Comparison Service.

Enables side-by-side comparison of 2 to 4 players (Batters vs Batters or Bowlers vs Bowlers).
Provides normalized multi-axis radar charts and grouped performance comparisons.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from dashboard.services.data_loader import load_batter_ratings, load_bowler_ratings


def compare_batters(player_ids: List[str]) -> Dict[str, Any]:
    """Compile comparative metrics for 2-4 selected batters."""
    df = load_batter_ratings()
    if df.empty:
        return {}

    selected = df[df["player_id"].isin(player_ids)].copy()
    if selected.empty:
        return {}

    # Sort selected in order of player_ids passed
    selected["sort_order"] = selected["player_id"].map({pid: i for i, pid in enumerate(player_ids)})
    selected = selected.sort_values("sort_order")

    # Normalized radar metrics (0-100)
    # 1. FBPR (Rating)
    # 2. Strike Rate (80 -> 0, 200 -> 100)
    # 3. BPPI (Baseline retention)
    # 4. Boundary Efficiency
    # 5. Dot Ball Control (inverted dot %)
    # 6. Sample Depth (balls faced clipped at 150)
    radar_data: List[Dict[str, Any]] = []
    for _, r in selected.iterrows():
        sr_norm = float(np.clip((r["strike_rate"] - 80) / (200 - 80) * 100, 0, 100))
        dot_norm = float(np.clip((60 - r["dot_ball_percentage"]) / (60 - 20) * 100, 0, 100))
        sample_norm = float(np.clip(r["balls_faced"] / 150 * 100, 0, 100))
        bppi_norm = float(np.clip(r["bppi"], 0, 100))

        radar_data.append({
            "player_name": r["player_name"],
            "metrics": {
                "Pressure Rating (FBPR)": float(r["final_fbpr"]),
                "Strike Rate": sr_norm,
                "Baseline Retention (BPPI)": bppi_norm,
                "Boundary Efficiency": float(r.get("score_boundary_efficiency", 50.0)),
                "Dot Ball Control": dot_norm,
                "Sample Depth": sample_norm,
            },
        })

    return {
        "players_df": selected,
        "radar_data": radar_data,
        "role": "batting",
    }


def compare_bowlers(player_ids: List[str]) -> Dict[str, Any]:
    """Compile comparative metrics for 2-4 selected bowlers."""
    df = load_bowler_ratings()
    if df.empty:
        return {}

    selected = df[df["player_id"].isin(player_ids)].copy()
    if selected.empty:
        return {}

    selected["sort_order"] = selected["player_id"].map({pid: i for i, pid in enumerate(player_ids)})
    selected = selected.sort_values("sort_order")

    # Normalized radar metrics (0-100)
    # 1. FBOR (Rating)
    # 2. Economy Control (inverted: 13.0 -> 0, 6.0 -> 100)
    # 3. BPPI-B (Baseline retention)
    # 4. Wicket Taking (Wicket score)
    # 5. Dot Ball Generation (20% -> 0, 60% -> 100)
    # 6. Sample Depth (balls bowled clipped at 120)
    radar_data: List[Dict[str, Any]] = []
    for _, r in selected.iterrows():
        econ_norm = float(np.clip((13.0 - r["economy_rate"]) / (13.0 - 6.0) * 100, 0, 100))
        dot_norm = float(np.clip((r["dot_ball_percentage"] - 20) / (60 - 20) * 100, 0, 100))
        sample_norm = float(np.clip(r["legal_balls_bowled"] / 120 * 100, 0, 100))
        bppi_norm = float(np.clip(r["bppi_b"], 0, 100))

        radar_data.append({
            "player_name": r["player_name"],
            "metrics": {
                "Pressure Rating (FBOR)": float(r["final_fbor"]),
                "Economy Control": econ_norm,
                "Baseline Retention (BPPI-B)": bppi_norm,
                "Wicket Taking": float(r.get("score_wicket_taking", 50.0)),
                "Dot Ball Generation": dot_norm,
                "Sample Depth": sample_norm,
            },
        })

    return {
        "players_df": selected,
        "radar_data": radar_data,
        "role": "bowling",
    }

