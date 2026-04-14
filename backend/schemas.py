"""
Pydantic request/response schemas for all platform prediction endpoints.
All numeric fields include ge/le constraints for robust input validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class InstagramInput(BaseModel):
    profile_pic: int = Field(ge=0, le=1, description="1=has profile pic, 0=no pic")
    username_has_numbers: int = Field(ge=0, le=1, description="1=username contains numbers")
    bio_present: int = Field(ge=0, le=1, description="1=bio exists")
    posts: int = Field(ge=0, description="Number of posts")
    followers: int = Field(ge=0, description="Follower count")
    following: int = Field(ge=0, description="Following count")


class TwitterInput(BaseModel):
    # Core engagement metrics (required)
    statuses_count: int = Field(ge=0, description="Total tweets")
    followers_count: int = Field(ge=0, description="Follower count")
    friends_count: int = Field(ge=0, description="Following count")
    favourites_count: int = Field(ge=0, description="Total likes given")
    listed_count: int = Field(ge=0, description="Number of lists account is on")
    verified: int = Field(ge=0, le=1, description="1=verified account")
    default_profile_image: int = Field(ge=0, le=1, description="1=uses default avatar")
    # Profile completeness signals (optional — defaults to typical real-user values)
    geo_enabled: int = Field(default=0, ge=0, le=1, description="1=location enabled")
    has_bg_image: int = Field(default=1, ge=0, le=1, description="1=has background image")
    has_bg_tile: int = Field(default=0, ge=0, le=1, description="1=background is tiled")
    utc_offset: int = Field(default=0, description="UTC timezone offset in seconds")
    protected: int = Field(default=0, ge=0, le=1, description="1=protected/private account")


class RedditInput(BaseModel):
    account_age_days: int = Field(ge=0, description="Account age in days")
    user_karma: int = Field(ge=0, description="Total karma score")
    sentiment_score: float = Field(ge=-1.0, le=1.0, description="Comment sentiment (-1=negative, 1=positive)")
    avg_word_length: float = Field(ge=0, description="Average word length in comments")
    contains_links: int = Field(default=0, ge=0, le=1, description="1=frequently posts links")


class FacebookInput(BaseModel):
    friends: int = Field(ge=0, description="Friend count")
    following: int = Field(ge=0, description="Pages/people followed")
    community: int = Field(ge=0, description="Group memberships")
    age: float = Field(ge=0, description="Account age in years")
    postshared: int = Field(ge=0, description="Posts shared")
    urlshared: int = Field(ge=0, description="URLs shared")
    photos_videos: int = Field(ge=0, description="Photos/videos posted")
    fpurls: float = Field(ge=0, le=1, description="Fraction of posts that are URLs")
    fpphotos_videos: float = Field(ge=0, le=1, description="Fraction of posts with photos/videos")
    avgcomment_per_post: float = Field(ge=0, description="Average comments per post")
    likes_per_post: float = Field(ge=0, description="Average likes per post")
    tags_per_post: float = Field(ge=0, description="Average tags per post")
    num_tags_per_post: float = Field(ge=0, description="Number of tags per post")


class LinkedInInput(BaseModel):
    connections: int = Field(ge=0, description="Connection count")
    endorsements: int = Field(ge=0, description="Skill endorsement count")
    recommendations: int = Field(ge=0, description="Recommendation count")
    posts_per_month: float = Field(ge=0, description="Average posts per month")
    profile_views: int = Field(ge=0, description="Profile view count")
    account_age_days: int = Field(ge=0, description="Account age in days")
    has_profile_pic: int = Field(ge=0, le=1, description="1=has profile picture")
    has_summary: int = Field(ge=0, le=1, description="1=has About section")
    has_experience: int = Field(ge=0, le=1, description="1=has work experience")
    has_education: int = Field(ge=0, le=1, description="1=has education section")
    skills_count: int = Field(ge=0, description="Number of listed skills")
    mutual_connections: int = Field(ge=0, description="Mutual connection count")


class YouTubeInput(BaseModel):
    subscriber_count: int = Field(ge=0, description="Subscriber count")
    video_count: int = Field(ge=0, description="Uploaded video count")
    total_views: int = Field(ge=0, description="Total channel views")
    avg_likes_per_video: int = Field(ge=0, description="Average likes per video")
    avg_comments_per_video: int = Field(ge=0, description="Average comments per video")
    channel_age_days: int = Field(ge=0, description="Channel age in days")
    has_custom_thumbnail: int = Field(ge=0, le=1, description="1=uses custom thumbnails")
    has_description: int = Field(ge=0, le=1, description="1=channel has About description")
    uploads_per_month: float = Field(ge=0, description="Average uploads per month")
    engagement_rate: float = Field(ge=0, description="Engagement rate percentage")


class ReportRequest(BaseModel):
    platform: str
    probability: float = Field(ge=0, le=1)
    risk_level: str
    label: str
    message: str
    input_data: dict
    feature_importances: list
    timestamp: Optional[str] = None


class UrlScanRequest(BaseModel):
    url: str = Field(min_length=4, description="Profile URL to scan")


class BatchPredictRequest(BaseModel):
    records: List[dict] = Field(min_length=1, max_length=500, description="List of profile records (max 500)")
