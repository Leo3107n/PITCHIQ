"""
Unit tests for the clustering service and controller.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import pytest
from backend.services.clustering_service import get_similar_players, get_cluster
from backend.controllers.clustering_controller import (
    handle_similar_players, handle_cluster_info
)

SAMPLE = {
    "pace": 80, "shooting": 85, "passing": 65, "dribbling": 75,
    "defending": 28, "physical": 72, "stamina": 74,
    "strength": 70, "agility": 78, "vision": 68,
}


class TestSimilarPlayers:
    def test_returns_correct_count(self):
        for n in [1, 3, 5, 10]:
            result = get_similar_players(SAMPLE, top_n=n)
            assert len(result) == n

    def test_player_structure(self):
        players = get_similar_players(SAMPLE, top_n=3)
        for p in players:
            assert "name" in p
            assert "position" in p
            assert "similarity" in p
            assert 0 <= p["similarity"] <= 100

    def test_sorted_by_similarity(self):
        players = get_similar_players(SAMPLE, top_n=5)
        sims = [p["similarity"] for p in players]
        assert sims == sorted(sims, reverse=True)

    def test_similarity_range(self):
        players = get_similar_players(SAMPLE, top_n=5)
        for p in players:
            assert 0 <= p["similarity"] <= 100

    def test_attributes_present(self):
        players = get_similar_players(SAMPLE, top_n=1)
        attrs = ["pace","shooting","passing","dribbling","defending",
                 "physical","stamina","strength","agility","vision"]
        for attr in attrs:
            assert attr in players[0]


class TestClusterInfo:
    def test_cluster_structure(self):
        result = get_cluster(SAMPLE)
        assert "cluster_id" in result
        assert "cluster_size" in result
        assert "avg_attributes" in result
        assert "dominant_positions" in result

    def test_cluster_id_valid(self):
        result = get_cluster(SAMPLE)
        assert 0 <= result["cluster_id"] <= 7   # 8 clusters

    def test_cluster_size_positive(self):
        result = get_cluster(SAMPLE)
        assert result["cluster_size"] > 0

    def test_avg_attributes_complete(self):
        result = get_cluster(SAMPLE)
        expected = {"pace","shooting","passing","dribbling","defending",
                    "physical","stamina","strength","agility","vision"}
        assert set(result["avg_attributes"].keys()) == expected

    def test_dominant_positions_not_empty(self):
        result = get_cluster(SAMPLE)
        assert len(result["dominant_positions"]) >= 1

    def test_different_profiles_different_clusters(self):
        """A GK-like player should land in a different cluster than a striker."""
        gk = {
            "pace": 38, "shooting": 12, "passing": 48, "dribbling": 28,
            "defending": 18, "physical": 68, "stamina": 55,
            "strength": 62, "agility": 42, "vision": 44,
        }
        striker_cluster = get_cluster(SAMPLE)["cluster_id"]
        gk_cluster      = get_cluster(gk)["cluster_id"]
        assert striker_cluster != gk_cluster


class TestClusteringController:
    def test_handle_similar_players(self):
        result = handle_similar_players(SAMPLE, top_n=3)
        assert "similar_players" in result
        assert len(result["similar_players"]) == 3

    def test_handle_cluster_info(self):
        result = handle_cluster_info(SAMPLE)
        assert "cluster_id" in result
