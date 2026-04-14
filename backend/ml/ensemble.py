"""
Ensemble ML engine: weighted voting across XGBoost + Random Forest + Logistic Regression.
Falls back gracefully to XGBoost-only if ensemble models aren't available.
"""
import os
import json
import numpy as np
import joblib
import logging

logger = logging.getLogger("socialguard")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# ---------------------------------------------------------------------------
# Load ensemble models
# ---------------------------------------------------------------------------
_ensemble_models = {}  # {platform: {"xgb": model, "rf": model, "lr": {"model": lr, "scaler": scaler}}}
_ensemble_weights = {}  # {platform: {"xgb": w, "rf": w, "lr": w}}


def _load_ensemble_model(platform, suffix, name):
    """Load a model file, return None if not found."""
    path = os.path.join(MODEL_DIR, f"{platform}_{suffix}.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None


def _init_ensemble():
    """Initialize ensemble models for all platforms."""
    # XGBoost model filename mapping
    xgb_names = {
        "instagram": "fake_account_detector.pkl",
        "twitter": "twitter_bot_detector.pkl",
        "reddit": "reddit_bot_detector.pkl",
        "facebook": "facebook_spam_detector.pkl",
        "linkedin": "linkedin_fake_detector.pkl",
        "youtube": "youtube_bot_detector.pkl",
    }

    # Load evaluation metrics for weighting
    eval_path = os.path.join(MODEL_DIR, "..", "evaluation_results", "evaluation_summary.json")
    eval_data = {}
    try:
        if os.path.exists(eval_path):
            with open(eval_path, "r") as f:
                eval_data = json.load(f)
    except Exception:
        pass

    platforms = ["instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"]

    for platform in platforms:
        models = {}

        # XGBoost (always available)
        xgb_path = os.path.join(MODEL_DIR, xgb_names.get(platform, ""))
        if os.path.exists(xgb_path):
            models["xgb"] = joblib.load(xgb_path)

        # Random Forest
        rf = _load_ensemble_model(platform, "rf", "Random Forest")
        if rf is not None:
            models["rf"] = rf

        # Logistic Regression (packaged with scaler)
        lr = _load_ensemble_model(platform, "lr", "Logistic Regression")
        if lr is not None:
            models["lr"] = lr

        if models:
            _ensemble_models[platform] = models

        # Compute weights based on evaluation AUC scores
        if platform in eval_data and "comparison" in eval_data[platform]:
            comp = eval_data[platform]["comparison"]
            xgb_auc = comp.get("XGBoost", {}).get("auc", 0.9)
            rf_auc = comp.get("Random Forest", {}).get("auc", 0.85)
            lr_auc = comp.get("Logistic Regression", {}).get("auc", 0.8)
            total = xgb_auc + rf_auc + lr_auc
            _ensemble_weights[platform] = {
                "xgb": xgb_auc / total,
                "rf": rf_auc / total,
                "lr": lr_auc / total,
            }
        else:
            _ensemble_weights[platform] = {"xgb": 0.5, "rf": 0.3, "lr": 0.2}

    available = {p: list(m.keys()) for p, m in _ensemble_models.items() if len(m) > 1}
    if available:
        logger.info("✅ Ensemble models loaded: %s", available)
    else:
        logger.info("ℹ️  No ensemble models found — run train_ensemble.py to enable")


_init_ensemble()


# ---------------------------------------------------------------------------
# Ensemble Prediction
# ---------------------------------------------------------------------------

def has_ensemble(platform: str) -> bool:
    """Check if ensemble models are available for a platform."""
    models = _ensemble_models.get(platform, {})
    return len(models) > 1


def ensemble_predict(platform: str, features: np.ndarray) -> dict:
    """
    Run ensemble prediction with weighted voting.

    Returns:
        {
            "ensemble_probability": float,
            "ensemble_agreement": "high" | "moderate" | "low",
            "individual_predictions": {
                "XGBoost": {"probability": float, "weight": float},
                "Random Forest": {"probability": float, "weight": float},
                "Logistic Regression": {"probability": float, "weight": float},
            }
        }
    """
    models = _ensemble_models.get(platform, {})
    weights = _ensemble_weights.get(platform, {})

    if not models:
        return None

    predictions = {}
    weighted_sum = 0.0
    total_weight = 0.0

    # XGBoost
    if "xgb" in models:
        prob = float(models["xgb"].predict_proba(features)[0][1])
        w = weights.get("xgb", 0.5)
        predictions["XGBoost"] = {"probability": round(prob, 4), "weight": round(w, 3)}
        weighted_sum += prob * w
        total_weight += w

    # Random Forest
    if "rf" in models:
        prob = float(models["rf"].predict_proba(features)[0][1])
        w = weights.get("rf", 0.3)
        predictions["Random Forest"] = {"probability": round(prob, 4), "weight": round(w, 3)}
        weighted_sum += prob * w
        total_weight += w

    # Logistic Regression (needs scaling)
    if "lr" in models:
        lr_data = models["lr"]
        if isinstance(lr_data, dict) and "model" in lr_data and "scaler" in lr_data:
            scaled = lr_data["scaler"].transform(features)
            prob = float(lr_data["model"].predict_proba(scaled)[0][1])
        else:
            # Fallback: model without scaler
            prob = float(lr_data.predict_proba(features)[0][1])
        w = weights.get("lr", 0.2)
        predictions["Logistic Regression"] = {"probability": round(prob, 4), "weight": round(w, 3)}
        weighted_sum += prob * w
        total_weight += w

    # Ensemble probability
    ensemble_prob = weighted_sum / total_weight if total_weight > 0 else 0.5

    # Agreement analysis
    probs = [p["probability"] for p in predictions.values()]
    if len(probs) >= 2:
        prob_range = max(probs) - min(probs)
        if prob_range < 0.1:
            agreement = "high"
        elif prob_range < 0.25:
            agreement = "moderate"
        else:
            agreement = "low"
    else:
        agreement = "single_model"

    # All agree on the same risk level?
    risk_levels = []
    for p in probs:
        if p < 0.3:
            risk_levels.append("low")
        elif p < 0.6:
            risk_levels.append("medium")
        else:
            risk_levels.append("high")

    unanimous = len(set(risk_levels)) == 1 if risk_levels else False

    return {
        "ensemble_probability": round(ensemble_prob, 4),
        "ensemble_agreement": agreement,
        "models_unanimous": unanimous,
        "models_used": len(predictions),
        "individual_predictions": predictions,
    }
