"""
SocialGuard AI — Main API Entry Point
Slim orchestrator that imports modular routes and configures middleware.
"""
import os
import logging
from contextlib import asynccontextmanager

# ---------------------------------------------------------------------------
# Load .env file FIRST — before any env vars are read
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("socialguard")

APP_VERSION = "5.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle handler."""
    # --- Startup ---
    from ml.engine import (
        instagram_model, twitter_model, reddit_model,
        facebook_model, linkedin_model, youtube_model,
    )
    model_status = {
        "instagram": instagram_model is not None,
        "twitter":   twitter_model is not None,
        "reddit":    reddit_model is not None,
        "facebook":  facebook_model is not None,
        "linkedin":  linkedin_model is not None,
        "youtube":   youtube_model is not None,
    }
    loaded = sum(model_status.values())
    failed = [p for p, ok in model_status.items() if not ok]

    logger.info("═" * 60)
    logger.info("  SocialGuard AI v%s — starting up", APP_VERSION)
    logger.info("  Models loaded : %d / 6", loaded)
    if failed:
        logger.warning("  Missing models: %s", ", ".join(failed))
    else:
        logger.info("  All 6 models : ✅ ready")
    logger.info("═" * 60)

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("SocialGuard AI — shutting down gracefully")


# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SocialGuard AI API",
    version=APP_VERSION,
    description=(
        "AI-powered fake account detection across 6 social media platforms. "
        "Supports ensemble ML predictions, SHAP explainability, batch analysis, "
        "PDF reports, URL scanning, and a server-proxied AI chatbot."
    ),
    lifespan=lifespan,
)

# CORS — configurable via environment variable (default: vercel + localhost dev origins)
cors_origins_str = os.environ.get("CORS_ORIGINS", "https://m-lsecurity-mh24.vercel.app,http://localhost:5173,http://127.0.0.1:5173")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# ---------------------------------------------------------------------------
# Security & Observability Middleware
# ---------------------------------------------------------------------------
from middleware import RequestLoggingMiddleware, RateLimitMiddleware, AuthMiddleware

# Parse rate limit from env (e.g. "60/minute" → max_requests=60, window=60)
rate_limit_str = os.environ.get("RATE_LIMIT", "60/minute")
try:
    parts = rate_limit_str.split("/")
    _max_req = int(parts[0])
    _window_map = {"second": 1, "minute": 60, "hour": 3600}
    _window = _window_map.get(parts[1], 60)
except (IndexError, ValueError):
    _max_req, _window = 60, 60

# Order matters: logging first (outermost), then rate limiting, then auth (innermost)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=_max_req, window_seconds=_window)
app.add_middleware(RequestLoggingMiddleware)

# ---------------------------------------------------------------------------
# Register Modular Routes
# ---------------------------------------------------------------------------
from routes.health import router as health_router
from routes.predictions import router as predictions_router
from routes.reports import router as reports_router
from routes.scanner import router as scanner_router
from routes.evaluation import router as evaluation_router
from routes.chatbot import router as chatbot_router
from routes.public_api import router as public_api_router

app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(reports_router)
app.include_router(scanner_router)
app.include_router(evaluation_router)
app.include_router(chatbot_router)
app.include_router(public_api_router)

# ---------------------------------------------------------------------------
# Serve Frontend Static Files (production — built by Dockerfile)
# ---------------------------------------------------------------------------
_static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(_static_dir):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(_static_dir, "assets")), name="assets")

    # SPA catch-all — return index.html for any non-API route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for all non-API routes."""
        file_path = os.path.join(_static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_static_dir, "index.html"))

    logger.info("📦 Frontend static files mounted from %s", _static_dir)
