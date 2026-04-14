"""
URL scanner with auto-fetch for Reddit + smart fallback for other platforms.
Reddit: Full auto-fetch via public JSON API.
Others: Detect platform + username, redirect to pre-filled form.
"""
import re
import datetime

from fastapi import APIRouter, HTTPException
import httpx

from schemas import UrlScanRequest, RedditInput
from routes.predictions import predict_reddit

router = APIRouter(prefix="/api", tags=["scanner"])

# ---------------------------------------------------------------------------
# Platform URL Patterns
# ---------------------------------------------------------------------------
PLATFORM_PATTERNS = {
    "instagram": r"(?:https?://)?(?:www\.)?instagram\.com/([^/?#]+)",
    "twitter": r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([^/?#]+)",
    "reddit": r"(?:https?://)?(?:www\.)?reddit\.com/(?:user|u)/([^/?#]+)",
    "facebook": r"(?:https?://)?(?:www\.)?facebook\.com/([^/?#]+)",
    "linkedin": r"(?:https?://)?(?:www\.)?linkedin\.com/in/([^/?#]+)",
    "youtube": r"(?:https?://)?(?:www\.)?youtube\.com/(?:@|channel/|c/)([^/?#]+)",
}


def _detect_platform(url: str):
    for platform, pattern in PLATFORM_PATTERNS.items():
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return platform, match.group(1)
    return None, None


# ---------------------------------------------------------------------------
# Lightweight Keyword-Based Sentiment Analyzer (zero dependencies)
# ---------------------------------------------------------------------------
_POSITIVE_WORDS = frozenset([
    "good", "great", "awesome", "excellent", "amazing", "love", "best",
    "happy", "wonderful", "fantastic", "helpful", "thanks", "thank",
    "nice", "cool", "perfect", "brilliant", "beautiful", "enjoy",
    "impressive", "outstanding", "superb", "positive", "recommend",
    "agree", "support", "appreciate", "useful", "interesting",
    "fun", "like", "glad", "well", "better", "improved",
])

_NEGATIVE_WORDS = frozenset([
    "bad", "terrible", "awful", "horrible", "hate", "worst", "ugly",
    "stupid", "boring", "annoying", "useless", "wrong", "fake",
    "scam", "spam", "toxic", "disgusting", "pathetic", "trash",
    "garbage", "lame", "sucks", "disappointed", "frustrating",
    "angry", "sad", "poor", "broken", "fail", "failed", "waste",
    "disagree", "unfortunately", "overrated", "mediocre",
])


def _compute_sentiment(text: str) -> float:
    """
    Compute a sentiment score between -1.0 and +1.0 from text.
    Uses a simple positive/negative word frequency approach.
    Returns 0.0 for empty text or balanced sentiment.
    """
    if not text:
        return 0.0
    words = re.findall(r'[a-z]+', text.lower())
    if not words:
        return 0.0
    pos_count = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in _NEGATIVE_WORDS)
    total_sentiment = pos_count + neg_count
    if total_sentiment == 0:
        return 0.0
    # Normalize: (pos - neg) / total_sentiment_words, clamped to [-1, 1]
    raw = (pos_count - neg_count) / total_sentiment
    return max(-1.0, min(1.0, raw))


# ---------------------------------------------------------------------------
# Reddit Scraper (RELIABLE — public JSON API, no auth needed)
# ---------------------------------------------------------------------------
async def _fetch_reddit_data(username: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {"User-Agent": "SocialGuardAI/5.0"}
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
        user_karma = data.get("total_karma", data.get("link_karma", 0) + data.get("comment_karma", 0))

        # Fetch comments for analysis
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
            all_comment_text = []
            link_count = 0
            for c in comments_data:
                body = c.get("data", {}).get("body", "")
                words = body.split()
                all_words.extend(words)
                all_comment_text.append(body)
                if "http" in body or "www." in body:
                    link_count += 1
            if all_words:
                avg_word_length = round(sum(len(w) for w in all_words) / len(all_words), 2)
            contains_links = 1 if comments_data and link_count > len(comments_data) * 0.3 else 0
            # Compute actual sentiment from comment text
            combined_text = " ".join(all_comment_text)
            sentiment_score = _compute_sentiment(combined_text)

        return {
            "account_age_days": account_age_days,
            "user_karma": user_karma,
            "sentiment_score": round(sentiment_score, 2),
            "avg_word_length": avg_word_length,
            "contains_links": contains_links,
        }


# ---------------------------------------------------------------------------
# Platform tips for manual input
# ---------------------------------------------------------------------------
PLATFORM_HELP = {
    "instagram": {
        "message": "Open the Instagram profile and fill in the details you can see:",
        "fields_help": {
            "profile_pic": "Does the profile have a custom profile picture? (1=yes, 0=no)",
            "username_has_numbers": "Does the username contain numbers?",
            "bio_present": "Does the profile have a bio? (1=yes, 0=no)",
            "posts": "Number of posts shown on the profile",
            "followers": "Number of followers",
            "following": "Number of accounts they follow",
        }
    },
    "twitter": {
        "message": "Open the Twitter/X profile and fill in these metrics:",
        "fields_help": {
            "statuses_count": "Total tweets/posts shown on the profile",
            "followers_count": "Number of followers",
            "friends_count": "Number of accounts they follow (Following)",
            "favourites_count": "Number of likes",
            "listed_count": "Number of lists they're on (visible in profile)",
            "verified": "Is the account verified? (1=yes, 0=no)",
            "default_profile_image": "Does it use the default egg/person avatar? (1=yes, 0=no)",
        }
    },
    "facebook": {
        "message": "Open the Facebook profile and fill in:",
        "fields_help": {
            "friends": "Number of friends",
            "following": "Number of pages/people they follow",
            "community": "Number of community groups",
        }
    },
    "linkedin": {
        "message": "Open the LinkedIn profile and fill in:",
        "fields_help": {
            "connections": "Number of connections (500+ counts as 500)",
            "endorsements": "Number of skill endorsements",
            "experience_years": "Approximate years of work experience",
        }
    },
    "youtube": {
        "message": "Open the YouTube channel and fill in:",
        "fields_help": {
            "subscriber_count": "Number of subscribers",
            "video_count": "Number of uploaded videos",
            "total_views": "Total channel views (from About page)",
        }
    },
}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/scan/url")
async def scan_url(req: UrlScanRequest):
    """Auto-detect platform from URL, auto-fetch for Reddit, guided input for others."""
    platform, username = _detect_platform(req.url)
    if not platform:
        raise HTTPException(
            status_code=400,
            detail="Could not detect platform from URL. Supported: Instagram, Twitter/X, Reddit, Facebook, LinkedIn, YouTube"
        )

    # --- Reddit: FULL AUTO ---
    if platform == "reddit":
        try:
            raw = await _fetch_reddit_data(username)
            reddit_input = RedditInput(**raw)
            result = predict_reddit(reddit_input)
            result["scanned_username"] = username
            result["scan_source"] = "url"
            result["auto_fetched"] = True
            result["fetched_data"] = raw
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to analyze Reddit profile: {str(e)}")

    # --- Other platforms: Smart redirect to pre-filled form ---
    help_info = PLATFORM_HELP.get(platform, {})
    prefilled = {}

    # Pre-fill what we CAN determine from the URL
    if platform == "instagram":
        prefilled["username_has_numbers"] = 1 if any(c.isdigit() for c in username) else 0
    
    return {
        "platform": platform,
        "username": username,
        "scan_source": "url",
        "auto_detected": True,
        "auto_fetched": False,
        "needs_manual_input": True,
        "message": help_info.get("message", f"Detected {platform.title()} profile for @{username}. Please enter the profile details manually."),
        "fields_help": help_info.get("fields_help", {}),
        "prefilled_data": prefilled,
        "why_manual": f"{platform.title()} requires login to view profile data, so we can't auto-fetch it. But we've detected the platform and username for you — just fill in the numbers you see on the profile!",
    }


@router.get("/fetch/reddit/{username}")
async def fetch_reddit_user(username: str):
    try:
        data = await _fetch_reddit_data(username)
        return {"success": True, "username": username, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Reddit data: {str(e)}")
