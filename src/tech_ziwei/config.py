from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str
    test_database_url: str = ""

    # Auth
    secret_key: str
    access_token_expire_minutes: int = 60

    # Claude API
    anthropic_api_key: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # App
    environment: str = "development"
    frontend_url: str = "http://localhost:3000"

    @property
    def async_database_url(self) -> str:
        """Always returns a postgresql+asyncpg:// URL for SQLAlchemy async engine."""
        url = self.database_url
        for prefix in ("postgres://", "postgresql+psycopg2://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+asyncpg://" + url[len(prefix):]
        return url

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()  # type: ignore[call-arg]
