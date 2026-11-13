"""PressureIQ Individual Player Profile & Analytics Service.

Compiles comprehensive individual player dossiers combining Phase 8 ratings,
Phase 5-7 baseline comparisons, situational breakdowns, and Phase 9 bootstrap stability.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from dashboard.services.data_loader import (
    load_batter_ratings,
    load_bowler_ratings,
    load_ranking_components,
    load_ranking_explanations,
    load_batter_categories,
    load_bowler_categories,
    load_batter_situational,
    load_bowler_situational,
    load_bootstrap_results,
    load_stability_results,
    load_player_registry,
)


def get_all_player_names_and_ids() -> List[Dict[str, Any]]:
    """Return list of all eligible players with roles for dropdown selection."""
    bat_df = load_batter_ratings()
    bowl_df = load_bowler_ratings()

    players: Dict[str, Dict[str, Any]] = {}

    if not bat_df.empty:
        for _, r in bat_df.iterrows():
            pid = r["player_id"]
            pname = r["player_name"]
            players[pid] = {
                "player_id": pid,
                "player_name": pname,
                "has_batting": True,
                "has_bowling": False,
                "display_label": f"{pname} (Batter #{r['rank']})",
            }

    if not bowl_df.empty:
        for _, r in bowl_df.iterrows():
            pid = r["player_id"]
            pname = r["player_name"]
            if pid in players:
                players[pid]["has_bowling"] = True
                bat_rank = players[pid]["display_label"].split("#")[-1].replace(")", "")
                players[pid]["display_label"] = f"{pname} (All-Rounder | Bat #{bat_rank}, Bowl #{r['rank']})"
            else:
                players[pid] = {
                    "player_id": pid,
                    "player_name": pname,
                    "has_batting": False,
                    "has_bowling": True,
                    "display_label": f"{pname} (Bowler #{r['rank']})",
                }

    sorted_players = sorted(players.values(), key=lambda x: x["player_name"])
    return sorted_players


def get_player_dossier(player_id: str, role: str = "batting") -> Dict[str, Any]:
    """Retrieve full statistical dossier for a single player in a given role."""
    is_batting = role.lower() == "batting"

    ratings_df = load_batter_ratings() if is_batting else load_bowler_ratings()
    bootstrap_df = load_bootstrap_results("batting" if is_batting else "bowling")
    stability_df = load_stability_results("batting" if is_batting else "bowling")
    cats_df = load_batter_categories() if is_batting else load_bowler_categories()
    sit_df = load_batter_situational() if is_batting else load_bowler_situational()
    comps_df = load_ranking_components()
    registry = load_player_registry()

    # 1. Rating Record
    player_row = ratings_df[ratings_df["player_id"] == player_id]
    if player_row.empty:
        return {}
    r = player_row.iloc[0].to_dict()

    # 2. Registry info
    reg_row = registry[registry["player_id"] == player_id] if not registry.empty else pd.DataFrame()
    comp_coverage = "IPL & T20I" if reg_row.empty else reg_row.iloc[0].get("competitions", "IPL & T20I")

    # 3. Bootstrap Uncertainty Record
    boot_row = bootstrap_df[bootstrap_df["player_id"] == player_id] if not bootstrap_df.empty else pd.DataFrame()
    boot_data = boot_row.iloc[0].to_dict() if not boot_row.empty else {}

    # 4. Stability Record
    stab_row = stability_df[stability_df["player_id"] == player_id] if not stability_df.empty else pd.DataFrame()
    stab_data = stab_row.iloc[0].to_dict() if not stab_row.empty else {}

    # 5. Pressure Category Metrics
    player_cats = cats_df[cats_df["player_id"] == player_id] if not cats_df.empty else pd.DataFrame()

    # 6. Situational Metrics
    player_sit = sit_df[sit_df["player_id"] == player_id] if not sit_df.empty else pd.DataFrame()

    # 7. Component Scores (0-100)
    p_comp = comps_df[comps_df["player_id"] == player_id] if not comps_df.empty else pd.DataFrame()
    comp_data = p_comp.iloc[0].to_dict() if not p_comp.empty else {}

    return {
        "player_id": player_id,
        "player_name": r.get("player_name", "Unknown Player"),
        "role": "Batter" if is_batting else "Bowler",
        "competition_coverage": comp_coverage,
        "rating_record": r,
        "bootstrap_data": boot_data,
        "stability_data": stab_data,
        "category_metrics": player_cats,
        "situational_metrics": player_sit,
        "component_scores": comp_data,
    }

