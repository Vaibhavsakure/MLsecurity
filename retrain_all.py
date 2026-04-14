import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "backend", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ====================================================================
# RETRAIN FACEBOOK MODEL
# ====================================================================
print("=" * 60)
print("RETRAINING FACEBOOK SPAM DETECTOR")
print("=" * 60)

df_fb = pd.read_csv("Facebook Spam Dataset.csv")
df_fb = df_fb.drop(columns=["profile id"])
df_fb = df_fb.rename(columns={"Label": "label"})
df_fb = df_fb.fillna(0)

X_fb = df_fb.drop(columns=["label"])
y_fb = df_fb["label"]

print("Features:", list(X_fb.columns))
print("Label distribution:", dict(y_fb.value_counts()))

X_train, X_test, y_train, y_test = train_test_split(X_fb, y_fb, test_size=0.2, random_state=42, stratify=y_fb)

fb_model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    eval_metric="logloss",
    random_state=42,
    scale_pos_weight=len(y_train[y_train==0]) / max(len(y_train[y_train==1]), 1)
)
fb_model.fit(X_train, y_train)

fb_pred = fb_model.predict(X_test)
print("Facebook Accuracy:", round(accuracy_score(y_test, fb_pred) * 100, 2), "%")
print(classification_report(y_test, fb_pred, target_names=["Real", "Spam"]))

# Cross-validation
cv_scores = cross_val_score(fb_model, X_fb, y_fb, cv=5, scoring="accuracy")
print("Cross-val accuracy:", round(cv_scores.mean() * 100, 2), "%")

joblib.dump(fb_model, os.path.join(MODEL_DIR, "facebook_spam_detector.pkl"))
print("Facebook model saved.\n")

# ====================================================================
# RETRAIN TWITTER MODEL  
# ====================================================================
print("=" * 60)
print("RETRAINING TWITTER BOT DETECTOR")
print("=" * 60)

users = pd.read_csv("twitter_dataset/users.csv")
fusers = pd.read_csv("twitter_dataset/fusers.csv")

# Add labels
users["label"] = 0  # genuine
fusers["label"] = 1  # fake

df_tw = pd.concat([users, fusers], ignore_index=True)

# Use the 14 features the model expects
feature_cols = [
    "id", "statuses_count", "followers_count", "friends_count",
    "favourites_count", "listed_count", "default_profile",
    "default_profile_image", "geo_enabled", "profile_use_background_image",
    "profile_background_tile", "utc_offset", "protected", "verified"
]

# Convert boolean columns to int
for col in feature_cols:
    if col in df_tw.columns:
        df_tw[col] = pd.to_numeric(df_tw[col], errors="coerce").fillna(0).astype(int)

X_tw = df_tw[feature_cols].fillna(0)
y_tw = df_tw["label"]

print("Features:", list(X_tw.columns))
print("Label distribution:", dict(y_tw.value_counts()))

X_train, X_test, y_train, y_test = train_test_split(X_tw, y_tw, test_size=0.2, random_state=42, stratify=y_tw)

tw_model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    eval_metric="logloss",
    random_state=42
)
tw_model.fit(X_train, y_train)

tw_pred = tw_model.predict(X_test)
print("Twitter Accuracy:", round(accuracy_score(y_test, tw_pred) * 100, 2), "%")
print(classification_report(y_test, tw_pred, target_names=["Real", "Bot"]))

cv_scores = cross_val_score(tw_model, X_tw, y_tw, cv=5, scoring="accuracy")
print("Cross-val accuracy:", round(cv_scores.mean() * 100, 2), "%")

joblib.dump(tw_model, os.path.join(MODEL_DIR, "twitter_bot_detector.pkl"))
print("Twitter model saved.\n")

# ====================================================================
# RETRAIN REDDIT MODEL
# ====================================================================
print("=" * 60)
print("RETRAINING REDDIT BOT DETECTOR")
print("=" * 60)

df_rd = pd.read_csv("reddit_dead_internet_analysis_2026.csv")
df_rd["karma_per_day"] = df_rd["user_karma"] / (df_rd["account_age_days"] + 1)
df_rd = df_rd.drop(columns=["comment_id", "subreddit", "bot_type_label", "bot_probability", "reply_delay_seconds"])
df_rd["contains_links"] = df_rd["contains_links"].astype(int)
df_rd = df_rd.rename(columns={"is_bot_flag": "label"})

X_rd = df_rd.drop(columns=["label"])
y_rd = df_rd["label"]

print("Features:", list(X_rd.columns))
print("Label distribution:", dict(y_rd.value_counts()))

X_train, X_test, y_train, y_test = train_test_split(X_rd, y_rd, test_size=0.2, random_state=42, stratify=y_rd)

rd_model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    eval_metric="logloss",
    random_state=42
)
rd_model.fit(X_train, y_train)

rd_pred = rd_model.predict(X_test)
print("Reddit Accuracy:", round(accuracy_score(y_test, rd_pred) * 100, 2), "%")
print(classification_report(y_test, rd_pred, target_names=["Real", "Bot"]))

cv_scores = cross_val_score(rd_model, X_rd, y_rd, cv=5, scoring="accuracy")
print("Cross-val accuracy:", round(cv_scores.mean() * 100, 2), "%")

joblib.dump(rd_model, os.path.join(MODEL_DIR, "reddit_bot_detector.pkl"))
print("Reddit model saved.\n")

print("=" * 60)
print("ALL MODELS RETRAINED SUCCESSFULLY")
print("=" * 60)
