from models.schemas import ExtractedCriteria, PropertyResult
from typing import List, Dict, Any


def match_properties(criteria: ExtractedCriteria, listings: List[Dict[str, Any]]) -> List[PropertyResult]:
    """
    MATCHING LOGIC:

    Phase 1 — Hard Filters (eliminate non-matching listings entirely):
      - City mismatch → exclude
      - Purpose mismatch (Rent vs Sale) → exclude
      - Price exceeds max_price → exclude
      - Bedrooms fewer than min_bedrooms → exclude
      - Parking required but listing has no parking → exclude

    Phase 2 — Soft Scoring (rank remaining listings, max ~100 points):
      - District match:           +20
      - Property type match:      +15
      - Furnishing exact match:   +15
      - Bathrooms >= requested:   +10
      - Area >= requested sqm:    +10
      - Price <= 90% of budget:   +10  (great deal bonus)
      - Amenity keyword match:    +5 per match, max +15
      - Parking included (bonus): +5  (when not strictly required)

    Returns top 5 by score, each with a human-readable reasons string.
    """
    results = []

    for prop in listings:

        # ── HARD FILTERS ──────────────────────────────────────────────
        if criteria.city:
            if prop["city"].strip().lower() != criteria.city.strip().lower():
                continue

        if criteria.purpose:
            if prop["purpose"].strip().lower() != criteria.purpose.strip().lower():
                continue

        if criteria.max_price is not None:
            if prop["price"] > criteria.max_price:
                continue

        if criteria.min_bedrooms is not None:
            if prop["bedrooms"] < criteria.min_bedrooms:
                continue

        if criteria.parking_required is True:
            if not prop.get("parking", False):
                continue

        # ── SOFT SCORING ──────────────────────────────────────────────
        score = 0.0
        reason_parts = []

        # Bedrooms — always mention if user specified
        if criteria.min_bedrooms is not None:
            reason_parts.append(f"{prop['bedrooms']}-bedroom")

        # District
        if criteria.district:
            if prop["district"].strip().lower() == criteria.district.strip().lower():
                score += 20
                reason_parts.append(f"in {prop['district']} as requested")

        # Property type
        if criteria.property_type:
            if prop["property_type"].strip().lower() == criteria.property_type.strip().lower():
                score += 15
                reason_parts.append(prop["property_type"].lower())

        # Furnishing
        if criteria.furnishing:
            if prop["furnishing"].strip().lower() == criteria.furnishing.strip().lower():
                score += 15
                reason_parts.append(prop["furnishing"].lower())

        # Bathrooms
        if criteria.min_bathrooms is not None:
            if prop["bathrooms"] >= criteria.min_bathrooms:
                score += 10
                reason_parts.append(f"{prop['bathrooms']} bathrooms")

        # Area
        if criteria.min_area_sqm is not None:
            if prop["area_sqm"] >= criteria.min_area_sqm:
                score += 10
                reason_parts.append(f"{prop['area_sqm']} sqm")

        # Price efficiency
        if criteria.max_price is not None:
            if prop["price"] <= criteria.max_price * 0.90:
                score += 10
                reason_parts.append(
                    f"priced at {prop['price']:,.0f} {prop['price_unit']} — under your budget"
                )
            else:
                reason_parts.append(
                    f"priced at {prop['price']:,.0f} {prop['price_unit']}"
                )
        else:
            reason_parts.append(f"{prop['price']:,.0f} {prop['price_unit']}")

        # Parking bonus
        if prop.get("parking") and not criteria.parking_required:
            score += 5
            reason_parts.append("includes parking")
        elif prop.get("parking") and criteria.parking_required:
            reason_parts.append("has parking")

        # Amenity keyword matching against preferences
        if criteria.preferences:
            prefs_lower = criteria.preferences.lower()
            amenity_hits = 0
            matched_amenities = []
            for amenity in prop.get("amenities", []):
                amenity_words = amenity.lower().split()
                if any(word in prefs_lower for word in amenity_words):
                    amenity_hits += 1
                    matched_amenities.append(amenity)
            amenity_score = min(amenity_hits * 5, 15)
            score += amenity_score
            if matched_amenities:
                reason_parts.append(f"amenities include: {', '.join(matched_amenities)}")

        reasons = "Why it fits: " + "; ".join(reason_parts) + "." if reason_parts else "Meets your search criteria."

        results.append(PropertyResult(
            id=prop["id"],
            title=prop["title"],
            city=prop["city"],
            district=prop["district"],
            property_type=prop["property_type"],
            purpose=prop["purpose"],
            price=prop["price"],
            price_unit=prop["price_unit"],
            bedrooms=prop["bedrooms"],
            bathrooms=prop["bathrooms"],
            area_sqm=prop["area_sqm"],
            parking=prop["parking"],
            furnishing=prop["furnishing"],
            description=prop["description"],
            score=round(score, 1),
            reasons=reasons
        ))

    # Sort descending by score, return top 5
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:5]
