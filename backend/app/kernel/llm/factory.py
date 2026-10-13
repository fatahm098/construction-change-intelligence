"""Factory provider LLM.

Memilih implementasi provider berdasarkan konfigurasi efektif
(DB > env > default, lihat `kernel.settings_store`).
"""

from __future__ import annotations

from ..config import settings
from .base import LLMProvider
from .local import LocalProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider


def _load_config() -> dict:
    """Konfigurasi efektif dari DB (bila tersedia), fallback ke environment."""
    try:
        from ...database import SessionLocal
        from ..settings_store import resolve_llm_config

        db = SessionLocal()
        try:
            return resolve_llm_config(db)
        finally:
            db.close()
    except Exception:  # noqa: BLE001 — DB belum siap → pakai env
        return {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "base_url": settings.llm_base_url,
            "embedding_model": settings.llm_embedding_model,
            "api_key": settings.openai_api_key,
        }


def get_llm_provider() -> LLMProvider:
    """Kembalikan provider LLM sesuai konfigurasi efektif."""
    cfg = _load_config()
    provider = (cfg["provider"] or "").lower()

    if provider == "local":
        return LocalProvider()

    if provider == "ollama":
        return OllamaProvider(
            base_url=cfg["base_url"],
            model=cfg["model"],
            embedding_model=cfg["embedding_model"],
        )

    if provider == "openai":
        if not cfg["api_key"]:
            raise ValueError("OPENAI_API_KEY belum diisi (env atau halaman Pengaturan).")
        return OpenAIProvider(
            api_key=cfg["api_key"],
            model=cfg["model"],
            embedding_model=cfg["embedding_model"],
            base_url=cfg["base_url"],
        )

    raise ValueError(
        f"LLM provider '{cfg['provider']}' tidak dikenal. "
        "Pilihan: local, ollama, openai."
    )
