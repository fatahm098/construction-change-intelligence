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

    # Lapisan LLM (pluggable). Default: DeepSeek (OpenAI-compatible).
    llm_provider: str = "deepseek"
    llm_model: str = "deepseek-chat"
    # DeepSeek belum menyediakan endpoint embeddings; RAG memakai hashing lokal
    # (lihat `kernel/llm/deepseek.py`). Nilai ini hanya informatif di UI.
    llm_embedding_model: str = "deepseek-embedding"
    # Base URL untuk provider OpenAI-compatible (default DeepSeek).
    # Untuk ollama, pakai ollama_base_url.
    llm_base_url: str = "https://api.deepseek.com/v1"

    # Provider embedding terpisah dari LLM chat. "hash" = offline (default),
    # "openai" = endpoint OpenAI-compatible sungguhan (embedding semantik).
    embedding_provider: str = "hash"
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str | None = None
    deepseek_api_key: str | None = None
    anthropic_api_key: str | None = None

    # --- Fase 4: Auth & multi-tenant ---
    auth_enabled: bool = False  # aktifkan setelah user dibuat
    jwt_secret: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720

    # --- Fase 4: Background jobs ---
    redis_url: str = "redis://localhost:6379/0"
    jobs_enabled: bool = False  # True → analisis dijalankan async via worker

    # --- Observability / logging ---
    log_level: str = "INFO"  # DEBUG | INFO | WARNING | ERROR
    log_json: bool = True  # True → log JSON terstruktur; False → teks (dev)

    # --- Pengaturan runtime (API key LLM) ---
    # Kunci untuk enkripsi API key yang disimpan di DB. Bila None → diturunkan
    # dari jwt_secret (fallback dev). Untuk produksi set eksplisit (string acak).
    settings_encryption_key: str | None = None

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
