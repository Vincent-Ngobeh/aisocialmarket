from openai import OpenAI
from openai import APIError, APIConnectionError, AuthenticationError, RateLimitError
from fastapi import HTTPException

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

    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": "invalid_api_key",
                "detail": "Your OpenAI API key is invalid or has been revoked. Please check your key and try again.",
                "service": "openai",
            },
        )
    except RateLimitError:
        raise AIServiceException(
            service="DALL-E",
            detail="OpenAI rate limit exceeded. Please wait a moment and try again.",
        )
    except APIConnectionError:
        raise AIServiceException(
            service="DALL-E",
            detail="Could not connect to OpenAI API. Please check your internet connection and try again.",
        )
    except APIError as e:
        raise AIServiceException(
            service="DALL-E",
            detail=f"OpenAI API error: {str(e)}",
        )
