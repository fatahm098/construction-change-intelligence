"""Kernel auth: hashing password, token JWT, dan dependency FastAPI.

Dipakai oleh `app.modules.auth` dan modul lain yang butuh proteksi endpoint.
"""

from .dependencies import get_current_user, get_current_user_optional, require_role
from .middleware import AuthGateMiddleware
from .security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

__all__ = [
    "AuthGateMiddleware",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
