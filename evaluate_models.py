"""
SocialGuard AI — Comprehensive Model Evaluation & Comparison Script
====================================================================
Generates:
  1. Confusion matrices (PNG) for all platform models
  2. ROC curves with AUC scores (PNG)
  3. Model comparison: XGBoost vs Random Forest vs Logistic Regression
  4. Cross-validation results table
  5. Feature importance charts (PNG)
  6. Summary metrics JSON for API consumption

Output directory: evaluation_results/
"""
import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import joblib

# Platforms trained on synthetic data (transparently marked in output)
SYNTHETIC_PLATFORMS = {"LinkedIn", "YouTube"}

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUT_DIR = os.path.join(os.path.dirname(__file__), "evaluation_results")
os.makedirs(OUT_DIR, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.2

# Dark theme for all plots
plt.rcParams.update({
    "figure.facecolor": "#0a0e1a",
    "axes.facecolor": "#111827",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#e2e8f0",
    "text.color": "#e2e8f0",
    "xtick.color": "#94a3b8",
    "ytick.color": "#94a3b8",
    "grid.color": "#1e293b",
    "font.family": "sans-serif",
    "font.size": 11,
})

PLATFORM_COLORS = {
    "Instagram": "#E1306C",
    "Twitter": "#1DA1F2",
    "Reddit": "#FF4500",
    "Facebook": "#1877F2",
    "LinkedIn": "#0A66C2",
    "YouTube": "#FF0000",
}

# ---------------------------------------------------------------------------
# Data Loaders
# ---------------------------------------------------------------------------

def load_instagram():
    df = pd.read_csv("Instagram_fake_profile_dataset.csv")
    # The last column is the label
    cols = df.columns.tolist()
    label_col = cols[-1]
    X = df.drop(columns=[label_col]).select_dtypes(include=[np.number]).fillna(0)
    y = df[label_col].astype(int)
    return X, y, "Instagram"


def load_twitter():
    users = pd.read_csv("twitter_dataset/users.csv")
    fusers = pd.read_csv("twitter_dataset/fusers.csv")
    users["label"] = 0
    fusers["label"] = 1
    df = pd.concat([users, fusers], ignore_index=True)
    feature_cols = [
        "id", "statuses_count", "followers_count", "friends_count",
        "favourites_count", "listed_count", "default_profile",
        "default_profile_image", "geo_enabled", "profile_use_background_image",
        "profile_background_tile", "utc_offset", "protected", "verified"
    ]
    for col in feature_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    X = df[feature_cols].fillna(0)
    y = df["label"]
    return X, y, "Twitter"


def load_reddit():
    df = pd.read_csv("reddit_dead_internet_analysis_2026.csv")
    df["karma_per_day"] = df["user_karma"] / (df["account_age_days"] + 1)
    df = df.drop(columns=["comment_id", "subreddit", "bot_type_label", "bot_probability", "reply_delay_seconds"], errors="ignore")
    df["contains_links"] = df["contains_links"].astype(int)
    df = df.rename(columns={"is_bot_flag": "label"})
    X = df.drop(columns=["label"])
    y = df["label"]
    return X, y, "Reddit"


def load_facebook():
    df = pd.read_csv("Facebook Spam Dataset.csv")
    df = df.drop(columns=["profile id"], errors="ignore")
    df = df.rename(columns={"Label": "label"})
    df = df.fillna(0)
    X = df.drop(columns=["label"])
    y = df["label"]
    return X, y, "Facebook"


def load_linkedin_synthetic():
    np.random.seed(42)
    N = 2000
    real = pd.DataFrame({
        'connections': np.random.randint(50, 500, N//2),
        'endorsements': np.random.randint(5, 200, N//2),
        'recommendations': np.random.randint(0, 20, N//2),
        'skills_count': np.random.randint(5, 50, N//2),
        'experience_years': np.random.uniform(1, 30, N//2).round(1),
        'education_count': np.random.randint(1, 5, N//2),
        'profile_views': np.random.randint(10, 5000, N//2),
        'articles_published': np.random.randint(0, 30, N//2),
        'has_profile_pic': np.random.choice([0, 1], N//2, p=[0.05, 0.95]),
        'has_summary': np.random.choice([0, 1], N//2, p=[0.1, 0.9]),
        'account_age_months': np.random.randint(6, 180, N//2),
        'activity_frequency': np.random.uniform(0.3, 1.0, N//2).round(2),
        'label': 0
    })
    fake = pd.DataFrame({
        'connections': np.random.choice(np.concatenate([np.random.randint(0, 10, N//4), np.random.randint(490, 500, N//4)]), N//2),
        'endorsements': np.random.randint(0, 5, N//2),
        'recommendations': np.random.randint(0, 2, N//2),
        'skills_count': np.random.randint(0, 5, N//2),
        'experience_years': np.random.uniform(0, 3, N//2).round(1),
        'education_count': np.random.randint(0, 2, N//2),
        'profile_views': np.random.randint(0, 50, N//2),
        'articles_published': np.random.randint(0, 1, N//2),
        'has_profile_pic': np.random.choice([0, 1], N//2, p=[0.6, 0.4]),
        'has_summary': np.random.choice([0, 1], N//2, p=[0.7, 0.3]),
        'account_age_months': np.random.randint(0, 6, N//2),
        'activity_frequency': np.random.uniform(0.0, 0.2, N//2).round(2),
        'label': 1
    })
    df = pd.concat([real, fake], ignore_index=True).sample(frac=1, random_state=42)
    X = df.drop('label', axis=1)
    y = df['label']
    return X, y, "LinkedIn"


def load_youtube_synthetic():
    np.random.seed(42)
    N = 2000
    real = pd.DataFrame({
        'subscriber_count': np.random.randint(0, 50000, N//2),
        'video_count': np.random.randint(0, 500, N//2),
        'total_views': np.random.randint(100, 10000000, N//2),
        'account_age_days': np.random.randint(90, 5000, N//2),
        'avg_comment_length': np.random.uniform(20, 200, N//2).round(1),
        'comment_frequency': np.random.uniform(0.1, 5.0, N//2).round(2),
        'likes_ratio': np.random.uniform(0.3, 0.95, N//2).round(2),
        'has_profile_pic': np.random.choice([0, 1], N//2, p=[0.1, 0.9]),
        'has_channel_description': np.random.choice([0, 1], N//2, p=[0.2, 0.8]),
        'playlists_count': np.random.randint(0, 30, N//2),
        'label': 0
    })
    fake = pd.DataFrame({
        'subscriber_count': np.random.randint(0, 10, N//2),
        'video_count': np.random.randint(0, 2, N//2),
        'total_views': np.random.randint(0, 100, N//2),
        'account_age_days': np.random.randint(1, 60, N//2),
        'avg_comment_length': np.random.uniform(3, 30, N//2).round(1),
        'comment_frequency': np.random.uniform(10, 100, N//2).round(2),
        'likes_ratio': np.random.uniform(0.0, 0.1, N//2).round(2),
        'has_profile_pic': np.random.choice([0, 1], N//2, p=[0.7, 0.3]),
        'has_channel_description': np.random.choice([0, 1], N//2, p=[0.85, 0.15]),
        'playlists_count': np.random.randint(0, 1, N//2),
        'label': 1
    })
    df = pd.concat([real, fake], ignore_index=True).sample(frac=1, random_state=42)
    X = df.drop('label', axis=1)
    y = df['label']
    return X, y, "YouTube"


# ---------------------------------------------------------------------------
# Evaluation Engine
# ---------------------------------------------------------------------------

def evaluate_platform(X, y, platform_name):
    """Train 3 models, evaluate, generate all charts."""
    print(f"\n{'='*60}")
    print(f"  EVALUATING: {platform_name.upper()}")
    print(f"{'='*60}")
    print(f"  Samples: {len(X)} | Features: {X.shape[1]} | Positive ratio: {y.mean():.2%}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # --- Train 3 models ---
    models = {
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            eval_metric="logloss", random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=RANDOM_STATE
        ),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]),
    }

    results = {}
    model_colors = {"XGBoost": "#00d4ff", "Random Forest": "#8b5cf6", "Logistic Regression": "#ec4899"}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)

        results[name] = {
            "accuracy": round(acc * 100, 2),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "auc": round(roc_auc, 4),
            "cv_mean": round(cv_scores.mean() * 100, 2),
            "cv_std": round(cv_scores.std() * 100, 2),
            "confusion_matrix": cm.tolist(),
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
        }

        print(f"\n  {name}:")
        print(f"    Accuracy:  {acc:.4f}")
        print(f"    Precision: {prec:.4f}")
        print(f"    Recall:    {rec:.4f}")
        print(f"    F1-Score:  {f1:.4f}")
        print(f"    AUC:       {roc_auc:.4f}")
        print(f"    CV:        {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # --- Generate Confusion Matrix (XGBoost) ---
    cm = np.array(results["XGBoost"]["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(6, 5))
    color = PLATFORM_COLORS.get(platform_name, "#00d4ff")
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("custom", ["#111827", color])
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    classes = ["Genuine", "Fake/Bot"]
    tick_marks = np.arange(len(classes))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(classes, fontsize=12)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(classes, fontsize=12)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"),
                    ha="center", va="center", fontsize=18, fontweight="bold",
                    color="white" if cm[i, j] > cm.max() / 2 else "#e2e8f0")
    ax.set_xlabel("Predicted Label", fontsize=13, fontweight="bold")
    ax.set_ylabel("True Label", fontsize=13, fontweight="bold")
    ax.set_title(f"{platform_name} — Confusion Matrix (XGBoost)", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"{platform_name.lower()}_confusion_matrix.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # --- Generate ROC Curves (all 3 models) ---
    fig, ax = plt.subplots(figsize=(7, 6))
    for name in models:
        fpr = results[name]["fpr"]
        tpr = results[name]["tpr"]
        roc_auc = results[name]["auc"]
        ax.plot(fpr, tpr, color=model_colors[name], lw=2.5,
                label=f"{name} (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], "w--", alpha=0.3, lw=1)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate", fontsize=13, fontweight="bold")
    ax.set_ylabel("True Positive Rate", fontsize=13, fontweight="bold")
    ax.set_title(f"{platform_name} — ROC Curve Comparison", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="lower right", fontsize=11, facecolor="#111827", edgecolor="#334155")
    ax.grid(True, alpha=0.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"{platform_name.lower()}_roc_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # --- Feature Importance (XGBoost) ---
    xgb_model = models["XGBoost"]
    importances = xgb_model.feature_importances_
    feature_names = X.columns.tolist()
    sorted_idx = np.argsort(importances)[-min(12, len(importances)):]  # Top 12
    fig, ax = plt.subplots(figsize=(8, max(5, len(sorted_idx) * 0.45)))
    colors = [color] * len(sorted_idx)
    ax.barh(range(len(sorted_idx)), importances[sorted_idx], color=colors, alpha=0.85, height=0.6)
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_names[i] for i in sorted_idx], fontsize=11)
    ax.set_xlabel("Feature Importance", fontsize=13, fontweight="bold")
    ax.set_title(f"{platform_name} — Feature Importance (XGBoost)", fontsize=14, fontweight="bold", pad=15)
    ax.grid(True, axis="x", alpha=0.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"{platform_name.lower()}_feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.close()

    return results


# ---------------------------------------------------------------------------
# Global Comparison Chart
# ---------------------------------------------------------------------------

def generate_comparison_chart(all_results):
    """Generate a grouped bar chart comparing accuracies across all platforms."""
    platforms = list(all_results.keys())
    model_names = ["XGBoost", "Random Forest", "Logistic Regression"]
    model_colors_list = ["#00d4ff", "#8b5cf6", "#ec4899"]

    x = np.arange(len(platforms))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 7))
    for i, model in enumerate(model_names):
        accs = [all_results[p][model]["accuracy"] for p in platforms]
        bars = ax.bar(x + i * width, accs, width, label=model,
                      color=model_colors_list[i], alpha=0.85, edgecolor="none")
        for bar, acc in zip(bars, accs):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.5,
                    f"{acc}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Platform", fontsize=14, fontweight="bold")
    ax.set_ylabel("Accuracy (%)", fontsize=14, fontweight="bold")
    ax.set_title("Model Accuracy Comparison Across Platforms", fontsize=16, fontweight="bold", pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels(platforms, fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=12, facecolor="#111827", edgecolor="#334155")
    ax.grid(True, axis="y", alpha=0.15)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "model_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


def generate_cv_comparison(all_results):
    """Generate cross-validation comparison chart."""
    platforms = list(all_results.keys())
    model_names = ["XGBoost", "Random Forest", "Logistic Regression"]
    model_colors_list = ["#00d4ff", "#8b5cf6", "#ec4899"]

    x = np.arange(len(platforms))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 7))
    for i, model in enumerate(model_names):
        means = [all_results[p][model]["cv_mean"] for p in platforms]
        stds = [all_results[p][model]["cv_std"] for p in platforms]
        ax.bar(x + i * width, means, width, yerr=stds, label=model,
               color=model_colors_list[i], alpha=0.85, capsize=3, error_kw={"ecolor": "#64748b"})

    ax.set_xlabel("Platform", fontsize=14, fontweight="bold")
    ax.set_ylabel("Cross-Validation Accuracy (%)", fontsize=14, fontweight="bold")
    ax.set_title("5-Fold Cross-Validation Comparison", fontsize=16, fontweight="bold", pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels(platforms, fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=12, facecolor="#111827", edgecolor="#334155")
    ax.grid(True, axis="y", alpha=0.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "cv_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  SocialGuard AI — Model Evaluation Suite")
    print("=" * 60)

    loaders = [
        load_instagram,
        load_twitter,
        load_reddit,
        load_facebook,
        load_linkedin_synthetic,
        load_youtube_synthetic,
    ]

    all_results = {}
    summary = {}

    for loader in loaders:
        try:
            X, y, name = loader()
            results = evaluate_platform(X, y, name)
            all_results[name] = results

            # Build summary (XGBoost as primary)
            xgb = results["XGBoost"]
            is_synthetic = name in SYNTHETIC_PLATFORMS
            summary[name.lower()] = {
                "accuracy": xgb["accuracy"],
                "precision": xgb["precision"],
                "recall": xgb["recall"],
                "f1_score": xgb["f1_score"],
                "auc": xgb["auc"],
                "cv_mean": xgb["cv_mean"],
                "cv_std": xgb["cv_std"],
                "samples": len(X),
                "features": X.shape[1],
                "data_source": "synthetic" if is_synthetic else "real_world",
                "comparison": {
                    model: {
                        "accuracy": results[model]["accuracy"],
                        "auc": results[model]["auc"],
                        "f1_score": results[model]["f1_score"],
                    }
                    for model in results
                }
            }
            if is_synthetic:
                summary[name.lower()]["disclaimer"] = (
                    "This model was trained on synthetically generated data. "
                    "Metrics may not reflect real-world performance."
                )
        except Exception as e:
            print(f"\n  ❌ Error evaluating {loader.__name__}: {e}")
            import traceback
            traceback.print_exc()

    # Global comparison charts
    if all_results:
        print(f"\n{'='*60}")
        print("  GENERATING COMPARISON CHARTS")
        print(f"{'='*60}")
        generate_comparison_chart(all_results)
        generate_cv_comparison(all_results)

    # Save summary JSON
    with open(os.path.join(OUT_DIR, "evaluation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  ✅ ALL EVALUATIONS COMPLETE")
    print(f"  📁 Results saved to: {OUT_DIR}")
    print(f"  📊 Charts: {len(all_results) * 3 + 2} PNG files generated")
    print(f"  📄 Summary: evaluation_summary.json")
    print(f"{'='*60}")
