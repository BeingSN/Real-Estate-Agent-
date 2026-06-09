import httpx
import json
import os
from dotenv import load_dotenv
from models.schemas import ExtractedCriteria

load_dotenv(override=True)

SYSTEM_PROMPT = """You are a real estate search criteria extractor for Saudi Arabia.
Given a user's natural language property request, extract structured search criteria.

Return ONLY a valid JSON object with EXACTLY these fields (use null for anything not mentioned by the user):
{
  "city": string or null,
  "district": string or null,
  "property_type": string or null,
  "purpose": string or null,
  "max_price": number or null,
  "min_bedrooms": integer or null,
  "min_bathrooms": integer or null,
  "parking_required": boolean or null,
  "furnishing": string or null,
  "min_area_sqm": number or null,
  "preferences": string or null,
  "is_unclear": boolean,
  "clarification_question": string or null
}

Strict rules:
- property_type must be exactly one of: Apartment, Villa, Duplex, Studio — or null
- purpose must be exactly "Rent" or "Sale" — or null
- furnishing must be exactly one of: Furnished, Unfurnished, Semi-Furnished — or null
- If the user says "rent", set purpose to "Rent". If "buy" or "purchase", set to "Sale".
- If the request has NO actionable criteria at all (e.g. only "something cheap", "a nice place"), set is_unclear to true and write a helpful clarification_question in English.
- If at least one criteria can be extracted, set is_unclear to false even if some fields are null.
- Return ONLY the JSON. No markdown, no backticks, no explanation."""


def _clarification_fallback(message: str | None = None) -> ExtractedCriteria:
    return ExtractedCriteria(
        is_unclear=True,
        clarification_question=message or (
            "I'd love to help you find a property! Could you tell me: "
            "Which city are you looking in? What's your budget? "
            "And are you looking to rent or buy?"
        ),
    )


async def extract_criteria(user_message: str) -> ExtractedCriteria:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_key_here":
        return _clarification_fallback(
            "AI service is not configured. Please set a valid OPENROUTER_API_KEY in backend/.env"
        )

    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Real Estate Agent"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
        data = response.json()
    except (httpx.HTTPError, json.JSONDecodeError):
        return _clarification_fallback(
            "I'm having trouble reaching the AI service right now. Please try again in a moment."
        )

    if response.status_code != 200 or "error" in data:
        error = data.get("error", {})
        if isinstance(error, dict):
            error = error.get("message", "OpenRouter API error")
        return _clarification_fallback(
            f"AI service error: {error}. Please check your OPENROUTER_API_KEY and model in backend/.env"
        )

    choices = data.get("choices")
    if not choices:
        return _clarification_fallback()

    content = choices[0].get("message", {}).get("content")
    if not content:
        return _clarification_fallback()

    raw = content.strip()

    # Strip markdown code fences if model adds them
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break

    try:
        parsed = json.loads(raw)
        return ExtractedCriteria(**parsed)
    except Exception:
        return _clarification_fallback()
