"""Tests for URL scanner platform detection."""
import pytest


class TestUrlScanner:
    """Test platform detection from URLs."""

    def test_detect_instagram(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://www.instagram.com/natgeo"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "instagram"

    def test_detect_twitter(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://twitter.com/elonmusk"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "twitter"

    def test_detect_x_dot_com(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://x.com/elonmusk"})
        assert resp.status_code == 200
        assert resp.json()["platform"] == "twitter"

    def test_detect_facebook(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://facebook.com/zuck"})
        assert resp.status_code == 200
        assert resp.json()["platform"] == "facebook"

    def test_detect_linkedin(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://linkedin.com/in/satyanadella"})
        assert resp.status_code == 200
        assert resp.json()["platform"] == "linkedin"

    def test_detect_youtube(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://youtube.com/@mkbhd"})
        assert resp.status_code == 200
        assert resp.json()["platform"] == "youtube"

    def test_unknown_url_returns_400(self, client):
        resp = client.post("/api/scan/url", json={"url": "https://example.com/user123"})
        assert resp.status_code == 400

    def test_reddit_url_triggers_scan(self, client):
        # Reddit should attempt auto-fetch — may get 404 for fake user,
        # but the platform detection itself should work
        resp = client.post("/api/scan/url", json={"url": "https://reddit.com/user/spez"})
        # Either 200 (found) or 404/500 (user not found / network) — but not 400
        assert resp.status_code != 400


class TestModelComparison:
    def test_returns_evaluation_data(self, client):
        resp = client.get("/api/models/comparison")
        assert resp.status_code == 200
        data = resp.json()
        assert "available" in data
        if data["available"]:
            assert "data" in data
