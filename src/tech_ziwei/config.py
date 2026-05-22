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

    # App
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()  # type: ignore[call-arg]
