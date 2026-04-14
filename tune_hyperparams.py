"""
SocialGuard AI — Hyperparameter Tuning with Optuna
===================================================
Optimizes XGBoost hyperparameters for each platform model using
Bayesian optimization with 5-fold stratified cross-validation.

Usage:
    pip install optuna
    python tune_hyperparams.py

Output:
    tuning_results/best_params.json
    tuning_results/tuning_report.txt
"""
import os
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# Attempt to import optuna — provide helpful message if missing
try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
except ImportError:
    print("=" * 60)
    print("  Optuna is required for hyperparameter tuning.")
    print("  Install it with: pip install optuna")
    print("=" * 60)
    exit(1)

OUT_DIR = os.path.join(os.path.dirname(__file__), "tuning_results")
os.makedirs(OUT_DIR, exist_ok=True)

RANDOM_STATE = 42
N_TRIALS = 50  # Number of Optuna trials per platform
CV_FOLDS = 5

# Default hyperparams (current model config)
DEFAULT_PARAMS = {
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.1,
    "min_child_weight": 1,
    "subsample": 1.0,
    "colsample_bytree": 1.0,
    "gamma": 0,
    "reg_alpha": 0,
    "reg_lambda": 1,
}


# ---------------------------------------------------------------------------
# Data Loaders (same as evaluate_models.py — only real-world datasets)
# ---------------------------------------------------------------------------

def load_instagram():
    df = pd.read_csv("Instagram_fake_profile_dataset.csv")
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


# ---------------------------------------------------------------------------
# Optuna Objective
# ---------------------------------------------------------------------------

def create_objective(X, y):
    """Create an Optuna objective function for a given dataset."""
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10, log=True),
            "eval_metric": "logloss",
            "random_state": RANDOM_STATE,
        }

        model = XGBClassifier(**params)
        cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
        return scores.mean()

    return objective


# ---------------------------------------------------------------------------
# Run Tuning
# ---------------------------------------------------------------------------

def evaluate_params(X, y, params):
    """Evaluate a parameter set with cross-validation."""
    model = XGBClassifier(**params, eval_metric="logloss", random_state=RANDOM_STATE)
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
    return scores.mean(), scores.std()


if __name__ == "__main__":
    print("=" * 60)
    print("  SocialGuard AI - Hyperparameter Tuning (Optuna)")
    print("=" * 60)

    loaders = [load_instagram, load_twitter, load_reddit, load_facebook]
    all_results = {}
    report_lines = []

    for loader in loaders:
        try:
            X, y, name = loader()
            print(f"\n{'='*60}")
            print(f"  TUNING: {name.upper()}  ({len(X)} samples, {X.shape[1]} features)")
            print(f"{'='*60}")

            # Baseline (default params)
            default_mean, default_std = evaluate_params(X, y, DEFAULT_PARAMS)
            print(f"  Default F1:  {default_mean:.4f} +/- {default_std:.4f}")

            # Optuna optimization
            study = optuna.create_study(direction="maximize")
            objective = create_objective(X, y)
            study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

            best_params = study.best_params
            best_mean, best_std = evaluate_params(X, y, best_params)

            improvement = best_mean - default_mean
            print(f"  Tuned F1:    {best_mean:.4f} +/- {best_std:.4f}")
            print(f"  Improvement: {'+' if improvement >= 0 else ''}{improvement:.4f}")
            print(f"  Best Params: {json.dumps(best_params, indent=2)}")

            all_results[name.lower()] = {
                "default_f1": round(default_mean, 4),
                "tuned_f1": round(best_mean, 4),
                "improvement": round(improvement, 4),
                "best_params": best_params,
                "n_trials": N_TRIALS,
                "samples": len(X),
                "features": X.shape[1],
            }

            report_lines.append(f"\n{name}:")
            report_lines.append(f"  Default F1: {default_mean:.4f} ± {default_std:.4f}")
            report_lines.append(f"  Tuned F1:   {best_mean:.4f} ± {best_std:.4f}")
            report_lines.append(f"  Δ F1:       {improvement:+.4f}")
            report_lines.append(f"  Params:     {best_params}")

        except Exception as e:
            print(f"  [ERROR] Error tuning {name}: {e}")
            import traceback
            traceback.print_exc()

    # Save results
    with open(os.path.join(OUT_DIR, "best_params.json"), "w") as f:
        json.dump(all_results, f, indent=2)

    with open(os.path.join(OUT_DIR, "tuning_report.txt"), "w", encoding="utf-8") as f:
        f.write("SocialGuard AI - Hyperparameter Tuning Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Trials per platform: {N_TRIALS}\n")
        f.write(f"CV folds: {CV_FOLDS}\n")
        f.write("\n".join(report_lines))
        f.write("\n")

    print(f"\n{'='*60}")
    print(f"  [DONE] TUNING COMPLETE")
    print(f"  Results: {OUT_DIR}/best_params.json")
    print(f"  Report:  {OUT_DIR}/tuning_report.txt")

    # Summary comparison table
    print(f"\n  {'Platform':<12} {'Default F1':>12} {'Tuned F1':>12} {'Delta':>8}")
    print(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*8}")
    for name, data in all_results.items():
        delta = data['improvement']
        print(f"  {name:<12} {data['default_f1']:>12.4f} {data['tuned_f1']:>12.4f} {delta:>+8.4f}")

    print(f"{'='*60}")
