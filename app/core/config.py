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

    # CORS: список origin'ов фронта через запятую. Со звёздочкой ("*")
    # cookie не работают — нужны конкретные адреса.
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # S3 / MinIO. Для локалки — значения из docker-compose.
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "atelier"
    s3_region: str = "us-east-1"
    # Базовый URL для публичных ссылок на файлы (CDN в проде).
    # Если пусто — берётся {s3_endpoint_url}/{s3_bucket}.
    s3_public_url: str | None = None

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        # Origin приходит без завершающего слэша — срезаем его на всякий случай.
        return [
            o.strip().rstrip("/")
            for o in self.cors_origins.split(",")
            if o.strip()
        ]

    @computed_field
    @property
    def s3_public_base(self) -> str:
        return (self.s3_public_url or f"{self.s3_endpoint_url}/{self.s3_bucket}").rstrip(
            "/"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
