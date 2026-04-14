"""
Comprehensive schema validation tests — verifies Field(ge/le) constraints
reject out-of-range values and coerce correctly for all 6 platforms.
"""
import pytest


# ---------------------------------------------------------------------------
# Instagram Validation
# ---------------------------------------------------------------------------
class TestInstagramValidation:
    BASE = {
        "profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
        "posts": 42, "followers": 1500, "following": 800,
    }

    def test_rejects_negative_posts(self, client):
        payload = {**self.BASE, "posts": -1}
        assert client.post("/api/predict/instagram", json=payload).status_code == 422

    def test_rejects_negative_followers(self, client):
        payload = {**self.BASE, "followers": -100}
        assert client.post("/api/predict/instagram", json=payload).status_code == 422

    def test_rejects_profile_pic_out_of_range(self, client):
        payload = {**self.BASE, "profile_pic": 2}
        assert client.post("/api/predict/instagram", json=payload).status_code == 422

    def test_accepts_zero_followers(self, client):
        payload = {**self.BASE, "followers": 0, "following": 0, "posts": 0}
        assert client.post("/api/predict/instagram", json=payload).status_code == 200


# ---------------------------------------------------------------------------
# Twitter Validation
# ---------------------------------------------------------------------------
class TestTwitterValidation:
    BASE = {
        "statuses_count": 3200, "followers_count": 500, "friends_count": 300,
        "favourites_count": 1200, "listed_count": 10,
        "verified": 0, "default_profile_image": 0,
    }

    def test_rejects_negative_statuses(self, client):
        payload = {**self.BASE, "statuses_count": -1}
        assert client.post("/api/predict/twitter", json=payload).status_code == 422

    def test_rejects_verified_out_of_range(self, client):
        payload = {**self.BASE, "verified": 5}
        assert client.post("/api/predict/twitter", json=payload).status_code == 422

    def test_optional_fields_default_correctly(self, client):
        """Sending only required fields should work (optional fields have defaults)."""
        resp = client.post("/api/predict/twitter", json=self.BASE)
        assert resp.status_code == 200
        assert 0 <= resp.json()["probability"] <= 1

    def test_rejects_protected_out_of_range(self, client):
        payload = {**self.BASE, "protected": 2}
        assert client.post("/api/predict/twitter", json=payload).status_code == 422


# ---------------------------------------------------------------------------
# Reddit Validation
# ---------------------------------------------------------------------------
class TestRedditValidation:
    BASE = {
        "account_age_days": 365, "user_karma": 5000,
        "sentiment_score": 0.15, "avg_word_length": 5.2, "contains_links": 0,
    }

    def test_rejects_sentiment_above_1(self, client):
        payload = {**self.BASE, "sentiment_score": 1.5}
        assert client.post("/api/predict/reddit", json=payload).status_code == 422

    def test_rejects_sentiment_below_minus_1(self, client):
        payload = {**self.BASE, "sentiment_score": -1.5}
        assert client.post("/api/predict/reddit", json=payload).status_code == 422

    def test_rejects_negative_karma(self, client):
        payload = {**self.BASE, "user_karma": -1}
        assert client.post("/api/predict/reddit", json=payload).status_code == 422

    def test_accepts_perfect_negative_sentiment(self, client):
        payload = {**self.BASE, "sentiment_score": -1.0}
        assert client.post("/api/predict/reddit", json=payload).status_code == 200

    def test_contains_links_defaults_to_0(self, client):
        """contains_links is optional with default=0."""
        payload = {k: v for k, v in self.BASE.items() if k != "contains_links"}
        assert client.post("/api/predict/reddit", json=payload).status_code == 200


# ---------------------------------------------------------------------------
# Facebook Validation
# ---------------------------------------------------------------------------
class TestFacebookValidation:
    BASE = {
        "friends": 500, "following": 200, "community": 10, "age": 3.5,
        "postshared": 100, "urlshared": 20, "photos_videos": 30,
        "fpurls": 0.2, "fpphotos_videos": 0.5,
        "avgcomment_per_post": 2.5, "likes_per_post": 10.0,
        "tags_per_post": 1.5, "num_tags_per_post": 3.0,
    }

    def test_rejects_fpurls_above_1(self, client):
        payload = {**self.BASE, "fpurls": 1.5}
        assert client.post("/api/predict/facebook", json=payload).status_code == 422

    def test_rejects_negative_friends(self, client):
        payload = {**self.BASE, "friends": -1}
        assert client.post("/api/predict/facebook", json=payload).status_code == 422

    def test_rejects_negative_age(self, client):
        payload = {**self.BASE, "age": -0.5}
        assert client.post("/api/predict/facebook", json=payload).status_code == 422


# ---------------------------------------------------------------------------
# YouTube Validation
# ---------------------------------------------------------------------------
class TestYouTubeValidation:
    BASE = {
        "subscriber_count": 10000, "video_count": 50, "total_views": 500000,
        "avg_likes_per_video": 200, "avg_comments_per_video": 30,
        "channel_age_days": 730, "has_custom_thumbnail": 1,
        "has_description": 1, "uploads_per_month": 4.0, "engagement_rate": 3.5,
    }

    def test_rejects_has_thumbnail_out_of_range(self, client):
        payload = {**self.BASE, "has_custom_thumbnail": 2}
        assert client.post("/api/predict/youtube", json=payload).status_code == 422

    def test_rejects_negative_subscribers(self, client):
        payload = {**self.BASE, "subscriber_count": -1}
        assert client.post("/api/predict/youtube", json=payload).status_code == 422

    def test_rejects_negative_engagement(self, client):
        payload = {**self.BASE, "engagement_rate": -0.1}
        assert client.post("/api/predict/youtube", json=payload).status_code == 422


# ---------------------------------------------------------------------------
# LinkedIn Validation
# ---------------------------------------------------------------------------
class TestLinkedInValidation:
    BASE = {
        "connections": 250, "endorsements": 50, "recommendations": 5,
        "posts_per_month": 2.5, "profile_views": 500, "account_age_days": 1200,
        "has_profile_pic": 1, "has_summary": 1, "has_experience": 1,
        "has_education": 1, "skills_count": 15, "mutual_connections": 50,
    }

    def test_rejects_has_profile_pic_out_of_range(self, client):
        payload = {**self.BASE, "has_profile_pic": 3}
        assert client.post("/api/predict/linkedin", json=payload).status_code == 422

    def test_rejects_negative_connections(self, client):
        payload = {**self.BASE, "connections": -5}
        assert client.post("/api/predict/linkedin", json=payload).status_code == 422


# ---------------------------------------------------------------------------
# Batch Validation
# ---------------------------------------------------------------------------
class TestBatchValidation:
    def test_batch_rejects_empty_records(self, client):
        """Empty records list should be rejected (min_length=1)."""
        resp = client.post("/api/predict/batch/instagram", json={"records": []})
        assert resp.status_code == 422

    def test_url_scan_rejects_empty_url(self, client):
        """Empty URL should be rejected by min_length=4 constraint."""
        resp = client.post("/api/scan/url", json={"url": ""})
        assert resp.status_code == 422

    def test_url_scan_rejects_very_short_url(self, client):
        resp = client.post("/api/scan/url", json={"url": "abc"})
        assert resp.status_code == 422
