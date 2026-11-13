"""Tests for player dossier compilation and dual-role handling."""

from __future__ import annotations
import pytest
from dashboard.services.player_service import get_all_player_names_and_ids, get_player_dossier


def test_get_all_player_names_and_ids():
    """Verify player dropdown catalog contains eligible batters and bowlers without duplicates."""
    players = get_all_player_names_and_ids()
    assert len(players) > 200
    ids = [p["player_id"] for p in players]
    assert len(ids) == len(set(ids)), "Player IDs in dropdown must be strictly unique"


def test_get_player_dossier_batter():
    """Verify loading dossier for top batter contains complete statistics."""
    players = get_all_player_names_and_ids()
    rinku = [p for p in players if "Rinku Singh" in p["player_name"]][0]
    dossier = get_player_dossier(rinku["player_id"], role="batting")

    assert dossier["player_name"] == "Rinku Singh"
    assert dossier["role"] == "Batter"
    r = dossier["rating_record"]
    assert r["rank"] == 1
    assert "strike_rate" in r
    assert "bppi" in r
    assert "final_fbpr" in r
    assert "ci_lower_fbpr" in r
    assert "ci_upper_fbpr" in r


def test_get_player_dossier_bowler():
    """Verify loading dossier for top bowler contains complete statistics."""
    players = get_all_player_names_and_ids()
    little = [p for p in players if "Joshua Little" in p["player_name"]][0]
    dossier = get_player_dossier(little["player_id"], role="bowling")

    assert dossier["player_name"] == "Joshua Little"
    assert dossier["role"] == "Bowler"
    r = dossier["rating_record"]
    assert r["rank"] == 1
    assert "economy_rate" in r
    assert "bppi_b" in r
    assert "final_fbor" in r

