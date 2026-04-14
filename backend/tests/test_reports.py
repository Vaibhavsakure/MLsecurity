"""Tests for PDF report generation and download endpoints."""
import pytest


SAMPLE_REPORT = {
    "platform": "instagram",
    "probability": 0.85,
    "risk_level": "high",
    "label": "High Risk",
    "message": "High probability of being a fake or bot account.",
    "input_data": {
        "profile_pic": 0,
        "username_has_numbers": 1,
        "bio_present": 0,
        "posts": 0,
        "followers": 0,
        "following": 5000,
    },
    "feature_importances": [
        {"feature": "Followers", "value": -0.2345},
        {"feature": "Following", "value": 0.5678},
        {"feature": "Profile Pic", "value": -0.1234},
    ],
}


class TestReportGeneration:
    def test_generate_report_returns_token(self, client):
        resp = client.post("/api/report/generate", json=SAMPLE_REPORT)
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert "filename" in data
        assert data["filename"].endswith(".pdf")

    def test_download_report_returns_pdf(self, client):
        # Generate
        gen_resp = client.post("/api/report/generate", json=SAMPLE_REPORT)
        token = gen_resp.json()["token"]

        # Download
        dl_resp = client.get(f"/api/report/download/{token}")
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "application/pdf"
        assert "Content-Disposition" in dl_resp.headers

    def test_download_expired_token_returns_404(self, client):
        resp = client.get("/api/report/download/nonexistent-token-12345")
        assert resp.status_code == 404

    def test_token_is_single_use(self, client):
        """After downloading once, the same token should return 404."""
        gen_resp = client.post("/api/report/generate", json=SAMPLE_REPORT)
        token = gen_resp.json()["token"]

        # First download succeeds
        dl_resp1 = client.get(f"/api/report/download/{token}")
        assert dl_resp1.status_code == 200

        # Second download fails (token consumed)
        dl_resp2 = client.get(f"/api/report/download/{token}")
        assert dl_resp2.status_code == 404

    def test_report_with_timestamp(self, client):
        payload = {**SAMPLE_REPORT, "timestamp": "2026-04-14 12:00:00"}
        resp = client.post("/api/report/generate", json=payload)
        assert resp.status_code == 200


class TestBatchReport:
    def test_batch_report_returns_token(self, client):
        reports = [SAMPLE_REPORT, {**SAMPLE_REPORT, "platform": "twitter"}]
        resp = client.post("/api/report/batch", json=reports)
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["filename"].endswith(".zip")

    def test_batch_download_returns_zip(self, client):
        reports = [SAMPLE_REPORT]
        gen_resp = client.post("/api/report/batch", json=reports)
        token = gen_resp.json()["token"]

        dl_resp = client.get(f"/api/report/download-zip/{token}")
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "application/zip"

    def test_batch_zip_expired_token(self, client):
        resp = client.get("/api/report/download-zip/fake-token-99999")
        assert resp.status_code == 404
