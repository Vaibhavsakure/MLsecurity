"""Tests for prediction endpoints — valid input, edge cases, and synthetic data markers."""
import pytest


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------
class TestInstagram:
    def test_valid_prediction(self, client):
        payload = {
            "profile_pic": 1,
            "username_has_numbers": 0,
            "bio_present": 1,
            "posts": 42,
            "followers": 1500,
            "following": 800,
        }
        resp = client.post("/api/predict/instagram", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert 0 <= data["probability"] <= 1
        assert data["risk_level"] in ("low", "medium", "high")
        assert data["platform"] == "instagram"
        assert data["data_source"] == "real_world"
        assert "feature_importances" in data
        assert "confidence" in data

    def test_fake_profile_signals(self, client):
        """No pic, numbers in username, no bio, no posts → should trend higher risk."""
        payload = {
            "profile_pic": 0,
            "username_has_numbers": 1,
            "bio_present": 0,
            "posts": 0,
            "followers": 0,
            "following": 5000,
        }
        resp = client.post("/api/predict/instagram", json=payload)
        assert resp.status_code == 200
        assert resp.json()["probability"] > 0.3  # Should not be low risk


# ---------------------------------------------------------------------------
# Twitter
# ---------------------------------------------------------------------------
class TestTwitter:
    def test_valid_prediction(self, client):
        payload = {
            "statuses_count": 3200,
            "followers_count": 500,
            "friends_count": 300,
            "favourites_count": 1200,
            "listed_count": 10,
            "verified": 0,
            "default_profile_image": 0,
            "geo_enabled": 1,
            "has_bg_image": 1,
            "has_bg_tile": 0,
            "utc_offset": -18000,
            "protected": 0,
        }
        resp = client.post("/api/predict/twitter", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "twitter"
        assert data["data_source"] == "real_world"

    def test_optional_twitter_fields_have_defaults(self, client):
        """Omitting optional Twitter fields should use sensible defaults."""
        payload = {
            "statuses_count": 100,
            "followers_count": 50,
            "friends_count": 100,
            "favourites_count": 200,
            "listed_count": 2,
            "verified": 0,
            "default_profile_image": 1,
            # geo_enabled, has_bg_image, has_bg_tile, utc_offset, protected omitted
        }
        resp = client.post("/api/predict/twitter", json=payload)
        assert resp.status_code == 200
        assert 0 <= resp.json()["probability"] <= 1


# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------
class TestReddit:
    def test_valid_prediction(self, client):
        payload = {
            "account_age_days": 365,
            "user_karma": 5000,
            "sentiment_score": 0.15,
            "avg_word_length": 5.2,
            "contains_links": 0,
        }
        resp = client.post("/api/predict/reddit", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "reddit"
        assert data["data_source"] == "real_world"


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------
class TestFacebook:
    def test_valid_prediction(self, client):
        payload = {
            "friends": 500,
            "following": 200,
            "community": 10,
            "age": 3.5,
            "postshared": 100,
            "urlshared": 20,
            "photos_videos": 30,
            "fpurls": 0.2,
            "fpphotos_videos": 0.5,
            "avgcomment_per_post": 2.5,
            "likes_per_post": 10.0,
            "tags_per_post": 1.5,
            "num_tags_per_post": 3.0,
        }
        resp = client.post("/api/predict/facebook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "facebook"


# ---------------------------------------------------------------------------
# LinkedIn (Realistic Synthetic Data)
# ---------------------------------------------------------------------------
class TestLinkedIn:
    def test_valid_prediction(self, client):
        payload = {
            "connections": 250,
            "endorsements": 50,
            "recommendations": 5,
            "posts_per_month": 2.5,
            "profile_views": 500,
            "account_age_days": 1200,
            "has_profile_pic": 1,
            "has_summary": 1,
            "has_experience": 1,
            "has_education": 1,
            "skills_count": 15,
            "mutual_connections": 50,
        }
        resp = client.post("/api/predict/linkedin", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "linkedin"
        assert data["data_source"] == "synthetic"  # Trained on synthetic data
        assert 0 <= data["probability"] <= 1
        assert data["risk_level"] in ("low", "medium", "high")

    def test_validation_rejects_negative(self, client):
        payload = {
            "connections": -1,  # ge=0 constraint should reject
            "endorsements": 0,
            "recommendations": 0,
            "posts_per_month": 0,
            "profile_views": 0,
            "account_age_days": 0,
            "has_profile_pic": 0,
            "has_summary": 0,
            "has_experience": 0,
            "has_education": 0,
            "skills_count": 0,
            "mutual_connections": 0,
        }
        resp = client.post("/api/predict/linkedin", json=payload)
        assert resp.status_code == 422  # Validation error


# ---------------------------------------------------------------------------
# YouTube (Realistic Synthetic Data)
# ---------------------------------------------------------------------------
class TestYouTube:
    def test_valid_prediction(self, client):
        payload = {
            "subscriber_count": 10000,
            "video_count": 50,
            "total_views": 500000,
            "avg_likes_per_video": 200,
            "avg_comments_per_video": 30,
            "channel_age_days": 730,
            "has_custom_thumbnail": 1,
            "has_description": 1,
            "uploads_per_month": 4.0,
            "engagement_rate": 3.5,
        }
        resp = client.post("/api/predict/youtube", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "youtube"
        assert data["data_source"] == "synthetic"  # Trained on synthetic data
        assert 0 <= data["probability"] <= 1
        assert data["risk_level"] in ("low", "medium", "high")


# ---------------------------------------------------------------------------
# Batch Predictions
# ---------------------------------------------------------------------------
class TestBatch:
    def test_batch_instagram(self, client):
        payload = {
            "records": [
                {"profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
                 "posts": 42, "followers": 1500, "following": 800},
                {"profile_pic": 0, "username_has_numbers": 1, "bio_present": 0,
                 "posts": 0, "followers": 0, "following": 5000},
            ]
        }
        resp = client.post("/api/predict/batch/instagram", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["total"] == 2
        assert data["summary"]["successful"] == 2

    def test_batch_unknown_platform(self, client):
        resp = client.post("/api/predict/batch/tiktok", json={"records": [{"any": "data"}]})
        assert resp.status_code == 400
