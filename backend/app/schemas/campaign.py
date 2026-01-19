"""
Pydantic schemas for campaign copy generation.
Defines request and response models for the API.
"""

from pydantic import BaseModel, Field


class CampaignBrief(BaseModel):
    """Input schema for generating social media copy."""

    business_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the business",
        examples=["The Corner Bakery"],
    )

    business_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of business or industry",
        examples=["Independent bakery and café"],
    )

    target_audience: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Description of the target audience",
        examples=["Local families, office workers, and food enthusiasts in Manchester"],
    )

    campaign_goal: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="What the campaign aims to achieve",
        examples=["Promote our new afternoon tea menu for the spring season"],
    )

    key_messages: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Key points or messages to include",
        examples=["Locally sourced ingredients, traditional recipes, book online for 10% off"],
    )

    tone: str = Field(
        default="friendly and professional",
        max_length=200,
        description="Desired tone of voice",
        examples=["warm", "playful", "professional", "luxurious"],
    )

    platforms: list[str] = Field(
        default=["Instagram", "Facebook"],
        description="Social media platforms to target",
        examples=[["Instagram", "Facebook", "LinkedIn", "X"]],
    )

    include_hashtags: bool = Field(
        default=True,
        description="Whether to include relevant hashtags",
    )

    include_emoji: bool = Field(
        default=True,
        description="Whether to include emojis in the copy",
    )

    seasonal_hook: str | None = Field(
        default=None,
        max_length=200,
        description="Optional seasonal or event tie-in",
        examples=["Easter", "Bank Holiday Weekend", "Summer Sale"],
    )


class PlatformCopy(BaseModel):
    """Generated copy for a single platform."""

    platform: str = Field(
        ...,
        description="Social media platform name",
    )

    copy: str = Field(
        ...,
        description="Generated marketing copy",
    )

    character_count: int = Field(
        ...,
        description="Character count for the copy",
    )


class CopyGenerationResponse(BaseModel):
    """Response schema for generated social media copy."""

    success: bool = Field(
        default=True,
        description="Whether generation was successful",
    )

    business_name: str = Field(
        ...,
        description="Business name from the request",
    )

    copies: list[PlatformCopy] = Field(
        ...,
        description="Generated copy for each platform",
    )

    image_prompt: str = Field(
        ...,
        description="AI image generation prompt for DALL-E",
    )

    message: str | None = Field(
        default=None,
        description="Optional message or note",
    )


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Additional error details")
