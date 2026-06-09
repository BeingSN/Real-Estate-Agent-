import json
from pathlib import Path
from fastapi import APIRouter
from datetime import datetime, timezone

from models.schemas import ChatRequest, ChatResponse
from services.extract_criteria import extract_criteria
from services.match_properties import match_properties
from services.chat_history import save_turn, get_all_history

router = APIRouter()

PROPERTIES_FILE = Path(__file__).parent.parent / "data" / "properties.json"


def load_listings():
    with open(PROPERTIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["listings"]


def build_criteria_summary(criteria) -> str:
    parts = []
    if criteria.city:            parts.append(f"City: {criteria.city}")
    if criteria.district:        parts.append(f"District: {criteria.district}")
    if criteria.property_type:   parts.append(f"Type: {criteria.property_type}")
    if criteria.purpose:         parts.append(f"Purpose: {criteria.purpose}")
    if criteria.max_price:       parts.append(f"Budget: up to {criteria.max_price:,.0f} SAR")
    if criteria.min_bedrooms:    parts.append(f"Min bedrooms: {criteria.min_bedrooms}")
    if criteria.min_bathrooms:   parts.append(f"Min bathrooms: {criteria.min_bathrooms}")
    if criteria.furnishing:      parts.append(f"Furnishing: {criteria.furnishing}")
    if criteria.min_area_sqm:    parts.append(f"Min area: {criteria.min_area_sqm} sqm")
    if criteria.parking_required: parts.append("Parking: required")
    if criteria.preferences:     parts.append(f"Preferences: {criteria.preferences}")
    return " | ".join(parts) if parts else "No specific criteria extracted"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    listings = load_listings()
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Extract criteria via LLM
    criteria = await extract_criteria(request.message)

    # Step 2: Handle unclear — ask follow-up question
    if criteria.is_unclear:
        question = criteria.clarification_question or (
            "Could you give me more details? For example: which city, "
            "your budget, whether you want to rent or buy, and how many bedrooms?"
        )
        save_turn({
            "user_message": request.message,
            "extracted_criteria": None,
            "recommendations": [],
            "assistant_response": question
        })
        return ChatResponse(
            assistant_message=question,
            extracted_criteria=criteria,
            recommendations=[],
            timestamp=now
        )

    # Step 3: Match against dataset
    matches = match_properties(criteria, listings)
    criteria_summary = build_criteria_summary(criteria)

    # Step 4: Build natural language response
    if not matches:
        assistant_msg = (
            f"I searched the dataset with your criteria ({criteria_summary}) "
            f"but found no matching properties. "
            f"Consider relaxing your budget, trying a different city, or adjusting the bedroom count."
        )
    else:
        count = len(matches)
        assistant_msg = (
            f"I found {count} matching propert{'y' if count == 1 else 'ies'} for you.\n"
            f"Search criteria used: {criteria_summary}."
        )

    # Step 5: Save full turn to chat_history.json
    save_turn({
        "user_message": request.message,
        "extracted_criteria": criteria.model_dump(),
        "recommendations": [r.model_dump() for r in matches],
        "assistant_response": assistant_msg
    })

    return ChatResponse(
        assistant_message=assistant_msg,
        extracted_criteria=criteria,
        recommendations=matches,
        timestamp=now
    )


@router.get("/history")
async def get_history():
    return get_all_history()
