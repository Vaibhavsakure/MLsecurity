import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib

print("Loading Facebook Spam Dataset...")
df = pd.read_csv("Facebook Spam Dataset.csv")

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Drop identifier column
df = df.drop(columns=["profile id"])

# Rename label column for consistency
df = df.rename(columns={"Label": "label"})

# Handle any missing values
df = df.fillna(0)

X = df.drop(columns=["label"])
y = df["label"]

print(f"Features: {list(X.columns)}")
print(f"Label distribution:\n{y.value_counts()}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training XGBoost Classifier...")
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
xgb_model.fit(X_train, y_train)

xgb_pred = xgb_model.predict(X_test)
acc = accuracy_score(y_test, xgb_pred)

print(f"\nFacebook Spam Detection Accuracy: {acc * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, xgb_pred))

joblib.dump(xgb_model, "facebook_spam_detector.pkl")
print("Model successfully saved to facebook_spam_detector.pkl")
