from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PajamaTalk API"
    env: str = "local"
    database_url: str = "sqlite:///./pajamatalk.db"
    jwt_secret: str = "change-me-in-dev"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    gemini_api_key: str | None = None
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PAJAMA_",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
