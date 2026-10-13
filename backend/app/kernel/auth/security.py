"""Primitif keamanan auth: hashing password (bcrypt) dan token JWT (pyjwt).

Modul ini bebas dari FastAPI/SQLAlchemy sehingga mudah diuji dan dipakai ulang
(mis. oleh worker ARQ yang tidak punya request context).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from ..config import settings

# bcrypt hanya memproses 72 byte pertama; potong agar password panjang tidak error.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """Hash password dengan bcrypt (salt acak). Kembalikan string siap simpan."""
    raw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Cek password terhadap hash bcrypt. False bila hash kosong/rusak."""
    if not hashed_password:
        return False
    try:
        raw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        return bcrypt.checkpw(raw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, expires_minutes: int | None = None) -> str:
    """Buat JWT akses dengan klaim `sub` (id user) dan `exp`."""
    minutes = settings.jwt_expire_minutes if expires_minutes is None else expires_minutes
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode & validasi token. Raise `jwt.PyJWTError` bila invalid/kedaluwarsa."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
