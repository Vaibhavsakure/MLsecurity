"""Quick test of all auto-fetch scrapers."""
import asyncio
from routes.scanner import (
    _fetch_reddit_data, _fetch_instagram_data,
    _fetch_twitter_data, _fetch_youtube_data,
)

async def test_all():
    print("=" * 60)
    print("  TESTING AUTO-FETCH SCRAPERS")
    print("=" * 60)

    # 1. Reddit
    print("\n[1] REDDIT (u/spez):")
    try:
        data = await _fetch_reddit_data("spez")
        karma = data.get("user_karma", "?")
        age = data.get("account_age_days", "?")
        print(f"    SUCCESS - karma={karma}, age={age} days")
    except Exception as e:
        print(f"    FAILED - {e}")

    # 2. Instagram
    print("\n[2] INSTAGRAM (@cristiano):")
    try:
        data = await _fetch_instagram_data("cristiano")
        print(f"    Result: {data}")
    except Exception as e:
        print(f"    FAILED - {e}")

    # 3. Twitter
    print("\n[3] TWITTER (@elonmusk):")
    try:
        data = await _fetch_twitter_data("elonmusk")
        print(f"    Result: tweets={data.get('statuses_count')}, followers={data.get('followers_count')}")
    except Exception as e:
        print(f"    FAILED - {e}")

    # 4. YouTube
    print("\n[4] YOUTUBE (@MrBeast):")
    try:
        data = await _fetch_youtube_data("MrBeast")
        print(f"    Result: subs={data.get('subscriber_count')}, videos={data.get('video_count')}")
    except Exception as e:
        print(f"    FAILED - {e}")

    print("\n" + "=" * 60)

asyncio.run(test_all())
