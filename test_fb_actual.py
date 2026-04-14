import pandas as pd
import requests
import json

df = pd.read_csv("Facebook Spam Dataset.csv")
df = df.drop(columns=["profile id"])
df = df.rename(columns={"Label": "label"})

# Take one actual spam row and one actual real row from the dataset
spam_rows = df[df["label"]==1].head(3)
real_rows = df[df["label"]==0].head(3)

print("=== ACTUAL SPAM FROM DATASET ===")
for i, row in spam_rows.iterrows():
    print(row.to_dict())
print()
print("=== ACTUAL REAL FROM DATASET ===")
for i, row in real_rows.iterrows():
    print(row.to_dict())
print()

BASE = "http://127.0.0.1:8000/api/predict/facebook"

# Test with actual spam row
for i, row in spam_rows.iterrows():
    d = {
        "friends": int(row["#friends"]),
        "following": int(row["#following"]),
        "community": int(row["#community"]),
        "age": float(row["age"]) / 365.25,  # convert days to years since API converts back
        "postshared": int(row["#postshared"]),
        "urlshared": int(row["#urlshared"]),
        "photos_videos": int(row["#photos/videos"]),
        "fpurls": float(row["fpurls"]),
        "fpphotos_videos": float(row["fpphotos/videos"]),
        "avgcomment_per_post": float(row["avgcomment/post"]),
        "likes_per_post": float(row["likes/post"]),
        "tags_per_post": float(row["tags/post"]),
        "num_tags_per_post": float(row["#tags/post"]),
    }
    r = requests.post(BASE, json=d).json()
    print("SPAM row " + str(i) + ": prob=" + str(r.get("probability")) + " risk=" + r.get("risk_level", "?"))

print()

for i, row in real_rows.iterrows():
    d = {
        "friends": int(row["#friends"]),
        "following": int(row["#following"]),
        "community": int(row["#community"]),
        "age": float(row["age"]) / 365.25,
        "postshared": int(row["#postshared"]),
        "urlshared": int(row["#urlshared"]),
        "photos_videos": int(row["#photos/videos"]),
        "fpurls": float(row["fpurls"]),
        "fpphotos_videos": float(row["fpphotos/videos"]),
        "avgcomment_per_post": float(row["avgcomment/post"]),
        "likes_per_post": float(row["likes/post"]),
        "tags_per_post": float(row["tags/post"]),
        "num_tags_per_post": float(row["#tags/post"]),
    }
    r = requests.post(BASE, json=d).json()
    print("REAL row " + str(i) + ": prob=" + str(r.get("probability")) + " risk=" + r.get("risk_level", "?"))
