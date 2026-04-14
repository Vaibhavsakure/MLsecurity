import requests
import json
import time

time.sleep(3)  # Wait for backend reload

BASE = "http://127.0.0.1:8000/api/predict"
results = {}

def test(platform, label, url, data):
    try:
        r = requests.post(url, json=data, timeout=10).json()
        results.setdefault(platform, []).append({
            "label": label,
            "probability": r.get("probability"),
            "risk_level": r.get("risk_level"),
        })
    except Exception as e:
        results.setdefault(platform, []).append({
            "label": label,
            "error": str(e)
        })

# INSTAGRAM (already working well)
test("instagram", "Real (good profile)", BASE + "/instagram",
     {"profile_pic": 1, "username_has_numbers": 0, "bio_present": 1,
      "posts": 150, "followers": 2000, "following": 500})
test("instagram", "Fake (suspicious)", BASE + "/instagram",
     {"profile_pic": 0, "username_has_numbers": 1, "bio_present": 0,
      "posts": 0, "followers": 5, "following": 3000})

# TWITTER
test("twitter", "Real (verified, active)", BASE + "/twitter",
     {"statuses_count": 5000, "followers_count": 3000, "friends_count": 500,
      "favourites_count": 8000, "listed_count": 50, "verified": 1,
      "default_profile_image": 0})
test("twitter", "Fake (bot-like)", BASE + "/twitter",
     {"statuses_count": 2, "followers_count": 0, "friends_count": 2000,
      "favourites_count": 0, "listed_count": 0, "verified": 0,
      "default_profile_image": 1})

# REDDIT
test("reddit", "Real (old, high karma)", BASE + "/reddit",
     {"account_age_days": 1500, "user_karma": 50000,
      "sentiment_score": 0.2, "avg_word_length": 5.5, "contains_links": 0})
test("reddit", "Fake (new bot)", BASE + "/reddit",
     {"account_age_days": 5, "user_karma": 10,
      "sentiment_score": 0.0, "avg_word_length": 3.0, "contains_links": 1})

# FACEBOOK - use realistic values based on dataset analysis
# Real users avg: friends=1253, following=1256, community=70, age=1122 days (~3yr), postshared=869, urlshared=85
# Spam users avg: friends=161, following=160, community=867, age=1657 days, postshared=2552, urlshared=1742
test("facebook", "Real (engaged user)", BASE + "/facebook",
     {"friends": 1200, "following": 1200, "community": 70, "age": 3.0,
      "postshared": 800, "urlshared": 80, "photos_videos": 800,
      "fpurls": 0.09, "fpphotos_videos": 0.5, "avgcomment_per_post": 0.5,
      "likes_per_post": 1.0, "tags_per_post": 0.5, "num_tags_per_post": 2.0})
test("facebook", "Fake (spam account)", BASE + "/facebook",
     {"friends": 160, "following": 160, "community": 800, "age": 4.5,
      "postshared": 2500, "urlshared": 1700, "photos_videos": 2500,
      "fpurls": 0.65, "fpphotos_videos": 0.3, "avgcomment_per_post": 7.0,
      "likes_per_post": 0.4, "tags_per_post": 1.0, "num_tags_per_post": 5.0})

with open("test_results2.json", "w") as f:
    json.dump(results, f, indent=2)

print("DONE - results in test_results2.json")
