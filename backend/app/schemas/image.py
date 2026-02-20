from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Image generation prompt",
    )

    size: str = Field(
        default="1024x1024",
        description="Image size",
        pattern="^(1024x1024|1024x1792|1792x1024)$",
    )


class ImageGenerationResponse(BaseModel):
    success: bool = Field(default=True)
    image_url: str = Field(..., description="URL of the generated image")
    revised_prompt: str = Field(..., description="DALL-E's revised prompt")


class CampaignFullResponse(BaseModel):
    success: bool = Field(default=True)
    business_name: str
    copies: list = Field(..., description="Generated copy for each platform")
    image_prompt: str | None = Field(default=None, description="Prompt used for image generation")
    image_url: str | None = Field(default=None, description="Generated image URL")
    revised_image_prompt: str | None = Field(default=None)
    message: str | None = None
