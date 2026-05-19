"""
Integration tests — hit the Flask test client for every endpoint.
"""
import json
import pytest


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_api_index(self, client):
        r = client.get("/api")
        assert r.status_code == 200
        data = r.get_json()
        assert "endpoints" in data
        assert len(data["endpoints"]) >= 10


class TestPrediction:
    def test_predict_positions(self, client, valid_attrs):
        r = client.post("/api/predict/positions",
                        data=json.dumps(valid_attrs),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "predictions" in data
        preds = data["predictions"]
        assert len(preds) == 5
        assert "position" in preds[0]
        assert "confidence" in preds[0]
        # Confidences should sum to ~100
        total = sum(p["confidence"] for p in preds)
        assert 99.0 <= total <= 101.0

    def test_predict_missing_field(self, client):
        r = client.post("/api/predict/positions",
                        data=json.dumps({"pace": 70}),
                        content_type="application/json")
        assert r.status_code == 400
        assert "error" in r.get_json()

    def test_predict_out_of_range(self, client, valid_attrs):
        bad = {**valid_attrs, "pace": 150}
        r = client.post("/api/predict/positions",
                        data=json.dumps(bad),
                        content_type="application/json")
        assert r.status_code == 400

    def test_gap_analysis(self, client, valid_attrs):
        payload = {**valid_attrs, "position": "ST"}
        r = client.post("/api/predict/gap-analysis",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert data["position"] == "ST"
        assert "gaps" in data
        assert "strengths" in data
        assert "weaknesses" in data
        # gaps should have all 10 attributes
        assert len(data["gaps"]) == 10

    def test_gap_analysis_missing_position(self, client, valid_attrs):
        r = client.post("/api/predict/gap-analysis",
                        data=json.dumps(valid_attrs),
                        content_type="application/json")
        assert r.status_code == 400

    def test_full_analysis(self, client, valid_attrs):
        payload = {**valid_attrs, "player_name": "Test Player",
                   "player_age": 22, "save": False}
        r = client.post("/api/predict/full",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "predictions" in data
        assert "gap_analysis" in data
        assert "similar_players" in data
        assert "cluster_info" in data
        assert "training_plan" in data
        assert "overall_rating" in data

    def test_full_analysis_saves_session(self, client, valid_attrs):
        payload = {**valid_attrs, "player_name": "Saved Player",
                   "player_age": 25, "save": True}
        r = client.post("/api/predict/full",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "session_token" in data
        assert len(data["session_token"]) == 36   # UUID format


class TestClustering:
    def test_similar_players(self, client, valid_attrs):
        r = client.post("/api/cluster/similar",
                        data=json.dumps(valid_attrs),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "similar_players" in data
        players = data["similar_players"]
        assert len(players) == 5
        assert "name" in players[0]
        assert "position" in players[0]
        assert "similarity" in players[0]
        assert 0 <= players[0]["similarity"] <= 100

    def test_similar_players_custom_top_n(self, client, valid_attrs):
        payload = {**valid_attrs, "top_n": 3}
        r = client.post("/api/cluster/similar",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 200
        assert len(r.get_json()["similar_players"]) == 3

    def test_cluster_info(self, client, valid_attrs):
        r = client.post("/api/cluster/info",
                        data=json.dumps(valid_attrs),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "cluster_id" in data
        assert "cluster_size" in data
        assert "avg_attributes" in data
        assert "dominant_positions" in data
        assert 0 <= data["cluster_id"] <= 7   # 8 clusters


class TestTraining:
    def test_training_plan(self, client, weak_attrs):
        r = client.post("/api/training/plan",
                        data=json.dumps(weak_attrs),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "gap_analysis" in data
        assert "training_plan" in data
        plan = data["training_plan"]
        assert "drills" in plan
        assert "weekly_plan" in plan
        assert len(plan["weekly_plan"]) == 5   # Mon–Fri

    def test_training_plan_with_position(self, client, weak_attrs):
        payload = {**weak_attrs, "position": "CB"}
        r = client.post("/api/training/plan",
                        data=json.dumps(payload),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert data["gap_analysis"]["position"] == "CB"


class TestAnalytics:
    def test_overview(self, client, valid_attrs):
        r = client.post("/api/analytics/overview",
                        data=json.dumps(valid_attrs),
                        content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "overall_rating" in data
        assert "top_position" in data
        assert "predictions" in data
        assert "gap_analysis" in data
        assert "similar_players" in data
        assert 1 <= data["overall_rating"] <= 99

    def test_position_profiles(self, client):
        r = client.get("/api/analytics/position-profiles")
        assert r.status_code == 200
        data = r.get_json()
        assert "profiles" in data
        profiles = data["profiles"]
        assert len(profiles) == 11
        assert "ST" in profiles
        assert "GK" in profiles
        # Each profile should have all 10 attributes
        for pos, attrs in profiles.items():
            assert len(attrs) == 10


class TestEvaluation:
    def test_all_models(self, client):
        r = client.get("/api/evaluate/models")
        assert r.status_code == 200
        data = r.get_json()
        assert "models" in data
        assert "best_model" in data
        # At least one model should be present
        assert len(data["models"]) >= 1

    def test_specific_model(self, client):
        r = client.get("/api/evaluate/models/knn")
        assert r.status_code == 200
        data = r.get_json()
        assert data["model"] == "knn"
        assert "metrics" in data
        m = data["metrics"]
        assert "accuracy" in m
        assert "f1" in m
        assert 0 < m["accuracy"] < 1

    def test_unknown_model(self, client):
        r = client.get("/api/evaluate/models/nonexistent")
        assert r.status_code == 404

    def test_confusion_matrix(self, client):
        r = client.get("/api/evaluate/confusion-matrix/knn")
        assert r.status_code == 200
        data = r.get_json()
        assert "matrix" in data
        assert "labels" in data
        assert len(data["labels"]) == 11   # 11 positions
        # Matrix should be 11×11
        assert len(data["matrix"]) == 11
        assert len(data["matrix"][0]) == 11


class TestSessions:
    def test_list_sessions_empty(self, client):
        r = client.get("/api/sessions/")
        assert r.status_code == 200
        data = r.get_json()
        assert "sessions" in data
        assert "total" in data

    def test_get_nonexistent_session(self, client):
        r = client.get("/api/sessions/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_session_lifecycle(self, client, valid_attrs):
        # Create a session via full analysis
        payload = {**valid_attrs, "player_name": "Session Test",
                   "player_age": 20, "save": True}
        create_r = client.post("/api/predict/full",
                               data=json.dumps(payload),
                               content_type="application/json")
        assert create_r.status_code == 200
        token = create_r.get_json()["session_token"]

        # Retrieve it
        get_r = client.get(f"/api/sessions/{token}")
        assert get_r.status_code == 200
        session = get_r.get_json()
        assert session["session_token"] == token
        assert session["player_name"] == "Session Test"
        assert session["player_age"] == 20
        assert session["pace"] == valid_attrs["pace"]

        # List should include it
        list_r = client.get("/api/sessions/")
        assert list_r.status_code == 200
        tokens = [s["session_token"] for s in list_r.get_json()["sessions"]]
        assert token in tokens

        # Delete it
        del_r = client.delete(f"/api/sessions/{token}")
        assert del_r.status_code == 200
        assert del_r.get_json()["deleted"] is True

        # Should be gone
        gone_r = client.get(f"/api/sessions/{token}")
        assert gone_r.status_code == 404
