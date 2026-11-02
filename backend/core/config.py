from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_WEAK_SECRETS = {
    "supersecretkey_please_change_in_production",
    "CHANGE_ME",
    "changeme",
    "secret",
    "password",
    "development",
    "insecure",
}


class Settings(BaseSettings):
    PROJECT_NAME: str = "BlueHire"
    API_V1_STR: str = "/api/v1"

    # DATABASE
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = Field(
        default="CHANGE_ME",
        description="Database password. Must be overridden via environment variable; never used in production as-is.",
    )
    POSTGRES_DB: str = "bluehire"
    DATABASE_URL: str | None = None

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # AUTHENTICATION
    SECRET_KEY: str = Field(
        default="CHANGE_ME",
        description="JWT signing secret. Mandatory. Must be a strong, randomly generated value; never commit this value.",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        value = v.strip()
        if not value or value in _WEAK_SECRETS or len(value) < 32:
            raise ValueError(
                "SECRET_KEY must be set to a strong, randomly generated value "
                "(at least 32 characters) and must not be a default or placeholder. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        return value

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
