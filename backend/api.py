import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = FastAPI(title="SocialGuard AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load Models (paths relative to project root)
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..")

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
    profile_pic: int  # 0 or 1
    username_has_numbers: int  # 0 or 1
    bio_present: int  # 0 or 1
    posts: int
    followers: int
    following: int

class TwitterInput(BaseModel):
    statuses_count: int
    followers_count: int
    friends_count: int
    favourites_count: int
    listed_count: int
    verified: int  # 0 or 1
    default_profile_image: int  # 0 or 1

class RedditInput(BaseModel):
    account_age_days: int
    user_karma: int
    sentiment_score: float
    avg_word_length: float
    contains_links: int  # 0 or 1

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
        }
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
        1,   # fullname words (default)
        0,   # nums/length fullname
        0,   # name==username
        data.bio_present,
        0,   # external URL
        0,   # private
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
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "instagram"}


@app.post("/api/predict/twitter")
def predict_twitter(data: TwitterInput):
    if twitter_model is None:
        raise HTTPException(status_code=503, detail="Twitter model not loaded")

    features = np.array([[
        0,                          # id (placeholder, not meaningful for prediction)
        data.statuses_count,
        data.followers_count,
        data.friends_count,
        data.favourites_count,
        data.listed_count,
        0,                          # default_profile
        data.default_profile_image,
        0,                          # geo_enabled
        1,                          # profile_use_background_image
        0,                          # profile_background_tile
        0,                          # utc_offset
        0,                          # protected
        data.verified
    ]])

    prob = float(twitter_model.predict_proba(features)[0][1])
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "twitter"}


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
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "reddit"}


@app.post("/api/predict/facebook")
def predict_facebook(data: FacebookInput):
    if facebook_model is None:
        raise HTTPException(status_code=503, detail="Facebook model not loaded")

    # Convert age from years (user input) to days (model was trained on days)
    age_in_days = data.age * 365.25

    features = np.array([[
        data.friends,
        data.following,
        data.community,
        age_in_days,
        data.postshared,
        data.urlshared,
        data.photos_videos,
        data.fpurls,
        data.fpphotos_videos,
        data.avgcomment_per_post,
        data.likes_per_post,
        data.tags_per_post,
        data.num_tags_per_post
    ]])

    prob = float(facebook_model.predict_proba(features)[0][1])
    return {"probability": round(prob, 4), **_interpret(prob), "platform": "facebook"}
