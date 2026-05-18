from typing import Dict, Any, Optional
from app.core.client import client

IP_API_URL = "http://ip-api.com/json/{ip}"

async def fetch_ip_data(ip: str) -> Optional[Dict[str, Any]]:
    url = IP_API_URL.format(ip=ip)

    try:
        session = await client.get_session()
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            elif resp.status == 429:
                return None
    except Exception:
        return None

    return None
