"""
Security middleware: Firebase auth verification, rate limiting, and request logging.

Auth middleware validates Firebase ID tokens on protected endpoints.
If firebase-admin is not configured, auth is bypassed with a warning (dev mode).

Response headers added:
  X-Request-ID     — unique trace ID per request
  X-RateLimit-*    — quota visibility for API consumers
"""
import os
import time
import uuid
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("socialguard")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# Firebase Admin Initialization (optional — graceful if not configured)
# ---------------------------------------------------------------------------
_firebase_app = None

def _init_firebase():
    global _firebase_app
    try:
        import firebase_admin
        from firebase_admin import credentials

        cred_path = os.environ.get(
            "FIREBASE_CREDENTIALS_PATH",
            os.path.join(os.path.dirname(__file__), "firebase-adminsdk.json"),
        )
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase Admin initialized — auth middleware active")
        else:
            logger.warning(
                "⚠️  Firebase credentials not found at %s — auth middleware DISABLED (dev mode)",
                cred_path,
            )
    except ImportError:
        logger.warning("⚠️  firebase-admin not installed — auth middleware DISABLED")
    except Exception as e:
        logger.warning("⚠️  Firebase init failed: %s — auth middleware DISABLED", e)


_init_firebase()


def verify_firebase_token(token: str):
    """Verify a Firebase ID token and return the decoded claims, or None."""
    if _firebase_app is None:
        return {"uid": "dev-mode", "dev_bypass": True}
    try:
        from firebase_admin import auth
        return auth.verify_id_token(token)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Auth Middleware
# ---------------------------------------------------------------------------
# Paths that do NOT require authentication
PUBLIC_PREFIXES = ("/api/health", "/api/models/", "/docs", "/openapi.json", "/redoc")


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates Firebase Bearer tokens on protected endpoints."""

    async def dispatch(self, request, call_next):
        path = request.url.path

        # Allow public endpoints
        if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
            return await call_next(request)

        # Allow OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Bypass auth in testing mode
        if os.environ.get("TESTING") == "1":
            request.state.user = {"uid": "test-user", "test_bypass": True}
            return await call_next(request)

        # Extract token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            claims = verify_firebase_token(token)
            if claims is not None:
                request.state.user = claims
                return await call_next(request)

        # If firebase is not configured, allow through in dev mode
        if _firebase_app is None:
            request.state.user = {"uid": "dev-mode", "dev_bypass": True}
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required. Provide a valid Firebase ID token."},
        )


# ---------------------------------------------------------------------------
# Rate Limiting Middleware (file-backed persistence)
# ---------------------------------------------------------------------------
_RATE_LIMIT_FILE = os.path.join(os.path.dirname(__file__), ".rate_limit_state.json")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding window rate limiter with file-backed persistence.

    Rate limit state is periodically saved to disk so limits survive
    server restarts. Falls back to pure in-memory if file I/O fails.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)
        self._save_counter = 0
        self._save_every = 10  # Save to disk every N requests
        self._load_state()

    def _load_state(self):
        """Load persisted rate limit state from disk on startup."""
        try:
            if os.path.exists(_RATE_LIMIT_FILE):
                import json
                with open(_RATE_LIMIT_FILE, "r") as f:
                    data = json.load(f)
                now = time.time()
                # Only load entries that haven't expired
                for ip, timestamps in data.items():
                    valid = [t for t in timestamps if now - t < self.window_seconds]
                    if valid:
                        self._requests[ip] = valid
                logger.info("✅ Rate limit state restored from disk (%d IPs)", len(self._requests))
        except Exception as e:
            logger.debug("Rate limit state load skipped: %s", e)

    def _save_state(self):
        """Persist current rate limit state to disk."""
        try:
            import json
            now = time.time()
            # Only save non-expired entries
            state = {}
            for ip, timestamps in self._requests.items():
                valid = [t for t in timestamps if now - t < self.window_seconds]
                if valid:
                    state[ip] = valid
            with open(_RATE_LIMIT_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass  # Graceful fallback — in-memory still works

    async def dispatch(self, request, call_next):
        # Don't rate-limit health checks
        if request.url.path.startswith("/api/health"):
            return await call_next(request)

        # Bypass rate limiting in test mode
        if os.environ.get("TESTING") == "1":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old entries and record new one
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > cutoff
        ]

        current_count = len(self._requests[client_ip])
        remaining = max(0, self.max_requests - current_count - 1)
        reset_at = int(now) + self.window_seconds

        if current_count >= self.max_requests:
            logger.warning("Rate limit exceeded for %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s."
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                },
            )

        self._requests[client_ip].append(now)

        # Periodically persist state to disk
        self._save_counter += 1
        if self._save_counter >= self._save_every:
            self._save_counter = 0
            self._save_state()

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        return response


# ---------------------------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------------------------
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs method, path, status code, and response time for every request.
    Injects X-Request-ID for distributed tracing.
    """

    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        # Attach trace ID to response
        response.headers["X-Request-ID"] = request_id

        # Color-code by status
        status = response.status_code
        if status < 400:
            level = logging.INFO
        elif status < 500:
            level = logging.WARNING
        else:
            level = logging.ERROR

        logger.log(
            level,
            "[%s] %s %s → %d (%.1fms)",
            request_id,
            request.method,
            request.url.path,
            status,
            duration_ms,
        )
        return response
