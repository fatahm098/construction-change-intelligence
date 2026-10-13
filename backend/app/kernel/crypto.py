"""Enkripsi rahasia (API key) dengan Fernet (AES-128-CBC + HMAC).

Kunci diturunkan dari `settings.settings_encryption_key`; bila kosong, dari
`settings.jwt_secret` (fallback dev) sehingga aplikasi tetap jalan tanpa
konfigurasi tambahan. Untuk produksi, set `SETTINGS_ENCRYPTION_KEY` eksplisit —
menggantinya akan membuat ciphertext lama tidak bisa didekripsi.
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from .config import settings


def _derive_key(secret: str) -> bytes:
    """Turunkan kunci Fernet (32 byte, urlsafe-base64) dari secret apa pun."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _fernet() -> Fernet:
    secret = settings.settings_encryption_key or settings.jwt_secret
    return Fernet(_derive_key(secret))


def encrypt_secret(plaintext: str) -> str:
    """Enkripsi string → token Fernet (str, aman disimpan di kolom teks)."""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str | None:
    """Dekripsi token Fernet. Kembalikan None bila token rusak/kunci berubah."""
    if not token:
        return None
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        return None
