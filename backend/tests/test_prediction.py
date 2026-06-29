"""
Unit tests for the prediction service and controller.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import pytest
from backend.services.prediction_service import predict_positions, gap_analysis, POSITION_PROFILES
from backend.controllers.prediction_controller import handle_predict, handle_gap_analysis


SAMPLE = {
    "pace": 80, "shooting": 85, "passing": 65, "dribbling": 75,
    "defending": 28, "physical": 72, "stamina": 74,
    "strength": 70, "agility": 78, "vision": 68,
}


class TestPredictionService:
    def test_returns_five_predictions(self):
        preds = predict_positions(SAMPLE, top_n=5)
        assert len(preds) == 5

    def test_prediction_structure(self):
        preds = predict_positions(SAMPLE)
        for p in preds:
            assert "position" in p
            assert "confidence" in p
            assert isinstance(p["confidence"], float)
            assert 0 <= p["confidence"] <= 100

    def test_confidences_sum_to_100(self):
        preds = predict_positions(SAMPLE)
        total = sum(p["confidence"] for p in preds)
        assert abs(total - 100.0) < 0.5

    def test_sorted_descending(self):
        preds = predict_positions(SAMPLE)
        confs = [p["confidence"] for p in preds]
        assert confs == sorted(confs, reverse=True)

    def test_top_n_respected(self):
        for n in [1, 3, 5]:
            preds = predict_positions(SAMPLE, top_n=n)
            assert len(preds) == n

    def test_known_striker_profile(self):
        """A player with high shooting/pace should rank ST or CF highly."""
        striker = {
            "pace": 88, "shooting": 90, "passing": 60, "dribbling": 75,
            "defending": 25, "physical": 75, "stamina": 72,
            "strength": 72, "agility": 74, "vision": 62,
        }
        preds = predict_positions(striker, top_n=3)
        top_positions = [p["position"] for p in preds]
        assert any(p in top_positions for p in ["ST", "CF", "LW", "RW"])

    def test_known_goalkeeper_profile(self):
        """
        A GK-like profile should rank GK in the top 2 positions.
        Key GK signatures from real data: very low stamina, dribbling, agility, vision.
        High defending and physical. These are the attributes derived from GK sub-stats.
        """
        gk = {
            "pace":    50,   # GK median ~50
            "shooting":60,   # GK median ~60 (from gk_kicking)
            "passing": 58,   # GK median ~59 (from gk_kicking)
            "dribbling":35,  # GK median ~36 — very low (movement_agility)
            "defending":62,  # GK median ~62 (from gk_positioning + reflexes)
            "physical": 60,  # GK median ~60 (power_strength)
            "stamina":  28,  # GK median ~28 — extremely low (power_stamina)
            "strength": 60,  # GK median ~60
            "agility":  35,  # GK median ~36 — very low
            "vision":   34,  # GK median ~34 — very low
        }
        preds = predict_positions(gk, top_n=2)
        top_positions = [p["position"] for p in preds]
        assert "GK" in top_positions


class TestGapAnalysis:
    def test_gap_analysis_structure(self):
        result = gap_analysis(SAMPLE, "ST")
        assert result["position"] == "ST"
        assert "gaps" in result
        assert "strengths" in result
        assert "weaknesses" in result

    def test_all_attributes_in_gaps(self):
        result = gap_analysis(SAMPLE, "ST")
        expected = {"pace","shooting","passing","dribbling","defending",
                    "physical","stamina","strength","agility","vision"}
        assert set(result["gaps"].keys()) == expected

    def test_gap_values_correct(self):
        # Use POSITION_PROFILES to get the actual ideal value dynamically
        # so this test stays correct regardless of profile source
        st_ideal_shooting = POSITION_PROFILES["ST"]["shooting"]
        attrs = {
            "pace": 78, "shooting": st_ideal_shooting,
            "passing": 60, "dribbling": 72,
            "defending": 30, "physical": 72, "stamina": 72,
            "strength": 72, "agility": 72, "vision": 65,
        }
        result = gap_analysis(attrs, "ST")
        # Player shooting == ideal shooting → gap must be 0
        assert result["gaps"]["shooting"]["gap"] == 0

    def test_weakness_threshold(self):
        """Player with pace=50 vs ST ideal=78 → deficit=28 → should be a weakness."""
        low_pace = {**SAMPLE, "pace": 50}
        result = gap_analysis(low_pace, "ST")
        weakness_attrs = [w["attribute"] for w in result["weaknesses"]]
        assert "pace" in weakness_attrs

    def test_strength_threshold(self):
        """Player with shooting=95 vs ST ideal=85 → surplus=10 → should be a strength."""
        high_shoot = {**SAMPLE, "shooting": 95}
        result = gap_analysis(high_shoot, "ST")
        strength_attrs = [s["attribute"] for s in result["strengths"]]
        assert "shooting" in strength_attrs

    def test_all_positions_valid(self):
        for pos in POSITION_PROFILES:
            result = gap_analysis(SAMPLE, pos)
            assert result["position"] == pos
            assert len(result["gaps"]) == 10

    def test_unknown_position_returns_empty(self):
        result = gap_analysis(SAMPLE, "UNKNOWN")
        assert result["gaps"] == {}
        assert result["strengths"] == []
        assert result["weaknesses"] == []


class TestPredictionController:
    def test_handle_predict_wraps_correctly(self):
        result = handle_predict(SAMPLE)
        assert "predictions" in result
        assert len(result["predictions"]) == 5

    def test_handle_gap_analysis(self):
        result = handle_gap_analysis(SAMPLE, "ST")
        assert result["position"] == "ST"
        assert "gaps" in result
