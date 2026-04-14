# ============================================================================
# SocialGuard AI — Unified Dockerfile (Frontend + Backend)
# Builds React frontend, then serves it via FastAPI on a single domain.
# ============================================================================

# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY frontend/ .
# Vite auto-reads .env.production during build
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
