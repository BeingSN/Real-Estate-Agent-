# AI Real Estate Property Recommendation Agent

## Project Summary

This full-stack application is an AI-powered real estate assistant for Saudi Arabia. Users describe their property needs in natural language through a chat interface. The system extracts structured search criteria using an OpenRouter LLM, then matches those criteria against a synthetic dataset of 35 property listings using a deterministic scoring algorithm. The top 3–5 matches are returned with prices, key details, and a human-readable explanation for each recommendation.

## How AI is Used

The system uses a **two-step approach** that keeps AI and data strictly separated:

1. **Criteria extraction** — User input is sent to the OpenRouter LLM (`mistralai/mistral-7b-instruct` by default). The model returns structured JSON with fields like city, budget, bedrooms, property type, and furnishing. It does **not** recommend or describe properties.

2. **Deterministic matching** — The extracted JSON criteria are passed to a Python scoring algorithm that filters and ranks listings from `properties.json`. Results are sorted by relevance score and the top 5 are returned.

**The LLM never invents properties.** All recommendations come exclusively from `backend/data/properties.json`.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| AI | OpenRouter API (configurable model) |
| HTTP Client | httpx (async) |
| Validation | Pydantic v2 |
| Config | python-dotenv |
| Data | JSON files (properties + chat history) |

## Setup & Run

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Open .env and set OPENROUTER_API_KEY=your_actual_key
python main.py
# API: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI: http://localhost:5173
```

## Dataset

- **File:** `backend/data/properties.json`
- **Count:** 35 synthetic listings across Riyadh (15), Jeddah (10), Dammam (6), and Khobar (4)
- **Label:** Top-level `"note"` field clearly states SYNTHETIC DATA
- **Fields per listing:** id, title, city, district, property_type, purpose, price, price_unit, bedrooms, bathrooms, area_sqm, parking, furnishing, description, amenities, floor, year_built

## Matching Logic

### Phase 1 — Hard Filters

Listings are eliminated if they don't match:

- **City** (if specified)
- **Purpose** — Rent vs Sale
- **Price** exceeds user's budget (`max_price`)
- **Bedrooms** fewer than requested (`min_bedrooms`)
- **No parking** when parking is required

### Phase 2 — Soft Scoring (max ~100 points)

| Criterion              | Points |
|------------------------|--------|
| District exact match   | +20    |
| Property type match    | +15    |
| Furnishing exact match | +15    |
| Bathrooms sufficient   | +10    |
| Area sufficient        | +10    |
| Price ≤ 90% of budget  | +10    |
| Each amenity keyword   | +5     |
| Parking bonus          | +5     |

Top 5 results returned with a human-readable reason string per property.

## 5 Test Examples

### Test 1

**Input:** `"I need a furnished 2-bedroom apartment in Riyadh with parking, budget under 7,000 SAR/month"`

**Expected extracted criteria:** city=Riyadh, purpose=Rent, min_bedrooms=2, max_price=7000, furnishing=Furnished, parking_required=True

**Expected output:** 3–5 apartments from Riyadh, all furnished, all with parking, all ≤7,000 SAR/month. Examples: PROP-001 (Al Malaz, 6,500), PROP-004 (Hittin, 5,800), PROP-012 (Al Nakheel, 7,200 may be excluded if over budget).

---

### Test 2

**Input:** `"Looking to buy a villa in Jeddah, 4 bedrooms, around 2 million SAR"`

**Expected extracted criteria:** city=Jeddah, purpose=Sale, property_type=Villa, min_bedrooms=4, max_price=2000000

**Expected output:** Villas from Jeddah with 4+ bedrooms priced ≤2,000,000 SAR. Example: PROP-016 (Al Hamra, 2,200,000 — may be excluded), PROP-022 (Al Rawdah, 1,850,000).

---

### Test 3

**Input:** `"I want something cheap"`

**Expected:** is_unclear=True, agent asks: *"Could you give me more details? Which city, budget, rent or buy, bedrooms?"*

**Expected output:** No property cards — only the clarification question shown.

---

### Test 4

**Input:** `"Studio in Dammam, no more than 3,000 SAR, unfurnished"`

**Expected extracted criteria:** city=Dammam, property_type=Studio, purpose=Rent, max_price=3000, furnishing=Unfurnished

**Expected output:** Studio listings from Dammam matching price and furnishing — e.g. PROP-027 (Al Shula, 2,200 SAR) — or a no-match message if criteria are too strict.

---

### Test 5

**Input:** `"3 bedroom apartment in Al Olaya Riyadh for rent, semi-furnished, need parking and gym"`

**Expected extracted criteria:** city=Riyadh, district=Al Olaya, property_type=Apartment, purpose=Rent, min_bedrooms=3, furnishing=Semi-Furnished, parking_required=True, preferences="gym"

**Expected output:** Apartments scored higher when they have Gym in amenities. PROP-002 and PROP-009 (both Al Olaya, semi-furnished, with gym) should rank highest.

## Assumptions

- All prices are in SAR. Rent prices are monthly.
- Cities supported: Riyadh, Jeddah, Dammam, Khobar (dataset scope only)
- Dataset is entirely synthetic — not sourced from any real property listings API
- English language input only
- OpenRouter API key must be set in `backend/.env` (never hardcoded)

## Limitations

- No real Saudi property data (no Aqar/Bayut API integration)
- No map or image support
- No user accounts or saved searches
- English only — no Arabic input support
- Dataset of 35 listings is small; matching may return 0 results for niche queries
- LLM extraction quality depends on the chosen OpenRouter model

## Future Improvements

- Integrate real listings API (Aqar.sa, Bayut.sa)
- Arabic language support (bilingual extraction prompt)
- Map view using Leaflet or Google Maps
- Vector similarity search (pgvector / FAISS) for semantic matching
- User accounts, saved searches, and favourites
- Property image galleries
- WhatsApp/Telegram bot interface
