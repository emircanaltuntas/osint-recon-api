import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        self.ttl = settings.CACHE_TTL_SECONDS

    async def get(self, key: str) -> Optional[dict]:
        try:
            val = await self.redis.get(key)
            return json.loads(val) if val else None
        except Exception:
            return None

    async def set(self, key: str, value: Any) -> None:
        try:
            await self.redis.set(key, json.dumps(value), ex=self.ttl)
        except Exception:
            pass

    async def close(self):
        await self.redis.close()

cache = CacheService()
