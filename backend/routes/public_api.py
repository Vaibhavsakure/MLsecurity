"""
Public API v1 — Programmatic access to SocialGuard AI predictions.
Uses API key authentication (X-API-Key header) instead of Firebase tokens.
"""
import secrets
import time
from typing import Optional
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Header, Request
from starlette.responses import JSONResponse

from schemas import (
    InstagramInput, TwitterInput, RedditInput,
    FacebookInput, LinkedInInput, YouTubeInput,
)
from routes.predictions import (
    predict_instagram, predict_twitter, predict_reddit,
    predict_facebook, predict_linkedin, predict_youtube,
)

router = APIRouter(prefix="/api/v1", tags=["public_api"])

# ---------------------------------------------------------------------------
# In-Memory API Key Store (production: use Firestore/Redis)
# ---------------------------------------------------------------------------
_api_keys = {}  # key_string -> {"uid": str, "name": str, "created": float, "requests": int}
_key_rate_limits = defaultdict(list)  # key -> list of timestamps
MAX_REQUESTS_PER_MINUTE = 20


def _validate_api_key(api_key: str) -> dict:
    """Validate API key and check rate limits."""
    if not api_key or api_key not in _api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Rate limit check
    now = time.time()
    _key_rate_limits[api_key] = [t for t in _key_rate_limits[api_key] if now - t < 60]
    if len(_key_rate_limits[api_key]) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail=f"API key rate limit exceeded. Max {MAX_REQUESTS_PER_MINUTE}/minute.",
        )
    _key_rate_limits[api_key].append(now)
    _api_keys[api_key]["requests"] += 1
    _api_keys[api_key]["last_used"] = now
    
    return _api_keys[api_key]


# ---------------------------------------------------------------------------
# Key Management Endpoints
# ---------------------------------------------------------------------------
@router.post("/keys/generate")
def generate_api_key(name: str = "API Key"):
    """Generate a new API key."""
    key = "sg_" + secrets.token_hex(24)
    _api_keys[key] = {
        "name": name,
        "created": time.time(),
        "requests": 0,
        "last_used": None,
    }
    return {"key": key, "name": name}


@router.get("/keys/list")
def list_api_keys():
    """List all API keys (masked)."""
    return [
        {
            "key_preview": f"{k[:12]}...{k[-8:]}",
            "name": v["name"],
            "created": v["created"],
            "requests": v["requests"],
            "last_used": v["last_used"],
        }
        for k, v in _api_keys.items()
    ]


@router.delete("/keys/revoke")
def revoke_api_key(key: str):
    """Revoke an API key."""
    if key in _api_keys:
        del _api_keys[key]
        return {"status": "revoked"}
    raise HTTPException(status_code=404, detail="Key not found")


# ---------------------------------------------------------------------------
# Public Analysis Endpoint
# ---------------------------------------------------------------------------
PLATFORM_HANDLERS = {
    "instagram": (InstagramInput, predict_instagram),
    "twitter": (TwitterInput, predict_twitter),
    "reddit": (RedditInput, predict_reddit),
    "facebook": (FacebookInput, predict_facebook),
    "linkedin": (LinkedInInput, predict_linkedin),
    "youtube": (YouTubeInput, predict_youtube),
}


@router.post("/analyze/{platform}")
async def analyze(platform: str, request: Request, x_api_key: str = Header(None)):
    """Public API endpoint for programmatic analysis."""
    _validate_api_key(x_api_key)
    
    if platform not in PLATFORM_HANDLERS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    input_class, handler = PLATFORM_HANDLERS[platform]
    body = await request.json()
    
    try:
        data = input_class(**body)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid input: {str(e)}")
    
    result = handler(data, ensemble=False)
    
    # Return trimmed response for API consumers
    return {
        "platform": platform,
        "probability": result["probability"],
        "risk_level": result["risk_level"],
        "confidence": result.get("confidence"),
        "label": result["label"],
        "message": result["message"],
        "data_source": result.get("data_source"),
    }


@router.get("/platforms")
def list_platforms():
    """List supported platforms."""
    return {
        "platforms": list(PLATFORM_HANDLERS.keys()),
        "version": "1.0",
    }
