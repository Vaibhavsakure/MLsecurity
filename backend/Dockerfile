FROM python:3.11-slim

WORKDIR /app

# System deps for sklearn/xgboost
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code only
COPY backend/ .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; r=httpx.get('http://localhost:8000/api/health'); assert r.status_code==200"

# Run server — Railway injects $PORT, defaults to 8000 locally
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
