# ============================================================================
# SocialGuard AI — Unified Dockerfile (Frontend + Backend)
# Builds React frontend, then serves it via FastAPI on a single domain.
# No CORS issues, no separate deployments.
# ============================================================================

# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY frontend/ .

# Firebase config — passed as build args from Railway env vars
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID
ARG VITE_FIREBASE_MEASUREMENT_ID

# Set env vars for the Vite build
ENV VITE_API_URL="" \
    VITE_FIREBASE_API_KEY=$VITE_FIREBASE_API_KEY \
    VITE_FIREBASE_AUTH_DOMAIN=$VITE_FIREBASE_AUTH_DOMAIN \
    VITE_FIREBASE_PROJECT_ID=$VITE_FIREBASE_PROJECT_ID \
    VITE_FIREBASE_STORAGE_BUCKET=$VITE_FIREBASE_STORAGE_BUCKET \
    VITE_FIREBASE_MESSAGING_SENDER_ID=$VITE_FIREBASE_MESSAGING_SENDER_ID \
    VITE_FIREBASE_APP_ID=$VITE_FIREBASE_APP_ID \
    VITE_FIREBASE_MEASUREMENT_ID=$VITE_FIREBASE_MEASUREMENT_ID

RUN npm run build

# --- Stage 2: Python Backend ---
FROM python:3.11-slim
WORKDIR /app

# System deps for sklearn/xgboost
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy built frontend into backend's static directory
COPY --from=frontend-build /frontend/dist ./static

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; r=httpx.get('http://localhost:8000/api/health'); assert r.status_code==200"

# Run server — Railway injects $PORT, defaults to 8000 locally
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
