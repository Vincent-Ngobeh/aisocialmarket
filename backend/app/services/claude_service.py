import anthropic
from anthropic import APIError, APIConnectionError, AuthenticationError, RateLimitError
from fastapi import HTTPException

from app.core.exceptions import AIServiceException, BadRequestException
from app.schemas.campaign import CampaignBrief, PlatformCopy, CopyGenerationResponse


PLATFORM_LIMITS = {
    "Instagram": 2200,
    "Facebook": 500,
    "LinkedIn": 700,
    "X": 280,
    "TikTok": 300,
}


def get_platform_limit(platform: str) -> int:
    return PLATFORM_LIMITS.get(platform, 500)


def build_copy_prompt(brief: CampaignBrief) -> str:
    platforms_info = "\n".join(
        f"- {p}: Maximum {get_platform_limit(p)} characters"
        for p in brief.platforms
    )

    seasonal_section = ""
    if brief.seasonal_hook:
        seasonal_section = f"""
Seasonal/Event Hook: {brief.seasonal_hook}
- Incorporate this seasonal element naturally into the copy
- Reference relevant UK cultural context if applicable
"""

    prompt = f"""You are an expert UK social media marketing copywriter. Generate engaging social media copy for a British small business.

IMPORTANT: You MUST write in British English. Use British spelling (colour, favourite, organise, centre, theatre, behaviour, programme, travelled, catalogue, defence, licence, practise, cheque, grey, tyre, aluminium, jewellery, mum, whilst, amongst).

## Business Details
- Business Name: {brief.business_name}
- Business Type: {brief.business_type}
- Target Audience: {brief.target_audience}

## Campaign Information
- Campaign Goal: {brief.campaign_goal}
- Key Messages: {brief.key_messages}
- Desired Tone: {brief.tone}
{seasonal_section}

## Content Requirements
- Include hashtags: {"Yes - add relevant UK-focused hashtags" if brief.include_hashtags else "No"}
- Include emojis: {"Yes - use sparingly and appropriately" if brief.include_emoji else "No"}

## Platforms and Limits
Generate copy for each platform, respecting character limits:
{platforms_info}

## Output Format
For each platform, provide:
1. The platform name
2. The complete copy (ready to post)
3. Ensure British spelling throughout

Also provide a DALL-E image prompt that would create an appropriate promotional image for this campaign. The prompt should:
- Describe a professional marketing image
- Match the brand tone
- Be suitable for UK audiences
- NOT include any text in the image (text will be added separately)

Respond in this exact format for each platform:

[PLATFORM: platform_name]
[COPY]
Your generated copy here...
[/COPY]

[IMAGE_PROMPT]
Your DALL-E prompt here...
[/IMAGE_PROMPT]
"""
    return prompt


def parse_claude_response(response_text: str, platforms: list[str]) -> tuple[list[PlatformCopy], str]:
    copies = []
    image_prompt = ""

    if "[IMAGE_PROMPT]" in response_text:
        start = response_text.find("[IMAGE_PROMPT]") + len("[IMAGE_PROMPT]")
        end = response_text.find("[/IMAGE_PROMPT]")
        if end > start:
            image_prompt = response_text[start:end].strip()

    for platform in platforms:
        marker = f"[PLATFORM: {platform}]"
        if marker in response_text:
            start = response_text.find(marker)
            copy_start = response_text.find("[COPY]", start) + len("[COPY]")
            copy_end = response_text.find("[/COPY]", start)

            if copy_start > len("[COPY]") - 1 and copy_end > copy_start:
                copy_text = response_text[copy_start:copy_end].strip()
                copies.append(
                    PlatformCopy(
                        platform=platform,
                        content=copy_text,
                        character_count=len(copy_text),
                    )
                )

    return copies, image_prompt


async def generate_copy(brief: CampaignBrief, api_key: str) -> CopyGenerationResponse:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_copy_prompt(brief)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        response_text = message.content[0].text
        copies, image_prompt = parse_claude_response(response_text, brief.platforms)

        if not copies:
            copies = [
                PlatformCopy(
                    platform=brief.platforms[0] if brief.platforms else "General",
                    content=response_text[:500],
                    character_count=min(len(response_text), 500),
                )
            ]

        if not image_prompt:
            image_prompt = f"Professional marketing photograph for {brief.business_type}, {brief.tone} style, suitable for UK audience, no text"

        return CopyGenerationResponse(
            success=True,
            business_name=brief.business_name,
            copies=copies,
            image_prompt=image_prompt,
            message="Copy generated successfully using British English",
        )

    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": "invalid_api_key",
                "detail": "Your Anthropic API key is invalid or has been revoked. Please check your key and try again.",
                "service": "anthropic",
            },
        )
    except RateLimitError:
        raise AIServiceException(
            service="Claude",
            detail="Anthropic rate limit exceeded. Please wait a moment and try again.",
        )
    except APIConnectionError:
        raise AIServiceException(
            service="Claude",
            detail="Could not connect to Claude API. Please check your internet connection and try again.",
        )
    except APIError as e:
        raise AIServiceException(
            service="Claude",
            detail=f"Claude API error: {str(e)}",
        )
