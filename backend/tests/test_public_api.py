"""
Tests for the Public API v1 — key management and prediction endpoints.
Covers: key generation, listing, revocation, prediction routing, and rate limit headers.
"""
import pytest


# ---------------------------------------------------------------------------
# API Key Management
# ---------------------------------------------------------------------------
class TestKeyManagement:
    def test_generate_key(self, client):
        """Generating a key returns a key string with the sg_ prefix."""
        resp = client.post("/api/v1/keys/generate", params={"name": "Test Key"})
        assert resp.status_code == 200
        data = resp.json()
        assert "key" in data
        assert data["key"].startswith("sg_")
        assert data["name"] == "Test Key"

    def test_generate_key_default_name(self, client):
        """Key generation works without a name param."""
        resp = client.post("/api/v1/keys/generate")
        assert resp.status_code == 200
        assert resp.json()["key"].startswith("sg_")

    def test_list_keys(self, client):
        """After generating a key, list endpoint returns at least one entry."""
        client.post("/api/v1/keys/generate", params={"name": "List Test"})
        resp = client.get("/api/v1/keys/list")
        assert resp.status_code == 200
        keys = resp.json()
        assert isinstance(keys, list)
        assert len(keys) >= 1

    def test_list_keys_are_masked(self, client):
        """Listed keys should be masked (key_preview), not full strings."""
        client.post("/api/v1/keys/generate", params={"name": "Mask Test"})
        resp = client.get("/api/v1/keys/list")
        for entry in resp.json():
            assert "key_preview" in entry
            assert "..." in entry["key_preview"]
            assert "key" not in entry or entry.get("key") is None  # full key not exposed

    def test_revoke_key(self, client):
        """Revoking a key removes it; revoking again returns 404."""
        gen = client.post("/api/v1/keys/generate", params={"name": "Revoke Test"})
        key = gen.json()["key"]

        # Revoke it
        resp = client.delete("/api/v1/keys/revoke", params={"key": key})
        assert resp.status_code == 200
        assert resp.json()["status"] == "revoked"

        # Revoke again → 404
        resp2 = client.delete("/api/v1/keys/revoke", params={"key": key})
        assert resp2.status_code == 404

    def test_list_platforms(self, client):
        """Platform list returns all 6 supported platforms."""
        resp = client.get("/api/v1/platforms")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data["platforms"]) == {
            "instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"
        }


# ---------------------------------------------------------------------------
# Public Prediction Endpoint
# ---------------------------------------------------------------------------
class TestPublicPredict:
    def _get_key(self, client) -> str:
        resp = client.post("/api/v1/keys/generate", params={"name": "Predict Test"})
        return resp.json()["key"]

    def test_instagram_prediction_with_valid_key(self, client):
        key = self._get_key(client)
        resp = client.post(
            "/api/v1/analyze/instagram",
            json={
                "profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
                "posts": 42, "followers": 1500, "following": 800,
            },
            headers={"X-API-Key": key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "probability" in data
        assert "risk_level" in data
        assert "confidence" in data
        assert data["platform"] == "instagram"

    def test_invalid_api_key_returns_401(self, client):
        resp = client.post(
            "/api/v1/analyze/instagram",
            json={
                "profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
                "posts": 10, "followers": 100, "following": 50,
            },
            headers={"X-API-Key": "sg_invalid_key_xyz"},
        )
        assert resp.status_code == 401

    def test_missing_api_key_returns_401(self, client):
        resp = client.post(
            "/api/v1/analyze/instagram",
            json={
                "profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
                "posts": 10, "followers": 100, "following": 50,
            },
        )
        assert resp.status_code == 401

    def test_unknown_platform_returns_400(self, client):
        key = self._get_key(client)
        resp = client.post(
            "/api/v1/analyze/tiktok",
            json={"any": "field"},
            headers={"X-API-Key": key},
        )
        assert resp.status_code == 400

    def test_invalid_payload_returns_422(self, client):
        key = self._get_key(client)
        resp = client.post(
            "/api/v1/analyze/instagram",
            json={"profile_pic": 99},  # Missing required fields
            headers={"X-API-Key": key},
        )
        assert resp.status_code == 422

    def test_response_does_not_expose_feature_importances(self, client):
        """Public API returns trimmed response — no SHAP internals exposed."""
        key = self._get_key(client)
        resp = client.post(
            "/api/v1/analyze/instagram",
            json={
                "profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
                "posts": 42, "followers": 1500, "following": 800,
            },
            headers={"X-API-Key": key},
        )
        data = resp.json()
        assert "feature_importances" not in data
        assert "input_data" not in data

    def test_api_key_request_counter_increments(self, client):
        key = self._get_key(client)
        payload = {
            "profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
            "posts": 5, "followers": 200, "following": 100,
        }
        headers = {"X-API-Key": key}
        client.post("/api/v1/analyze/instagram", json=payload, headers=headers)
        client.post("/api/v1/analyze/instagram", json=payload, headers=headers)

        # Check the request count incremented
        key_list = client.get("/api/v1/keys/list").json()
        found = next(
            (k for k in key_list if k["key_preview"].startswith(key[:12])), None
        )
        assert found is not None
        assert found["requests"] >= 2
