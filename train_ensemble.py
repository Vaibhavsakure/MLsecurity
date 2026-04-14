"""
Train ensemble models (Random Forest + Logistic Regression) for all 6 platforms.
XGBoost models are already trained — this adds RF and LR for weighted ensemble voting.

Usage:
    python train_ensemble.py
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

MODEL_DIR = os.path.join(os.path.dirname(__file__), "backend", "models")
EVAL_FILE = os.path.join(os.path.dirname(__file__), "evaluation_results", "evaluation_summary.json")

# ---------------------------------------------------------------------------
# Dataset loaders (same feature engineering as original training scripts)
# ---------------------------------------------------------------------------

def load_instagram():
    df = pd.read_csv("Instagram_fake_profile_dataset.csv")
    # Use all numeric columns as features, last column or 'fake' as target
    if "fake" in df.columns:
        y = df["fake"].values
        X = df.drop(columns=["fake"]).select_dtypes(include=[np.number]).values
    else:
        y = df.iloc[:, -1].values
        X = df.iloc[:, :-1].select_dtypes(include=[np.number]).values
    return X, y, "instagram"

def load_twitter():
    tweet_dir = "twitter_dataset"
    if os.path.exists(tweet_dir):
        files = [f for f in os.listdir(tweet_dir) if f.endswith(".csv")]
        if files:
            dfs = [pd.read_csv(os.path.join(tweet_dir, f)) for f in files]
            df = pd.concat(dfs, ignore_index=True)
        else:
            return None, None, "twitter"
    else:
        return None, None, "twitter"
    
    if "bot" in df.columns:
        y = df["bot"].values
        X = df.drop(columns=["bot"]).select_dtypes(include=[np.number]).values
    elif "label" in df.columns:
        y = df["label"].values
        X = df.drop(columns=["label"]).select_dtypes(include=[np.number]).values
    else:
        y = df.iloc[:, -1].values
        X = df.iloc[:, :-1].select_dtypes(include=[np.number]).values
    return X, y, "twitter"

def load_reddit():
    df = pd.read_csv("reddit_dead_internet_analysis_2026.csv")
    if "is_bot" in df.columns:
        y = df["is_bot"].values
        X = df.drop(columns=["is_bot"]).select_dtypes(include=[np.number]).values
    elif "label" in df.columns:
        y = df["label"].values
        X = df.drop(columns=["label"]).select_dtypes(include=[np.number]).values
    else:
        y = df.iloc[:, -1].values
        X = df.iloc[:, :-1].select_dtypes(include=[np.number]).values
    return X, y, "reddit"

def load_facebook():
    df = pd.read_csv("Facebook Spam Dataset.csv")
    if "spam" in df.columns:
        y = df["spam"].values
        X = df.drop(columns=["spam"]).select_dtypes(include=[np.number]).values
    elif "label" in df.columns:
        y = df["label"].values
        X = df.drop(columns=["label"]).select_dtypes(include=[np.number]).values
    else:
        y = df.iloc[:, -1].values
        X = df.iloc[:, :-1].select_dtypes(include=[np.number]).values
    return X, y, "facebook"

def generate_synthetic(platform, n_samples=2000, n_features=12, seed=42):
    """Generate synthetic data for LinkedIn/YouTube."""
    rng = np.random.RandomState(seed)
    X_real = rng.rand(n_samples // 2, n_features) * 0.6 + 0.4
    X_fake = rng.rand(n_samples // 2, n_features) * 0.4
    X = np.vstack([X_real, X_fake])
    y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    return X, y, platform

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_and_save(X, y, platform):
    """Train RF and LR models, save them, return CV scores."""
    if X is None or y is None:
        print(f"  ⚠️  Skipping {platform} — no data available")
        return None

    # Handle NaN
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    print(f"\n{'='*50}")
    print(f"  Training ensemble for: {platform.upper()}")
    print(f"  Samples: {len(y)} | Features: {X.shape[1]}")
    print(f"{'='*50}")

    results = {}

    # --- Random Forest ---
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X, y)
    rf_cv = cross_val_score(rf, X, y, cv=5, scoring="accuracy")
    rf_path = os.path.join(MODEL_DIR, f"{platform}_rf.pkl")
    joblib.dump(rf, rf_path)
    print(f"  ✅ Random Forest: {rf_cv.mean()*100:.2f}% (±{rf_cv.std()*100:.2f}%)")
    results["rf"] = {"accuracy": round(rf_cv.mean() * 100, 2), "std": round(rf_cv.std() * 100, 2)}

    # --- Logistic Regression ---
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_scaled, y)
    lr_cv = cross_val_score(lr, X_scaled, y, cv=5, scoring="accuracy")
    # Save both scaler and model together
    lr_path = os.path.join(MODEL_DIR, f"{platform}_lr.pkl")
    joblib.dump({"model": lr, "scaler": scaler}, lr_path)
    print(f"  ✅ Logistic Regression: {lr_cv.mean()*100:.2f}% (±{lr_cv.std()*100:.2f}%)")
    results["lr"] = {"accuracy": round(lr_cv.mean() * 100, 2), "std": round(lr_cv.std() * 100, 2)}

    return results


def main():
    print("🧠 SocialGuard AI — Ensemble Model Training")
    print("=" * 60)

    os.makedirs(MODEL_DIR, exist_ok=True)

    loaders = [
        load_instagram,
        load_twitter,
        load_reddit,
        load_facebook,
        lambda: generate_synthetic("linkedin", n_features=12, seed=42),
        lambda: generate_synthetic("youtube", n_features=10, seed=123),
    ]

    all_results = {}
    for loader in loaders:
        try:
            X, y, platform = loader()
            result = train_and_save(X, y, platform)
            if result:
                all_results[platform] = result
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Save ensemble metadata
    meta_path = os.path.join(MODEL_DIR, "ensemble_meta.json")
    with open(meta_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Ensemble training complete! Models saved to {MODEL_DIR}")
    print(f"   Metadata: {meta_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
