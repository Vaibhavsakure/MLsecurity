"""
Prediction endpoints for all 6 social media platforms + batch predictions.
Includes synthetic data transparency for LinkedIn/YouTube models.
Supports optional ensemble mode (?ensemble=true) for weighted multi-model voting.
"""
import numpy as np
from fastapi import APIRouter, HTTPException, Query

from schemas import (
    InstagramInput, TwitterInput, RedditInput,
    FacebookInput, LinkedInInput, YouTubeInput,
    BatchPredictRequest,
)
from ml.engine import (
    instagram_model, twitter_model, reddit_model,
    facebook_model, linkedin_model, youtube_model,
    get_shap_importances, interpret_risk,
    is_synthetic, SYNTHETIC_DISCLAIMER,
)
from ml.ensemble import has_ensemble, ensemble_predict

router = APIRouter(prefix="/api", tags=["predictions"])


def _add_synthetic_info(result: dict) -> dict:
    """Annotate the response if the platform uses synthetic training data."""
    if is_synthetic(result.get("platform", "")):
        result["data_source"] = "synthetic"
        result["model_disclaimer"] = SYNTHETIC_DISCLAIMER
    else:
        result["data_source"] = "real_world"
    return result


def _add_ensemble(result: dict, platform: str, features: np.ndarray, use_ensemble: bool) -> dict:
    """Optionally add ensemble predictions to the result."""
    if use_ensemble and has_ensemble(platform):
        ens = ensemble_predict(platform, features)
        if ens:
            result["ensemble"] = ens
    return result


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------
@router.post("/predict/instagram")
def predict_instagram(data: InstagramInput, ensemble: bool = Query(False)):
    if instagram_model is None:
        raise HTTPException(status_code=503, detail="Instagram model not loaded")

    follower_following_ratio = data.followers / (data.following + 1)
    posts_per_follower = data.posts / (data.followers + 1)
    has_description = data.bio_present
    has_fullname = 1
    profile_completeness = data.profile_pic + has_description + has_fullname

    features = np.array([[
        data.profile_pic,
        0.7 if data.username_has_numbers == 1 else 0,
        1, 0, 0,
        data.bio_present, 0, 0,
        data.posts, data.followers, data.following,
        follower_following_ratio, posts_per_follower,
        has_description, has_fullname, profile_completeness
    ]])

    prob = float(instagram_model.predict_proba(features)[0][1])
    importances = get_shap_importances("instagram", features)
    result = {"probability": round(prob, 4), **interpret_risk(prob, "instagram"), "platform": "instagram",
            "feature_importances": importances, "input_data": data.model_dump()}
    _add_ensemble(result, "instagram", features, ensemble)
    return _add_synthetic_info(result)


# ---------------------------------------------------------------------------
# Twitter
# ---------------------------------------------------------------------------
@router.post("/predict/twitter")
def predict_twitter(data: TwitterInput, ensemble: bool = Query(False)):
    if twitter_model is None:
        raise HTTPException(status_code=503, detail="Twitter model not loaded")

    features = np.array([[
        0, data.statuses_count, data.followers_count, data.friends_count,
        data.favourites_count, data.listed_count, 0, data.default_profile_image,
        data.geo_enabled, data.has_bg_image, data.has_bg_tile,
        data.utc_offset, data.protected, data.verified
    ]])

    prob = float(twitter_model.predict_proba(features)[0][1])
    importances = get_shap_importances("twitter", features)
    result = {"probability": round(prob, 4), **interpret_risk(prob, "twitter"), "platform": "twitter",
            "feature_importances": importances, "input_data": data.model_dump()}
    _add_ensemble(result, "twitter", features, ensemble)
    return _add_synthetic_info(result)


# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------
@router.post("/predict/reddit")
def predict_reddit(data: RedditInput, ensemble: bool = Query(False)):
    if reddit_model is None:
        raise HTTPException(status_code=503, detail="Reddit model not loaded")

    karma_per_day = data.user_karma / (data.account_age_days + 1)
    features = np.array([[
        data.account_age_days, data.user_karma, data.sentiment_score,
        data.avg_word_length, int(data.contains_links), karma_per_day
    ]])

    prob = float(reddit_model.predict_proba(features)[0][1])
    importances = get_shap_importances("reddit", features)
    result = {"probability": round(prob, 4), **interpret_risk(prob, "reddit"), "platform": "reddit",
            "feature_importances": importances, "input_data": data.model_dump()}
    _add_ensemble(result, "reddit", features, ensemble)
    return _add_synthetic_info(result)


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------
@router.post("/predict/facebook")
def predict_facebook(data: FacebookInput, ensemble: bool = Query(False)):
    if facebook_model is None:
        raise HTTPException(status_code=503, detail="Facebook model not loaded")

    age_in_days = data.age * 365.25
    features = np.array([[
        data.friends, data.following, data.community, age_in_days,
        data.postshared, data.urlshared, data.photos_videos,
        data.fpurls, data.fpphotos_videos, data.avgcomment_per_post,
        data.likes_per_post, data.tags_per_post, data.num_tags_per_post
    ]])

    prob = float(facebook_model.predict_proba(features)[0][1])
    importances = get_shap_importances("facebook", features)
    result = {"probability": round(prob, 4), **interpret_risk(prob, "facebook"), "platform": "facebook",
            "feature_importances": importances, "input_data": data.model_dump()}
    _add_ensemble(result, "facebook", features, ensemble)
    return _add_synthetic_info(result)


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------
@router.post("/predict/linkedin")
def predict_linkedin(data: LinkedInInput, ensemble: bool = Query(False)):
    if linkedin_model is None:
        raise HTTPException(status_code=503, detail="LinkedIn model not loaded")

    features = np.array([[
        data.connections, data.endorsements, data.recommendations,
        data.posts_per_month, data.profile_views, data.account_age_days,
        data.has_profile_pic, data.has_summary, data.has_experience,
        data.has_education, data.skills_count, data.mutual_connections
    ]])

    prob = float(linkedin_model.predict_proba(features)[0][1])
    importances = get_shap_importances("linkedin", features)
    result = {"probability": round(prob, 4), **interpret_risk(prob, "linkedin"), "platform": "linkedin",
            "feature_importances": importances, "input_data": data.model_dump()}
    _add_ensemble(result, "linkedin", features, ensemble)
    return _add_synthetic_info(result)


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------
@router.post("/predict/youtube")
def predict_youtube(data: YouTubeInput, ensemble: bool = Query(False)):
    if youtube_model is None:
        raise HTTPException(status_code=503, detail="YouTube model not loaded")

    features = np.array([[
        data.subscriber_count, data.video_count, data.total_views,
        data.avg_likes_per_video, data.avg_comments_per_video, data.channel_age_days,
        data.has_custom_thumbnail, data.has_description, data.uploads_per_month,
        data.engagement_rate
    ]])

    prob = float(youtube_model.predict_proba(features)[0][1])
    importances = get_shap_importances("youtube", features)
    result = {"probability": round(prob, 4), **interpret_risk(prob, "youtube"), "platform": "youtube",
            "feature_importances": importances, "input_data": data.model_dump()}
    _add_ensemble(result, "youtube", features, ensemble)
    return _add_synthetic_info(result)


# ---------------------------------------------------------------------------
# Batch Predictions
# ---------------------------------------------------------------------------
PREDICT_FUNCTIONS = {
    "instagram": (InstagramInput, predict_instagram),
    "twitter": (TwitterInput, predict_twitter),
    "reddit": (RedditInput, predict_reddit),
    "facebook": (FacebookInput, predict_facebook),
    "linkedin": (LinkedInInput, predict_linkedin),
    "youtube": (YouTubeInput, predict_youtube),
}


@router.post("/predict/batch/{platform}")
def batch_predict(platform: str, req: BatchPredictRequest):
    """Run predictions on a batch of records."""
    if platform not in PREDICT_FUNCTIONS:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")

    input_class, predict_fn = PREDICT_FUNCTIONS[platform]
    results = []

    for i, record in enumerate(req.records):
        try:
            validated = input_class(**record)
            result = predict_fn(validated, ensemble=False)
            result["row_index"] = i
            results.append(result)
        except Exception as e:
            results.append({
                "row_index": i,
                "error": str(e),
                "probability": None,
                "risk_level": "unknown",
                "label": "Error",
                "message": f"Failed to process row {i}: {str(e)}"
            })

    summary = {
        "total": len(results),
        "successful": sum(1 for r in results if r.get("probability") is not None),
        "high_risk": sum(1 for r in results if r.get("risk_level") == "high"),
        "medium_risk": sum(1 for r in results if r.get("risk_level") == "medium"),
        "low_risk": sum(1 for r in results if r.get("risk_level") == "low"),
    }

    return {"platform": platform, "results": results, "summary": summary}
