from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str


class ExtractedCriteria(BaseModel):
    city: Optional[str] = None
    district: Optional[str] = None
    property_type: Optional[str] = None     # Apartment | Villa | Duplex | Studio
    purpose: Optional[str] = None           # Rent | Sale
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    parking_required: Optional[bool] = None
    furnishing: Optional[str] = None        # Furnished | Unfurnished | Semi-Furnished
    min_area_sqm: Optional[float] = None
    preferences: Optional[str] = None       # freeform, e.g. "near schools, gym, quiet"
    is_unclear: bool = False
    clarification_question: Optional[str] = None


class PropertyResult(BaseModel):
    id: str
    title: str
    city: str
    district: str
    property_type: str
    purpose: str
    price: float
    price_unit: str
    bedrooms: int
    bathrooms: int
    area_sqm: float
    parking: bool
    furnishing: str
    description: str
    score: float
    reasons: str                            # human-readable explanation of why this matches


class ChatResponse(BaseModel):
    assistant_message: str
    extracted_criteria: Optional[ExtractedCriteria] = None
    recommendations: Optional[List[PropertyResult]] = None
    timestamp: str
