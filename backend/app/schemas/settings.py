"""Skema pengaturan runtime LLM (API key).

Kontrak beku v1 (lihat `frontend/src/lib/types.ts`):
`LLMSettings` / `LLMSettingsUpdate` / `LLMTestResult`. API key bersifat
write-only — respons hanya membawa `has_api_key`, `api_key_masked`, dan
`source` (asal API key efektif).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class LLMSettingsResponse(BaseModel):
    """Pengaturan LLM efektif. API key mentah TIDAK pernah disertakan."""

    provider: str
    model: str
    base_url: str
    embedding_model: str
    has_api_key: bool
    api_key_masked: Optional[str] = None
    source: str  # "db" | "env" | "none"


class LLMSettingsUpdateRequest(BaseModel):
    """Payload pembaruan. Field None = jangan ubah; `api_key:""` = hapus key."""

    provider: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    embedding_model: Optional[str] = None
    api_key: Optional[str] = None


class LLMSettingsTestResponse(BaseModel):
    """Hasil uji koneksi ke provider LLM (HTTP selalu 200)."""

    ok: bool
    message: str
    model: str
