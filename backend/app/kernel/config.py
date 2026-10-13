"""Konfigurasi aplikasi terpusat (env-driven).

Semua nilai dapat di-override lewat environment variable atau file `.env`
(di root repo atau di folder `backend/`).
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/kernel/config.py -> kernel -> app -> backend -> repo
BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent

DEFAULT_SQLITE_PATH = BACKEND_DIR / "construction.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Construction Change Intelligence API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Default ke SQLite lokal; override via DATABASE_URL (mis. Postgres di Docker).
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_PATH}"

    # Daftar origin CORS dipisah koma. Contoh: "http://localhost:3000,https://app.example.com"
    cors_origins: str = "http://localhost:3000"

    # Lapisan LLM (dipakai mulai Fase 2)
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2:3b"
    llm_base_url: str = "http://localhost:11434"
    llm_embedding_model: str = "nomic-embed-text"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
