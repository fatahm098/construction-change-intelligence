"""Uji koneksi provider LLM memakai pengaturan tersimpan.

Selalu mengembalikan `LLMSettingsTestResponse` (tidak pernah melempar error
HTTP), supaya tombol "Uji Koneksi" di UI bisa menampilkan pesan apa pun hasilnya.
"""

from __future__ import annotations

import httpx
from sqlalchemy.orm import Session

from ...kernel import settings_store
from ...schemas import LLMSettingsTestResponse

_CONNECT_TIMEOUT = 8.0


def test_connection(db: Session) -> LLMSettingsTestResponse:
    """Cek provider aktif: lokal selalu siap; ollama/openai/deepseek via HTTP."""
    cfg = settings_store.effective_settings(db)
    provider = (cfg["provider"] or "").strip().lower()
    model = cfg["model"]

    if provider == "local":
        return LLMSettingsTestResponse(
            ok=True, message="Provider lokal (offline) siap dipakai.", model=model
        )

    if provider == "ollama":
        base = cfg["base_url"].rstrip("/")
        try:
            with httpx.Client(timeout=_CONNECT_TIMEOUT) as client:
                resp = client.get(f"{base}/api/tags")
        except Exception as exc:  # noqa: BLE001 — pesan apa pun → hasil uji
            return LLMSettingsTestResponse(
                ok=False, message=f"Tidak dapat menghubungi Ollama: {exc}", model=model
            )
        if resp.status_code == 200:
            return LLMSettingsTestResponse(
                ok=True, message=f"Terhubung ke Ollama di {base}.", model=model
            )
        return LLMSettingsTestResponse(
            ok=False, message=f"Ollama membalas status {resp.status_code}.", model=model
        )

    if provider in ("openai", "deepseek"):
        api_key = settings_store.resolve_api_key(db, provider)
        if not api_key:
            return LLMSettingsTestResponse(
                ok=False, message="API key belum diisi.", model=model
            )
        base = cfg["base_url"].rstrip("/")
        try:
            with httpx.Client(timeout=_CONNECT_TIMEOUT) as client:
                resp = client.get(
                    f"{base}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
        except Exception as exc:  # noqa: BLE001
            return LLMSettingsTestResponse(
                ok=False, message=f"Tidak dapat menghubungi provider: {exc}", model=model
            )
        if resp.status_code == 200:
            return LLMSettingsTestResponse(
                ok=True, message=f"API key valid. Terhubung ke {base}.", model=model
            )
        if resp.status_code in (401, 403):
            return LLMSettingsTestResponse(
                ok=False, message="API key ditolak oleh provider.", model=model
            )
        return LLMSettingsTestResponse(
            ok=False, message=f"Provider membalas status {resp.status_code}.", model=model
        )

    return LLMSettingsTestResponse(
        ok=False, message=f"Provider '{cfg['provider']}' tidak dikenal.", model=model
    )
