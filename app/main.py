from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api import endpoints
from app.core.client import client
from app.services.cache import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.start()
    yield
    await client.stop()
    await cache.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
