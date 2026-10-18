"""Akses pengaturan runtime (baris tunggal `app_settings`) + resolusi API key.

Prioritas nilai: kolom DB → default environment (`settings`). API key disimpan
terenkripsi (lihat `kernel.crypto`) dan hanya didekripsi di backend — tidak
pernah dikirim ke klien. Key dari env mengikuti provider aktif
(`DEEPSEEK_API_KEY` untuk deepseek, `OPENAI_API_KEY` untuk openai).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import AppSetting
from .config import settings
from .crypto import decrypt_secret, encrypt_secret

SINGLETON_ID = 1


def get_or_create(db: Session) -> AppSetting:
    """Ambil baris pengaturan; buat bila belum ada."""
    row = db.get(AppSetting, SINGLETON_ID)
    if row is None:
        row = AppSetting(id=SINGLETON_ID)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _mask(secret: str) -> str:
    """Mask API key: 3 karakter awal + '...' + 4 karakter akhir."""
    if len(secret) <= 7:
        return f"{secret[:3]}..."
    return f"{secret[:3]}...{secret[-4:]}"


def _provider(row: AppSetting) -> str:
    """Provider efektif: DB → env default."""
    return (row.provider or settings.llm_provider).lower()


def _env_api_key(provider: str) -> str | None:
    """API key dari environment sesuai provider aktif."""
    if (provider or "").lower() == "deepseek":
        return settings.deepseek_api_key or settings.openai_api_key
    return settings.openai_api_key


def _effective_base_url(row: AppSetting) -> str:
    """base_url efektif: DB → env. Untuk provider ollama, fallback ke OLLAMA_BASE_URL."""
    if row.base_url:
        return row.base_url
    if _provider(row) == "ollama":
        return settings.ollama_base_url
    return settings.llm_base_url


def _key_source(row: AppSetting) -> str:
    """Asal API key efektif: 'db' | 'env' | 'none'."""
    if row.api_key_encrypted:
        return "db"
    if _env_api_key(_provider(row)):
        return "env"
    return "none"


def _effective_api_key(row: AppSetting) -> str | None:
    """API key efektif (didekripsi bila dari DB) — hanya untuk dipakai backend."""
    if row.api_key_encrypted:
        return decrypt_secret(row.api_key_encrypted)
    return _env_api_key(_provider(row))


def effective_settings(db: Session) -> dict:
    """Nilai efektif (DB menimpa env) tanpa membocorkan API key mentah."""
    row = get_or_create(db)
    raw_key = _effective_api_key(row)
    return {
        "provider": row.provider or settings.llm_provider,
        "model": row.model or settings.llm_model,
        "base_url": _effective_base_url(row),
        "embedding_model": row.embedding_model or settings.llm_embedding_model,
        "has_api_key": bool(raw_key),
        "api_key_masked": _mask(raw_key) if raw_key else None,
        "source": _key_source(row),
    }


def update_settings(
    db: Session,
    *,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    embedding_model: str | None = None,
    api_key: str | None = None,
) -> dict:
    """Perbarui pengaturan.

    Field `None` = jangan diubah. Untuk `api_key`: `None` = jangan diubah,
    string kosong/whitespace = HAPUS key tersimpan, selain itu = simpan
    (terenkripsi).
    """
    row = get_or_create(db)
    if provider is not None:
        row.provider = provider.strip() or None
    if model is not None:
        row.model = model.strip() or None
    if base_url is not None:
        row.base_url = base_url.strip() or None
    if embedding_model is not None:
        row.embedding_model = embedding_model.strip() or None
    if api_key is not None:
        if api_key.strip():
            row.api_key_encrypted = encrypt_secret(api_key.strip())
        else:
            row.api_key_encrypted = None
    db.commit()
    db.refresh(row)
    return effective_settings(db)


def resolve_api_key(db: Session, provider: str | None = None) -> str | None:
    """API key efektif: DB (terenkripsi) → fallback env sesuai provider."""
    row = db.get(AppSetting, SINGLETON_ID)
    if row is not None and row.api_key_encrypted:
        key = decrypt_secret(row.api_key_encrypted)
        if key:
            return key
    if provider is None:
        provider = _provider(row) if row is not None else settings.llm_provider
    return _env_api_key(provider)


def resolve_llm_config(db: Session) -> dict:
    """Konfigurasi LLM efektif untuk factory provider (DB > env > default)."""
    row = db.get(AppSetting, SINGLETON_ID)
    provider = (row.provider if row else None) or settings.llm_provider
    if row is not None:
        base_url = _effective_base_url(row)
    else:
        base_url = (
            settings.ollama_base_url
            if provider.lower() == "ollama"
            else settings.llm_base_url
        )
    return {
        "provider": provider,
        "model": (row.model if row else None) or settings.llm_model,
        "base_url": base_url,
        "embedding_model": (row.embedding_model if row else None)
        or settings.llm_embedding_model,
        "api_key": resolve_api_key(db, provider),
    }
