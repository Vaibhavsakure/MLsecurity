"""
Train YouTube Bot Channel Detector using REALISTIC data.
Uses overlapping distributions for real-world applicable accuracy.
"""
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# Load realistic dataset
data = pd.read_csv("youtube_realistic_dataset.csv")
print(f"Loaded {len(data)} YouTube channels ({data['is_fake'].sum()} fake, {(data['is_fake']==0).sum()} real)")

X = data.drop("is_fake", axis=1)
y = data["is_fake"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss",
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {acc:.4f}")
print(classification_report(y_test, y_pred))

# Cross-validation
cv = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"5-Fold CV: {cv.mean():.4f} +/- {cv.std():.4f}")

# Save model
out = os.path.join("backend", "models", "youtube_bot_detector.pkl")
joblib.dump(model, out)
print(f"Model saved to {out}")
