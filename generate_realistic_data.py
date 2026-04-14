"""
Generate REALISTIC synthetic datasets for LinkedIn and YouTube.
Unlike the original trivially-separable data, this produces overlapping
distributions with Gaussian noise, simulating real-world conditions.

Expected model accuracy: 85-92% (realistic, NOT 100%).

Usage: python generate_realistic_data.py
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_linkedin_data(n=3000):
    """Generate realistic LinkedIn profiles with overlapping distributions."""
    n_real = int(n * 0.6)  # 60/40 split (realistic imbalance)
    n_fake = n - n_real

    # ---- Real profiles ----
    real = pd.DataFrame({
        "connections": np.clip(np.random.lognormal(5.5, 1.0, n_real), 10, 5000).astype(int),
        "endorsements": np.clip(np.random.lognormal(2.5, 0.9, n_real), 0, 99).astype(int),
        "recommendations": np.clip(np.random.poisson(3, n_real), 0, 20),
        "posts_per_month": np.clip(np.random.lognormal(1.0, 0.8, n_real), 0, 30).round(1),
        "profile_views": np.clip(np.random.lognormal(4.0, 1.2, n_real), 0, 5000).astype(int),
        "account_age_days": np.clip(np.random.normal(1200, 600, n_real), 30, 5000).astype(int),
        "has_profile_pic": np.random.choice([0, 1], n_real, p=[0.05, 0.95]),
        "has_summary": np.random.choice([0, 1], n_real, p=[0.15, 0.85]),
        "has_experience": np.random.choice([0, 1], n_real, p=[0.08, 0.92]),
        "has_education": np.random.choice([0, 1], n_real, p=[0.10, 0.90]),
        "skills_count": np.clip(np.random.lognormal(2.0, 0.7, n_real), 0, 50).astype(int),
        "mutual_connections": np.clip(np.random.lognormal(3.0, 1.0, n_real), 0, 500).astype(int),
        "is_fake": 0,
    })

    # ---- Fake profiles (OVERLAPPING distributions — key for realism) ----
    fake = pd.DataFrame({
        "connections": np.clip(np.random.lognormal(3.5, 1.5, n_fake), 0, 3000).astype(int),
        "endorsements": np.clip(np.random.lognormal(1.0, 1.2, n_fake), 0, 50).astype(int),
        "recommendations": np.clip(np.random.poisson(0.5, n_fake), 0, 5),
        "posts_per_month": np.clip(np.random.exponential(0.5, n_fake), 0, 15).round(1),
        "profile_views": np.clip(np.random.lognormal(2.5, 1.5, n_fake), 0, 2000).astype(int),
        "account_age_days": np.clip(np.random.exponential(200, n_fake), 1, 3000).astype(int),
        "has_profile_pic": np.random.choice([0, 1], n_fake, p=[0.35, 0.65]),
        "has_summary": np.random.choice([0, 1], n_fake, p=[0.55, 0.45]),
        "has_experience": np.random.choice([0, 1], n_fake, p=[0.50, 0.50]),
        "has_education": np.random.choice([0, 1], n_fake, p=[0.45, 0.55]),
        "skills_count": np.clip(np.random.lognormal(1.0, 1.0, n_fake), 0, 30).astype(int),
        "mutual_connections": np.clip(np.random.lognormal(1.5, 1.2, n_fake), 0, 200).astype(int),
        "is_fake": 1,
    })

    df = pd.concat([real, fake], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    path = os.path.join(OUTPUT_DIR, "linkedin_realistic_dataset.csv")
    df.to_csv(path, index=False)
    print(f"✅ LinkedIn: {len(df)} profiles ({n_real} real, {n_fake} fake) → {path}")
    return df


def generate_youtube_data(n=3000):
    """Generate realistic YouTube channel data with overlapping distributions."""
    n_real = int(n * 0.55)  # 55/45 split
    n_fake = n - n_real

    # ---- Real channels ----
    real = pd.DataFrame({
        "subscriber_count": np.clip(np.random.lognormal(7.0, 2.5, n_real), 0, 1e7).astype(int),
        "video_count": np.clip(np.random.lognormal(4.0, 1.5, n_real), 1, 5000).astype(int),
        "total_views": np.clip(np.random.lognormal(10.0, 3.0, n_real), 100, 1e9).astype(int),
        "avg_likes_per_video": np.clip(np.random.lognormal(3.0, 1.5, n_real), 0, 10000).astype(int),
        "avg_comments_per_video": np.clip(np.random.lognormal(2.0, 1.2, n_real), 0, 2000).astype(int),
        "channel_age_days": np.clip(np.random.normal(1500, 700, n_real), 30, 6000).astype(int),
        "has_custom_thumbnail": np.random.choice([0, 1], n_real, p=[0.10, 0.90]),
        "has_description": np.random.choice([0, 1], n_real, p=[0.08, 0.92]),
        "uploads_per_month": np.clip(np.random.lognormal(1.0, 0.8, n_real), 0, 60).round(1),
        "engagement_rate": np.clip(np.random.beta(2, 20, n_real) * 100, 0.1, 15).round(2),
        "is_fake": 0,
    })

    # ---- Fake/bot channels (overlapping) ----
    fake = pd.DataFrame({
        "subscriber_count": np.clip(np.random.lognormal(4.0, 2.0, n_fake), 0, 500000).astype(int),
        "video_count": np.clip(np.random.lognormal(2.5, 1.8, n_fake), 0, 2000).astype(int),
        "total_views": np.clip(np.random.lognormal(6.0, 3.0, n_fake), 0, 1e7).astype(int),
        "avg_likes_per_video": np.clip(np.random.lognormal(1.0, 1.5, n_fake), 0, 500).astype(int),
        "avg_comments_per_video": np.clip(np.random.lognormal(0.5, 1.5, n_fake), 0, 200).astype(int),
        "channel_age_days": np.clip(np.random.exponential(250, n_fake), 1, 2000).astype(int),
        "has_custom_thumbnail": np.random.choice([0, 1], n_fake, p=[0.45, 0.55]),
        "has_description": np.random.choice([0, 1], n_fake, p=[0.40, 0.60]),
        "uploads_per_month": np.clip(np.random.exponential(2.0, n_fake), 0, 100).round(1),
        "engagement_rate": np.clip(np.random.beta(1, 50, n_fake) * 100, 0, 5).round(2),
        "is_fake": 1,
    })

    df = pd.concat([real, fake], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    path = os.path.join(OUTPUT_DIR, "youtube_realistic_dataset.csv")
    df.to_csv(path, index=False)
    print(f"✅ YouTube: {len(df)} channels ({n_real} real, {n_fake} fake) → {path}")
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("Generating REALISTIC datasets (overlapping distributions)")
    print("=" * 60)
    generate_linkedin_data()
    generate_youtube_data()
    print("\nDone! Now retrain models with:")
    print("  python train_linkedin.py")
    print("  python train_youtube.py")
