from typing import Dict, Any, Optional
from app.services.scrapers.username import fetch_username_data

async def fetch_identity_task(query: str) -> Optional[Dict[str, Any]]:
    data = await fetch_username_data(query)
    return data
