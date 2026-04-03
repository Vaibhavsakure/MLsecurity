import os
import io
import json
import datetime
import joblib
import numpy as np
import shap
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx

# PDF
from fpdf import FPDF

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = FastAPI(title="SocialGuard AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load Models
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def _load(name: str):
    path = os.path.join(MODEL_DIR, name)
    if not os.path.exists(path):
        return None
    return joblib.load(path)

instagram_model = _load("fake_account_detector.pkl")
twitter_model = _load("twitter_bot_detector.pkl")
reddit_model = _load("reddit_bot_detector.pkl")
facebook_model = _load("facebook_spam_detector.pkl")

# ---------------------------------------------------------------------------
# SHAP Explainers
# ---------------------------------------------------------------------------
SHAP_EXPLAINERS = {}

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
}

def _init_explainers():
    models = {
        "instagram": instagram_model,
        "twitter": twitter_model,
        "reddit": reddit_model,
        "facebook": facebook_model,
    }
    for name, model in models.items():
        if model is not None:
            try:
                SHAP_EXPLAINERS[name] = shap.TreeExplainer(model)
            except Exception:
                SHAP_EXPLAINERS[name] = None

_init_explainers()

def _get_shap_importances(platform: str, features: np.ndarray):
    explainer = SHAP_EXPLAINERS.get(platform)
    if explainer is None:
        return []
    try:
        sv = explainer.shap_values(features)
        # For binary classification, sv might be a list of two arrays
        if isinstance(sv, list):
            values = sv[1][0]  # class 1 (fake/bot)
        else:
            values = sv[0]
        names = FEATURE_NAMES.get(platform, [])
        importances = []
        for i, v in enumerate(values):
            name = names[i] if i < len(names) else f"Feature {i}"
            importances.append({"feature": name, "value": round(float(v), 4)})
        importances.sort(key=lambda x: abs(x["value"]), reverse=True)
        return importances[:8]  # Top 8 features
    except Exception:
        return []

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _interpret(prob: float):
    if prob < 0.3:
        return {"risk_level": "low", "label": "Low Risk", "message": "This account appears to be genuine."}
    elif prob < 0.6:
        return {"risk_level": "medium", "label": "Medium Risk", "message": "Some suspicious indicators detected. Proceed with caution."}
    else:
        return {"risk_level": "high", "label": "High Risk", "message": "High probability of being a fake or bot account."}

# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class InstagramInput(BaseModel):
    profile_pic: int
    username_has_numbers: int
    bio_present: int
    posts: int
    followers: int
    following: int

class TwitterInput(BaseModel):
    statuses_count: int
    followers_count: int
    friends_count: int
    favourites_count: int
    listed_count: int
    verified: int
    default_profile_image: int

class RedditInput(BaseModel):
    account_age_days: int
    user_karma: int
    sentiment_score: float
    avg_word_length: float
    contains_links: int

class FacebookInput(BaseModel):
    friends: int
    following: int
    community: int
    age: float
    postshared: int
    urlshared: int
    photos_videos: int
    fpurls: float
    fpphotos_videos: float
    avgcomment_per_post: float
    likes_per_post: float
    tags_per_post: float
    num_tags_per_post: float

class ReportRequest(BaseModel):
    platform: str
    probability: float
    risk_level: str
    label: str
    message: str
    input_data: dict
    feature_importances: list
    timestamp: Optional[str] = None

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "models": {
            "instagram": instagram_model is not None,
            "twitter": twitter_model is not None,
            "reddit": reddit_model is not None,
            "facebook": facebook_model is not None,
        },
        "shap": {k: v is not None for k, v in SHAP_EXPLAINERS.items()},
    }


@app.post("/api/predict/instagram")
def predict_instagram(data: InstagramInput):
    if instagram_model is None:
        raise HTTPException(status_code=503, detail="Instagram model not loaded")

    follower_following_ratio = data.followers / (data.following + 1)
    posts_per_follower = data.posts / (data.followers + 1)
    has_description = data.bio_present
    has_fullname = 1
    profile_completeness = data.profile_pic + has_description + has_fullname

    features = np.array([[
        data.profile_pic,
        0.7 if data.username_has_numbers == 1 else 0,
        1, 0, 0,
        data.bio_present,
        0, 0,
        data.posts,
        data.followers,
        data.following,
        follower_following_ratio,
        posts_per_follower,
        has_description,
        has_fullname,
        profile_completeness
    ]])

    prob = float(instagram_model.predict_proba(features)[0][1])
    importances = _get_shap_importances("instagram", features)
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "instagram",
            "feature_importances": importances, "input_data": data.model_dump()}


@app.post("/api/predict/twitter")
def predict_twitter(data: TwitterInput):
    if twitter_model is None:
        raise HTTPException(status_code=503, detail="Twitter model not loaded")

    features = np.array([[
        0,
        data.statuses_count,
        data.followers_count,
        data.friends_count,
        data.favourites_count,
        data.listed_count,
        0,
        data.default_profile_image,
        0, 1, 0, 0, 0,
        data.verified
    ]])

    prob = float(twitter_model.predict_proba(features)[0][1])
    importances = _get_shap_importances("twitter", features)
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "twitter",
            "feature_importances": importances, "input_data": data.model_dump()}


@app.post("/api/predict/reddit")
def predict_reddit(data: RedditInput):
    if reddit_model is None:
        raise HTTPException(status_code=503, detail="Reddit model not loaded")

    karma_per_day = data.user_karma / (data.account_age_days + 1)

    features = np.array([[
        data.account_age_days,
        data.user_karma,
        data.sentiment_score,
        data.avg_word_length,
        int(data.contains_links),
        karma_per_day
    ]])

    prob = float(reddit_model.predict_proba(features)[0][1])
    importances = _get_shap_importances("reddit", features)
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "reddit",
            "feature_importances": importances, "input_data": data.model_dump()}


@app.post("/api/predict/facebook")
def predict_facebook(data: FacebookInput):
    if facebook_model is None:
        raise HTTPException(status_code=503, detail="Facebook model not loaded")

    age_in_days = data.age * 365.25

    features = np.array([[
        data.friends, data.following, data.community, age_in_days,
        data.postshared, data.urlshared, data.photos_videos,
        data.fpurls, data.fpphotos_videos, data.avgcomment_per_post,
        data.likes_per_post, data.tags_per_post, data.num_tags_per_post
    ]])

    prob = float(facebook_model.predict_proba(features)[0][1])
    importances = _get_shap_importances("facebook", features)
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "facebook",
            "feature_importances": importances, "input_data": data.model_dump()}


# ---------------------------------------------------------------------------
# Auto-Fetch: Reddit (public JSON API, no auth needed)
# ---------------------------------------------------------------------------

@app.get("/api/fetch/reddit/{username}")
async def fetch_reddit_user(username: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"User-Agent": "SocialGuardAI/2.0"}
            resp = await client.get(
                f"https://www.reddit.com/user/{username}/about.json",
                headers=headers, follow_redirects=True
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Reddit user '{username}' not found")

            data = resp.json().get("data", {})
            created_utc = data.get("created_utc", 0)
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            account_age_days = int((now - created_utc) / 86400) if created_utc else 0

            # Fetch recent comments for sentiment/word analysis
            comments_resp = await client.get(
                f"https://www.reddit.com/user/{username}/comments.json?limit=25",
                headers=headers, follow_redirects=True
            )
            avg_word_length = 5.0
            sentiment_score = 0.0
            contains_links = 0

            if comments_resp.status_code == 200:
                comments_data = comments_resp.json().get("data", {}).get("children", [])
                all_words = []
                link_count = 0
                for c in comments_data:
                    body = c.get("data", {}).get("body", "")
                    words = body.split()
                    all_words.extend(words)
                    if "http" in body or "www." in body:
                        link_count += 1
                if all_words:
                    avg_word_length = round(sum(len(w) for w in all_words) / len(all_words), 2)
                contains_links = 1 if link_count > len(comments_data) * 0.3 else 0

            return {
                "success": True,
                "username": username,
                "data": {
                    "account_age_days": account_age_days,
                    "user_karma": data.get("total_karma", data.get("link_karma", 0) + data.get("comment_karma", 0)),
                    "sentiment_score": round(sentiment_score, 2),
                    "avg_word_length": avg_word_length,
                    "contains_links": contains_links,
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Reddit data: {str(e)}")


# ---------------------------------------------------------------------------
# PDF Report Generation
# ---------------------------------------------------------------------------

class SocialGuardPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(0, 180, 220)
        self.cell(0, 12, "SocialGuard AI", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "AI-Powered Fake Account Detection Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(6)
        self.set_draw_color(0, 180, 220)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"SocialGuard AI Report - Page {self.page_no()}", align="C")


@app.post("/api/report/generate")
def generate_report(req: ReportRequest):
    pdf = SocialGuardPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Timestamp
    ts = req.timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 6, f"Generated: {ts}", new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(4)

    # Platform
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, f"{req.platform.title()} Account Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Risk Summary Box
    risk_colors = {"low": (34, 197, 94), "medium": (245, 158, 11), "high": (239, 68, 68)}
    rc = risk_colors.get(req.risk_level, (100, 100, 100))

    pdf.set_fill_color(rc[0], rc[1], rc[2])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(90, 12, f"  {req.label}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, f"Probability: {round(req.probability * 100, 1)}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 6, req.message)
    pdf.ln(6)

    # Input Data Table
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "Input Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    alt = False
    for key, val in req.input_data.items():
        if alt:
            pdf.set_fill_color(240, 245, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        label = key.replace("_", " ").title()
        pdf.set_text_color(80, 80, 80)
        pdf.cell(90, 7, f"  {label}", fill=True)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, f"  {val}", fill=True, new_x="LMARGIN", new_y="NEXT")
        alt = not alt
    pdf.ln(6)

    # Feature Importances (SHAP)
    if req.feature_importances:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 8, "Key Contributing Factors (SHAP Analysis)", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        max_val = max(abs(f["value"]) for f in req.feature_importances) if req.feature_importances else 1
        for feat in req.feature_importances:
            bar_width = min(abs(feat["value"]) / (max_val + 0.001) * 80, 80)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(60, 7, f"  {feat['feature']}")
            if feat["value"] > 0:
                pdf.set_fill_color(239, 68, 68)  # red = higher risk
                direction = "Increases Risk"
            else:
                pdf.set_fill_color(34, 197, 94)  # green = lower risk
                direction = "Decreases Risk"
            pdf.cell(bar_width, 7, "", fill=True)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 7, f"  {direction} ({feat['value']:+.4f})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

    # Disclaimer
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 4, "Disclaimer: This report is generated by an AI model and should be used as a reference only. "
                         "The predictions are based on statistical patterns and may not be 100% accurate. "
                         "Always verify findings through additional investigation.")

    # Output
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    filename = f"SocialGuard_{req.platform.title()}_Report.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
