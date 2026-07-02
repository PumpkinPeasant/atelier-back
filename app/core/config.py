from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "atelier-back"
    debug: bool = False

    postgres_user: str = "atelier"
    postgres_password: str = "atelier"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "atelier"

    # Auth / JWT. ОБЯЗАТЕЛЬНО переопределить secret_key в проде.
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Cookie-настройки. secure=True требуется для прода (HTTPS).
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
