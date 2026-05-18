import aiohttp
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings

class HTTPClient:
    _session: Optional[aiohttp.ClientSession] = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=30)
            cls._session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return cls._session

    @classmethod
    async def close(cls):
        if cls._session:
            await cls._session.close()
            cls._session = None

    @classmethod
    async def start(cls):
        await cls.get_session()

    @classmethod
    async def stop(cls):
        await cls.close()

    @classmethod
    async def fetch(cls, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, retries: int = 2) -> Optional[Dict[str, Any]]:
        session = await cls.get_session()

        for attempt in range(retries + 1):
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        try:
                            return await response.json(content_type=None)
                        except Exception:
                            return None
                    elif response.status in (401, 403, 404):
                        return None
                    elif response.status >= 500:
                        pass
                    else:
                        return None
            except Exception:
                pass

            if attempt < retries:
                await asyncio.sleep(0.5 * (2 ** attempt))

        return None

client = HTTPClient
