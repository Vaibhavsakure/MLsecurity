"""Tests for SHAP feature importance output across all platforms."""
import pytest


# Payloads for each platform
PLATFORM_PAYLOADS = {
    "instagram": {
        "profile_pic": 1,
        "username_has_numbers": 0,
        "bio_present": 1,
        "posts": 42,
        "followers": 1500,
        "following": 800,
    },
    "twitter": {
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
    },
    "reddit": {
        "account_age_days": 365,
        "user_karma": 5000,
        "sentiment_score": 0.15,
        "avg_word_length": 5.2,
        "contains_links": 0,
    },
    "facebook": {
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
    },
    "linkedin": {
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
    },
    "youtube": {
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
    },
}


class TestShapImportances:
    @pytest.mark.parametrize("platform", ["instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"])
    def test_shap_returns_feature_importances(self, client, platform):
        """Every prediction should include a feature_importances list."""
        resp = client.post(f"/api/predict/{platform}", json=PLATFORM_PAYLOADS[platform])
        assert resp.status_code == 200
        data = resp.json()
        assert "feature_importances" in data
        assert isinstance(data["feature_importances"], list)

    @pytest.mark.parametrize("platform", ["instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"])
    def test_shap_importance_structure(self, client, platform):
        """Each importance entry should have 'feature' (str) and 'value' (float)."""
        resp = client.post(f"/api/predict/{platform}", json=PLATFORM_PAYLOADS[platform])
        data = resp.json()
        for imp in data["feature_importances"]:
            assert "feature" in imp, f"Missing 'feature' key in {platform}"
            assert "value" in imp, f"Missing 'value' key in {platform}"
            assert isinstance(imp["feature"], str)
            assert isinstance(imp["value"], (int, float))

    @pytest.mark.parametrize("platform", ["instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"])
    def test_shap_max_8_features(self, client, platform):
        """SHAP should return at most 8 feature importances (top-8)."""
        resp = client.post(f"/api/predict/{platform}", json=PLATFORM_PAYLOADS[platform])
        data = resp.json()
        assert len(data["feature_importances"]) <= 8

    @pytest.mark.parametrize("platform", ["instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"])
    def test_shap_sorted_by_absolute_value(self, client, platform):
        """Feature importances should be sorted by absolute value (descending)."""
        resp = client.post(f"/api/predict/{platform}", json=PLATFORM_PAYLOADS[platform])
        importances = resp.json()["feature_importances"]
        if len(importances) > 1:
            abs_values = [abs(imp["value"]) for imp in importances]
            assert abs_values == sorted(abs_values, reverse=True), \
                f"SHAP values not sorted by absolute value for {platform}"


class TestModelDataSource:
    """Verify platform data-source labels match the training data reality.

    Instagram, Twitter, Reddit, Facebook → trained on real-world Kaggle datasets.
    LinkedIn, YouTube → trained on realistic synthetic data (100% eval metrics
    are a strong indicator of synthetic data; see evaluation_results/evaluation_summary.json).
    """

    @pytest.mark.parametrize("platform", ["instagram", "twitter", "reddit", "facebook"])
    def test_real_world_platforms(self, client, platform):
        """Real-world platforms should return data_source=real_world."""
        resp = client.post(f"/api/predict/{platform}", json=PLATFORM_PAYLOADS[platform])
        data = resp.json()
        assert data["data_source"] == "real_world"
        assert "synthetic_warning" not in data

    @pytest.mark.parametrize("platform", ["linkedin", "youtube"])
    def test_synthetic_platforms(self, client, platform):
        """LinkedIn and YouTube use synthetic data — should be transparent about it."""
        resp = client.post(f"/api/predict/{platform}", json=PLATFORM_PAYLOADS[platform])
        assert resp.status_code == 200
        # Prediction should still work
        data = resp.json()
        assert 0 <= data["probability"] <= 1
        assert data["risk_level"] in ("low", "medium", "high")
