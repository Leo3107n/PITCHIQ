"""
Unit and integration tests for the AI scouting report feature.
The OpenAI client is fully mocked — no real API calls are made.
"""
import sys, os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import pytest
from unittest.mock import patch, MagicMock

# ── Shared fixtures ────────────────────────────────────────────────────────────

VALID_ATTRS = {
    "pace": 75, "shooting": 80, "passing": 65,
    "dribbling": 72, "defending": 30, "physical": 70,
    "stamina": 72, "strength": 68, "agility": 74, "vision": 66,
}

MOCK_PREDICTIONS = [
    {"position": "ST", "confidence": 74.6},
    {"position": "CF", "confidence": 10.0},
    {"position": "LW", "confidence": 8.0},
]

MOCK_GAP = {
    "position": "ST",
    "gaps": {
        "pace":      {"player": 75, "ideal": 75, "gap": 0},
        "shooting":  {"player": 80, "ideal": 68, "gap": 12},
        "passing":   {"player": 65, "ideal": 57, "gap": 8},
        "dribbling": {"player": 72, "ideal": 67, "gap": 5},
        "defending": {"player": 30, "ideal": 34, "gap": -4},
        "physical":  {"player": 70, "ideal": 70, "gap": 0},
        "stamina":   {"player": 72, "ideal": 69, "gap": 3},
        "strength":  {"player": 68, "ideal": 77, "gap": -9},
        "agility":   {"player": 74, "ideal": 72, "gap": 2},
        "vision":    {"player": 66, "ideal": 60, "gap": 6},
    },
    "strengths":  [{"attribute": "shooting", "value": 80, "ideal": 68, "surplus": 12}],
    "weaknesses": [{"attribute": "strength", "value": 68, "ideal": 77, "deficit": 9}],
}

MOCK_SIMILAR = [
    {"name": "T. Chevalier", "position": "ST", "similarity": 97.4},
]

FULL_PAYLOAD = {
    **VALID_ATTRS,
    "player_name":    "Carlos Silva",
    "player_age":     22,
    "predictions":    MOCK_PREDICTIONS,
    "gap_analysis":   MOCK_GAP,
    "similar_players": MOCK_SIMILAR,
}

MOCK_REPORT = (
    "Carlos Silva projects as a natural striker whose shooting and vision "
    "give him an immediate edge in the final third.\n\n"
    "His primary strength is his clinical finishing — an 80 shooting rating "
    "puts him well above the ideal for the position.\n\n"
    "To reach his potential, Carlos should prioritise strength training, "
    "focusing on resistance work to improve his 68 rating toward the 77 ideal."
)


# ── Service-level tests (prompt building + API call) ─────────────────────────

class TestPromptBuilding:
    def test_prompt_contains_player_name(self):
        from backend.services.scouting_service import _build_prompt
        ctx = {**FULL_PAYLOAD, "attributes": VALID_ATTRS,
               "predictions": MOCK_PREDICTIONS, "gap_analysis": MOCK_GAP,
               "similar_players": MOCK_SIMILAR}
        prompt = _build_prompt(ctx)
        assert "Carlos Silva" in prompt

    def test_prompt_contains_top_position(self):
        from backend.services.scouting_service import _build_prompt
        ctx = {"attributes": VALID_ATTRS, "predictions": MOCK_PREDICTIONS,
               "gap_analysis": MOCK_GAP, "similar_players": MOCK_SIMILAR}
        prompt = _build_prompt(ctx)
        assert "ST" in prompt
        assert "Striker" in prompt

    def test_prompt_contains_strengths(self):
        from backend.services.scouting_service import _build_prompt
        ctx = {"attributes": VALID_ATTRS, "predictions": MOCK_PREDICTIONS,
               "gap_analysis": MOCK_GAP, "similar_players": MOCK_SIMILAR}
        prompt = _build_prompt(ctx)
        assert "shooting" in prompt

    def test_prompt_contains_weaknesses(self):
        from backend.services.scouting_service import _build_prompt
        ctx = {"attributes": VALID_ATTRS, "predictions": MOCK_PREDICTIONS,
               "gap_analysis": MOCK_GAP, "similar_players": MOCK_SIMILAR}
        prompt = _build_prompt(ctx)
        assert "strength" in prompt

    def test_prompt_works_without_optional_fields(self):
        """Missing player_name, player_age, similar_players — should not crash."""
        from backend.services.scouting_service import _build_prompt
        ctx = {"attributes": VALID_ATTRS, "predictions": MOCK_PREDICTIONS,
               "gap_analysis": MOCK_GAP}
        prompt = _build_prompt(ctx)
        assert "ST" in prompt
        assert len(prompt) > 100


class TestScoutingService:
    def test_missing_api_key_raises_error(self):
        from backend.services.scouting_service import generate_scouting_report, ScoutingReportError
        from backend.config import Config
        original = Config.OPENAI_API_KEY
        try:
            Config.OPENAI_API_KEY = ""
            with pytest.raises(ScoutingReportError) as exc_info:
                generate_scouting_report({
                    "attributes": VALID_ATTRS,
                    "predictions": MOCK_PREDICTIONS,
                    "gap_analysis": MOCK_GAP,
                })
            assert exc_info.value.retry is False
        finally:
            Config.OPENAI_API_KEY = original

    def test_successful_generation(self):
        from backend.services.scouting_service import generate_scouting_report
        from backend.config import Config
        if not Config.OPENAI_API_KEY:
            pytest.skip("No API key configured")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_REPORT

        with patch("openai.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            result = generate_scouting_report({
                "attributes": VALID_ATTRS,
                "predictions": MOCK_PREDICTIONS,
                "gap_analysis": MOCK_GAP,
                "similar_players": MOCK_SIMILAR,
                "player_name": "Carlos Silva",
                "player_age": 22,
            })
            assert "Carlos Silva" in result or len(result) > 50

    def test_empty_response_raises_error(self):
        from backend.services.scouting_service import generate_scouting_report, ScoutingReportError
        from backend.config import Config
        if not Config.OPENAI_API_KEY:
            pytest.skip("No API key configured")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""

        with patch("backend.services.scouting_service.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            with pytest.raises(ScoutingReportError):
                generate_scouting_report({
                    "attributes": VALID_ATTRS,
                    "predictions": MOCK_PREDICTIONS,
                    "gap_analysis": MOCK_GAP,
                })


# ── Route-level integration tests ─────────────────────────────────────────────

class TestScoutingRoutes:
    def test_missing_attributes_returns_400(self, client):
        payload = {
            "predictions": MOCK_PREDICTIONS,
            "gap_analysis": MOCK_GAP,
            # no attributes
        }
        r = client.post("/api/scouting/report",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 400

    def test_missing_predictions_returns_400(self, client):
        payload = {**VALID_ATTRS, "gap_analysis": MOCK_GAP}
        r = client.post("/api/scouting/report",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 400
        assert "predictions" in r.get_json()["error"].lower()

    def test_missing_gap_analysis_returns_400(self, client):
        payload = {**VALID_ATTRS, "predictions": MOCK_PREDICTIONS}
        r = client.post("/api/scouting/report",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 400
        assert "gap_analysis" in r.get_json()["error"].lower()

    def test_no_api_key_returns_502(self, client):
        """Without a configured API key, the route should return 502 with a clean message."""
        from backend.config import Config
        original = Config.OPENAI_API_KEY
        try:
            Config.OPENAI_API_KEY = ""
            payload = {**FULL_PAYLOAD}
            r = client.post("/api/scouting/report",
                            data=json.dumps(payload),
                            content_type="application/json")
            assert r.status_code == 502
            data = r.get_json()
            assert "error" in data
            assert data.get("retry") is False
        finally:
            Config.OPENAI_API_KEY = original

    def test_success_returns_report(self, client):
        """Mocked OpenAI — verifies the route returns 200 with a report string."""
        from backend.config import Config
        if not Config.OPENAI_API_KEY:
            pytest.skip("No API key configured")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_REPORT

        with patch("backend.services.scouting_service.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            r = client.post("/api/scouting/report",
                            data=json.dumps(FULL_PAYLOAD),
                            content_type="application/json")
            assert r.status_code == 200
            data = r.get_json()
            assert "report" in data
            assert len(data["report"]) > 50

    def test_llm_failure_returns_502_with_retry(self, client):
        """Simulates an API timeout — should return 502 with retry=True."""
        from backend.config import Config
        if not Config.OPENAI_API_KEY:
            pytest.skip("No API key configured")

        with patch("backend.services.scouting_service.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            from openai import APITimeoutError
            mock_client.chat.completions.create.side_effect = APITimeoutError(
                request=MagicMock()
            )

            r = client.post("/api/scouting/report",
                            data=json.dumps(FULL_PAYLOAD),
                            content_type="application/json")
            assert r.status_code == 502
            assert r.get_json().get("retry") is True

    def test_get_saved_report_missing_session_returns_404(self, client):
        r = client.get("/api/scouting/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404
