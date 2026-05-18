from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "OSINT API Aggregator"
    API_V1_STR: str = "/api/v1"
    RAPIDAPI_KEY: str
    NUMVERIFY_API_KEY: str
    RAPIDAPI_USERNAME_ENDPOINT: str = "https://social-media-data-api.p.rapidapi.com"
    RAPIDAPI_USERNAME_HOST: str = "social-media-data-api.p.rapidapi.com"
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
