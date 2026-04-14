# SocialGuard AI — Multi-Platform Fake Account Detection

[![CI](https://github.com/Vaibhavsakure/socialguard-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Vaibhavsakure/socialguard-ai/actions)
[![Tests Backend](https://img.shields.io/badge/backend_tests-80%2B_passed-brightgreen)]()
[![Tests Frontend](https://img.shields.io/badge/frontend_tests-28_passed-brightgreen)]()
[![Docker](https://img.shields.io/badge/docker-compose_up-blue)]()

> AI-powered ensemble fake account detection across 6 social media platforms with explainable predictions, profile comparison, dark/light theme, public API, and a Chrome browser extension.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Frontend (React 19 + Vite 8)                       │
│  ┌────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐ ┌───────────────┐ │
│  │  Auth  │ │ Platform │ │ Compare │ │API Keys│ │   Dashboard   │ │
│  │ Pages  │ │ Analyzer │ │  Mode   │ │  Page  │ │  + Analytics  │ │
│  └───┬────┘ └────┬─────┘ └────┬────┘ └───┬────┘ └───────┬───────┘ │
│      └────────────┴────────────┴──────────┴──────────────┘         │
│              │ api.js │ Dark/Light Theme │ Ensemble Toggle          │
└──────────────┼────────────────────────────────────────────────────┘
               │ HTTPS + Bearer Token / API Key
┌──────────────┼────────────────────────────────────────────────────┐
│                        FastAPI Backend                              │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ Middleware  │  │   Routes     │  │    ML Engine               │ │
│  │ • Auth     │  │ • Predict/6  │  │ • Ensemble (XGB+RF+LR)    │ │
│  │ • RateLimit│  │ • Public API │  │ • SHAP Explainers          │ │
│  │ • Logging  │  │ • Scanner    │  │ • 17 Model Files (.pkl)    │ │
│  └────────────┘  │ • Reports    │  └───────────────────────────┘ │
│                  │ • Chatbot    │                                   │
│                  │ • Evaluation │                                   │
│                  └──────────────┘                                   │
└────────────────────────────────────────────────────────────────────┘
```

## Features

| Feature | Status |
|---|---|
| Multi-platform detection (Instagram, Twitter, Reddit, Facebook, LinkedIn, YouTube) | ✅ |
| Ensemble ML Pipeline (XGBoost + Random Forest + Logistic Regression) | ✅ |
| SHAP Explainability (per-prediction feature importance) | ✅ |
| Profile Comparison Mode (side-by-side analysis) | ✅ |
| Dark/Light Theme System (CSS variables + localStorage) | ✅ |
| Advanced Analytics Dashboard (timeline, distributions, heatmaps) | ✅ |
| Public API v1 (API key auth, rate limiting) | ✅ |
| Firebase Authentication (Email, Google, GitHub) | ✅ |
| PDF Report Generation (single + batch ZIP) | ✅ |
| Batch Analysis (CSV upload) | ✅ |
| URL-based Profile Scanning + Reddit Auto-Scraping | ✅ |
| AI Chatbot (Gemini, server-side proxied) | ✅ |
| Chrome Browser Extension (Manifest V3) | ✅ |
| Hyperparameter Tuning (Optuna) | ✅ |
| Docker Deployment (`docker-compose up`) | ✅ |
| CI/CD Pipeline (GitHub Actions) | ✅ |
| Backend Tests (68 pytest) | ✅ |
| Frontend Tests (28 Vitest) | ✅ |
| E2E Tests (Playwright) | ✅ |
| IEEE Research Paper | ✅ |

## Tech Stack

**Frontend:** React 19, Vite 8, Recharts, Firebase SDK, Vitest  
**Backend:** FastAPI, Uvicorn, Pydantic v2, HTTPX  
**ML:** XGBoost, Random Forest, Logistic Regression, SHAP, NumPy, Pandas  
**Auth/DB:** Firebase Auth + Firestore  
**AI Chat:** Groq (Llama 3.3-70B, primary) + Google Gemini (fallback), server-proxied  
**Testing:** Pytest (80+ tests), Vitest (28 tests), Playwright (E2E)  
**DevOps:** Docker, Docker Compose, GitHub Actions CI (4 jobs)  
**Deployment:** Railway (backend), Vercel (frontend)  

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and start everything
git clone https://github.com/YOUR_USERNAME/socialguard-ai.git
cd socialguard-ai

# Create .env (see backend/.env.example)
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Build and run
docker-compose up --build
```

- Frontend: http://localhost:4173
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/api/health

### Option 2: Local Development

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m uvicorn api:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

**Backend** (`backend/.env`):
```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
RATE_LIMIT=60/minute
GEMINI_API_KEY=your_gemini_api_key_here
FIREBASE_CREDENTIALS_PATH=./firebase-adminsdk.json
```

**Frontend** (`frontend/.env`):
```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_API_URL=http://127.0.0.1:8000
```

## Running Tests

```bash
# Backend (80+ tests)
cd backend
set TESTING=1
python -m pytest tests/ -v

# Frontend (28 tests)
cd frontend
npm test

# E2E (requires both servers running)
cd e2e
npx playwright test
```

## Public API

The public API allows programmatic access with API key authentication:

```bash
# Generate an API key from the /api-keys page, then:
curl -X POST http://localhost:8000/api/v1/analyze/instagram \
  -H "X-API-Key: sg_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"profile_pic": 0, "username_has_numbers": 1, "bio_present": 0, "posts": 0, "followers": 10, "following": 5000}'
```

## Model Performance

| Platform | Accuracy | CV Score | Data Source |
|---|---|---|---|
| Instagram | 98.60% | 98.8% | Real-world (Kaggle — 5,000 profiles) |
| Twitter | 99.29% | 99.6% | Real-world (Kaggle — 2,818 accounts) |
| Reddit | 94.00% | 95.0% | Real-world (dead-internet dataset) |
| Facebook | 95.00% | 96.0% | Real-world (Kaggle — 600 profiles) |
| LinkedIn | 99.17%* | 99.17%* | ⚗️ Realistic synthetic (no public dataset) |
| YouTube | 98.17%* | 98.63%* | ⚗️ Realistic synthetic (no public dataset) |

> \* LinkedIn and YouTube models are trained on realistic synthetic data generated to match real platform distributions.
> Metrics are evaluated on held-out synthetic samples and may not reflect real-world generalization.
> Predictions for these platforms include a synthetic-data transparency warning in the API response.

## Cloud Deployment

### Backend → Railway
```bash
railway login
railway up
```

### Frontend → Vercel
```bash
cd frontend
vercel --prod
```

Set `VITE_API_URL` to your Railway backend URL in Vercel environment variables:
```bash
vercel env add VITE_API_URL
# Enter: https://your-project.up.railway.app
```

> **Note**: `VITE_API_URL` is baked into the static bundle at build time.
> For local Docker dev, `http://localhost:8000` is correct (browser-to-host mapping).
> For production Vercel → Railway, set it to your Railway public URL.

## Security Notes

- ⚠️ **Never commit `.env` files or `firebase-adminsdk*.json`** — they are in `.gitignore`
- Three-layer middleware: Logging → Rate Limiting → Firebase Auth
- Dual authentication: Firebase tokens (web) + API keys (programmatic)
- Persistent rate limiting survives server restarts
- Gemini API key is kept server-side only

## License

MIT
