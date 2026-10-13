"""Dependency FastAPI untuk autentikasi (JWT Bearer) dan otorisasi (role)."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import User, UserRole
from .security import decode_access_token

# auto_error=False → dependency tidak melempar 403 sendiri; kita kontrol pesannya,
# dan endpoint yang ingin tetap terbuka saat auth dimatikan bisa memakai opsi ini.
_bearer = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kredensial tidak valid atau tidak ada.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Ambil user aktif dari header `Authorization: Bearer <token>`.

    Melempar 401 bila token tidak ada, invalid, kedaluwarsa, atau user nonaktif.
    """
    if credentials is None or not credentials.credentials:
        raise _unauthorized()

    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:  # noqa: BLE001 — semua kegagalan decode JWT → 401
        raise _unauthorized()

    subject = payload.get("sub")
    if subject is None:
        raise _unauthorized()

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise _unauthorized()

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _unauthorized()
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """Seperti `get_current_user`, tapi kembalikan None bila token tak ada/invalid.

    Dipakai endpoint yang tetap harus jalan saat `auth_enabled=false`.
    """
    if credentials is None or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except Exception:  # noqa: BLE001 — token apa pun yang gagal → anggap anonim
        return None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user


def require_role(*roles: UserRole):
    """Factory dependency: izinkan hanya user dengan salah satu role tertentu.

    Contoh: `Depends(require_role(UserRole.ADMIN))`.
    """

    allowed = set(roles)

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak untuk role ini.",
            )
        return current_user

    return _checker
