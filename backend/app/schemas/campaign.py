from datetime import datetime
from pydantic import BaseModel, Field


class CampaignBrief(BaseModel):
    business_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    business_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    target_audience: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )
    campaign_goal: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )
    key_messages: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )
    tone: str = Field(
        default="friendly and professional",
        max_length=200,
    )
    platforms: list[str] = Field(
        default=["Instagram", "Facebook"],
    )
    include_hashtags: bool = Field(default=True)
    include_emoji: bool = Field(default=True)
    seasonal_hook: str | None = Field(default=None, max_length=200)


class PlatformCopy(BaseModel):
    platform: str
    content: str
    character_count: int


class CopyGenerationResponse(BaseModel):
    success: bool = Field(default=True)
    business_name: str
    copies: list[PlatformCopy]
    image_prompt: str | None = None
    message: str | None = None


class ErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: str
    detail: str | None = None


class CampaignRecord(BaseModel):
    id: int
    business_name: str
    business_type: str
    target_audience: str
    campaign_goal: str
    key_messages: str
    tone: str
    platforms: list[str]
    include_hashtags: bool
    include_emoji: bool
    seasonal_hook: str | None
    generated_copies: list[dict]
    image_prompt: str
    image_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    success: bool = True
    campaigns: list[CampaignRecord]
    total: int


class FreeTierStatusResponse(BaseModel):
    remaining: int
    limit: int
    resets_at: str
