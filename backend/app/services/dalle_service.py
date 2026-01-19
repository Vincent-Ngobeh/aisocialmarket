from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError

from app.core.exceptions import AIServiceException


async def generate_image(prompt: str, api_key: str, size: str = "1024x1024") -> dict:
    client = OpenAI(api_key=api_key)

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

    except RateLimitError:
        raise AIServiceException(
            service="DALL-E",
            detail="Rate limit exceeded. Please try again in a few moments.",
        )
    except APIConnectionError:
        raise AIServiceException(
            service="DALL-E",
            detail="Could not connect to OpenAI API. Please try again.",
        )
    except APIError as e:
        raise AIServiceException(
            service="DALL-E",
            detail=str(e),
        )
