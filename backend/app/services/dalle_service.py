from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError

from app.core.config import get_settings


settings = get_settings()


async def generate_image(prompt: str, size: str = "1024x1024") -> dict:
    """
    Generate an image using DALL-E API.

    Args:
        prompt: Image generation prompt
        size: Image size (1024x1024, 1024x1792, 1792x1024)

    Returns:
        Dict with image URL and revised prompt
    """
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is not configured")

    client = OpenAI(api_key=settings.openai_api_key)

    enhanced_prompt = f"{prompt}. Professional marketing photograph, high quality, suitable for social media advertising, no text overlays."

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=size,
            quality="standard",
            n=1,
        )

        return {
            "success": True,
            "image_url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt,
        }

    except RateLimitError as e:
        raise ValueError(f"Rate limit exceeded. Please try again later. {str(e)}")
    except APIConnectionError as e:
        raise ValueError(f"Could not connect to OpenAI API. {str(e)}")
    except APIError as e:
        raise ValueError(f"OpenAI API error: {str(e)}")
