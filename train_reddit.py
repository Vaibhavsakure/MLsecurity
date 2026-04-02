import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import joblib

print("Loading dataset...")
df = pd.read_csv("reddit_dead_internet_analysis_2026.csv")

print("Engineering features & dropping data leaks...")
# Create karma_per_day feature
df["karma_per_day"] = df["user_karma"] / (df["account_age_days"] + 1)

# Drop leaky and unnecessary columns
df = df.drop(columns=[
    "comment_id",
    "subreddit",
    "bot_type_label",
    "bot_probability",
    "reply_delay_seconds"
])

df["contains_links"] = df["contains_links"].astype(int)
df = df.rename(columns={"is_bot_flag": "label"})

X = df.drop(columns=["label"])
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training XGBoost Classifier...")
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
xgb_model.fit(X_train, y_train)

xgb_pred = xgb_model.predict(X_test)
acc = accuracy_score(y_test, xgb_pred)

print(f"New Realistic Model Accuracy: {acc * 100:.2f}%")

joblib.dump(xgb_model, "reddit_bot_detector.pkl")
print("Model successfully saved to reddit_bot_detector.pkl")
