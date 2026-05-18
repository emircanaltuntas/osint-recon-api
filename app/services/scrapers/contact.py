from typing import Optional, Dict, List
from app.core.client import client
from app.core.config import settings
from app.api.models import BreachData

RAPIDAPI_BREACH_URL = "https://breachdirectory.p.rapidapi.com/"

async def fetch_email_breaches(email: str) -> List[BreachData]:
    params = {"func": "auto", "term": email}

    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "breachdirectory.p.rapidapi.com"
    }

    try:
        data = await client.fetch(RAPIDAPI_BREACH_URL, params=params, headers=headers)

        if not data:
            return []

        results = []
        if isinstance(data, list):
            raw_list = data
        else:
            raw_list = data.get("result", [])

        for item in raw_list:
            raw_sources = item.get("sources")

            if isinstance(raw_sources, str):
                sources = [s.strip() for s in raw_sources.split(",") if s.strip()]
            elif isinstance(raw_sources, list):
                sources = raw_sources
            elif "source" in item:
                sources = [item["source"]]
            else:
                sources = []

            for src in sources:
                results.append(BreachData(source=src, year=None))

        unique_results = {}
        for r in results:
            if r.source not in unique_results:
                unique_results[r.source] = r

        return list(unique_results.values())

    except Exception:
        return []

NUMVERIFY_API_URL = "http://apilayer.net/api/validate"

async def fetch_phone_data(phone: str) -> Optional[Dict]:
    params = {
        "access_key": settings.NUMVERIFY_API_KEY,
        "number": phone,
        "format": "1"
    }

    try:
        data = await client.fetch(NUMVERIFY_API_URL, params=params)

        if not data:
            return None

        if "error" in data:
            return None

        return {
            "valid": data.get("valid"),
            "number": data.get("number"),
            "format": data.get("international_format"),
            "country_code": data.get("country_code"),
            "country": data.get("country_name"),
            "location": data.get("location"),
            "carrier": data.get("carrier"),
            "line_type": data.get("line_type")
        }

    except Exception:
        return None
