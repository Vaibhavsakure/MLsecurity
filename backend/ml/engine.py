"""
ML engine: model loading, SHAP explainers, feature definitions, and prediction helpers.
Includes synthetic data transparency markers for LinkedIn and YouTube models.
"""
import os
import numpy as np
import joblib
import shap

# ---------------------------------------------------------------------------
# Model Loading
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def _load(name: str):
    path = os.path.join(MODEL_DIR, name)
    if not os.path.exists(path):
        return None
    return joblib.load(path)


instagram_model = _load("fake_account_detector.pkl")
twitter_model = _load("twitter_bot_detector.pkl")
reddit_model = _load("reddit_bot_detector.pkl")
facebook_model = _load("facebook_spam_detector.pkl")
linkedin_model = _load("linkedin_fake_detector.pkl")
youtube_model = _load("youtube_bot_detector.pkl")

# ---------------------------------------------------------------------------
# Synthetic Data Transparency
# ---------------------------------------------------------------------------
# LinkedIn and YouTube have no public fake-account datasets, so they were
# trained on realistic synthetic data. Their evaluation metrics (100% AUC)
# confirm this — real-world data never achieves perfect scores.
# Flagging them here causes:
#   • data_source: "synthetic" in API responses
#   • confidence downgrade in interpret_risk()
#   • synthetic_warning flag for frontend display
# This is consistent with evaluation_results/evaluation_summary.json.
# ---------------------------------------------------------------------------
SYNTHETIC_PLATFORMS = {"linkedin", "youtube"}

SYNTHETIC_DISCLAIMER = (
    "This model was trained on synthetically generated data and has not been "
    "validated on real-world profiles. Results should be treated as demonstrative "
    "only and may not reflect actual fake account characteristics."
)


def is_synthetic(platform: str) -> bool:
    """Return True if the platform model was trained on synthetic data."""
    return platform.lower() in SYNTHETIC_PLATFORMS


# ---------------------------------------------------------------------------
# Feature Names (for SHAP explanations)
# ---------------------------------------------------------------------------
FEATURE_NAMES = {
    "instagram": [
        "Profile Pic", "Username Numbers", "Fullname Words", "Nums/Fullname",
        "Name=Username", "Bio Present", "External URL", "Private",
        "Posts", "Followers", "Following", "Follower/Following Ratio",
        "Posts/Follower", "Has Description", "Has Fullname", "Profile Completeness"
    ],
    "twitter": [
        "ID", "Tweets", "Followers", "Friends", "Favourites",
        "Listed Count", "Default Profile", "Default Image",
        "Geo Enabled", "BG Image", "BG Tile", "UTC Offset",
        "Protected", "Verified"
    ],
    "reddit": [
        "Account Age (Days)", "Karma", "Sentiment Score",
        "Avg Word Length", "Contains Links", "Karma/Day"
    ],
    "facebook": [
        "Friends", "Following", "Communities", "Account Age",
        "Posts Shared", "URLs Shared", "Photos/Videos",
        "Fraction URLs", "Fraction Photos", "Avg Comments/Post",
        "Likes/Post", "Tags/Post", "# Tags/Post"
    ],
    "linkedin": [
        "Connections", "Endorsements", "Recommendations", "Posts/Month",
        "Profile Views", "Account Age (Days)", "Has Profile Pic", "Has Summary",
        "Has Experience", "Has Education", "Skills Count", "Mutual Connections"
    ],
    "youtube": [
        "Subscribers", "Videos", "Total Views", "Avg Likes/Video",
        "Avg Comments/Video", "Channel Age (Days)", "Has Custom Thumbnail",
        "Has Description", "Uploads/Month", "Engagement Rate"
    ],
}

# ---------------------------------------------------------------------------
# SHAP Explainers
# ---------------------------------------------------------------------------
SHAP_EXPLAINERS = {}


def _init_explainers():
    models = {
        "instagram": instagram_model,
        "twitter": twitter_model,
        "reddit": reddit_model,
        "facebook": facebook_model,
        "linkedin": linkedin_model,
        "youtube": youtube_model,
    }
    for name, model in models.items():
        if model is not None:
            try:
                SHAP_EXPLAINERS[name] = shap.TreeExplainer(model)
            except Exception:
                SHAP_EXPLAINERS[name] = None


_init_explainers()


def get_shap_importances(platform: str, features: np.ndarray):
    """Return top-8 SHAP feature importances for a prediction."""
    explainer = SHAP_EXPLAINERS.get(platform)
    if explainer is None:
        return []
    try:
        sv = explainer.shap_values(features)
        if isinstance(sv, list):
            values = sv[1][0]
        else:
            values = sv[0]
        names = FEATURE_NAMES.get(platform, [])
        importances = []
        for i, v in enumerate(values):
            name = names[i] if i < len(names) else f"Feature {i}"
            importances.append({"feature": name, "value": round(float(v), 4)})
        importances.sort(key=lambda x: abs(x["value"]), reverse=True)
        return importances[:8]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def interpret_risk(prob: float, platform: str = None):
    """Interpret a probability score into a risk level with confidence band.

    If the platform uses synthetic training data, the confidence is
    automatically downgraded and a warning flag is added.
    """
    if prob < 0.3:
        risk = {
            "risk_level": "low",
            "label": "Low Risk",
            "message": "This account appears to be genuine.",
        }
    elif prob < 0.6:
        risk = {
            "risk_level": "medium",
            "label": "Medium Risk",
            "message": "Some suspicious indicators detected. Proceed with caution.",
        }
    else:
        risk = {
            "risk_level": "high",
            "label": "High Risk",
            "message": "High probability of being a fake or bot account.",
        }

    # Add confidence band based on distance from decision boundaries
    if prob < 0.15 or prob > 0.85:
        risk["confidence"] = "very_high"
    elif prob < 0.25 or prob > 0.7:
        risk["confidence"] = "high"
    elif 0.4 < prob < 0.5:
        risk["confidence"] = "low"
    else:
        risk["confidence"] = "moderate"

    # Downgrade confidence for synthetic-data models
    if platform and is_synthetic(platform):
        _confidence_downgrade = {
            "very_high": "moderate",
            "high": "low",
            "moderate": "low",
            "low": "low",
        }
        risk["confidence"] = _confidence_downgrade.get(risk["confidence"], "low")
        risk["synthetic_warning"] = True
        risk["message"] += (
            " ⚠️ Note: This prediction is based on a model trained with "
            "synthetic data and may not reflect real-world accuracy."
        )

    return risk


def get_model(platform: str):
    """Return the model for a given platform or None."""
    return {
        "instagram": instagram_model,
        "twitter": twitter_model,
        "reddit": reddit_model,
        "facebook": facebook_model,
        "linkedin": linkedin_model,
        "youtube": youtube_model,
    }.get(platform)
