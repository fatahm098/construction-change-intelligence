"""Factory provider LLM.

Memilih implementasi provider berdasarkan `settings.llm_provider`.
"""

from __future__ import annotations

from ..config import settings
from .base import LLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    """Kembalikan provider LLM sesuai konfigurasi."""
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.llm_model,
            embedding_model=settings.llm_embedding_model,
        )

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY belum diisi di environment.")
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            embedding_model=settings.llm_embedding_model,
            base_url=settings.llm_base_url,
        )

    raise ValueError(
        f"LLM provider '{settings.llm_provider}' tidak dikenal. "
        "Pilihan: ollama, openai."
    )
