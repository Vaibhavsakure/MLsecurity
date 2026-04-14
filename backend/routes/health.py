"""
Health check endpoint — returns model status, version, and uptime.
"""
import time
from fastapi import APIRouter

from ml.engine import (
    instagram_model, twitter_model, reddit_model,
    facebook_model, linkedin_model, youtube_model,
    SHAP_EXPLAINERS,
)
from ml.ensemble import _ensemble_models

router = APIRouter(prefix="/api", tags=["health"])

_START_TIME = time.time()


@router.get("/health")
def health():
    uptime_seconds = int(time.time() - _START_TIME)
    model_status = {
        "instagram": instagram_model is not None,
        "twitter":   twitter_model is not None,
        "reddit":    reddit_model is not None,
        "facebook":  facebook_model is not None,
        "linkedin":  linkedin_model is not None,
        "youtube":   youtube_model is not None,
    }
    return {
        "status": "ok",
        "version": "5.0.0",
        "uptime_seconds": uptime_seconds,
        "models": model_status,
        "models_loaded": sum(model_status.values()),
        "shap": {k: v is not None for k, v in SHAP_EXPLAINERS.items()},
        "ensemble": {
            p: len(m) > 1 for p, m in _ensemble_models.items()
        },
    }
