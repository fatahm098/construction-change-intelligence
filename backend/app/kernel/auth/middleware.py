"""Gerbang auth global (ASGI middleware).

Saat `settings.auth_enabled=false` middleware ini tidak melakukan apa pun,
sehingga perilaku dev/demo lama tetap identik. Saat `true`, semua request HTTP
wajib membawa Bearer JWT yang valid, kecuali daftar endpoint publik minimal di
bawah.

Sengaja dipasang sebagai middleware (bukan dependency per-router) agar tidak ada
endpoint modul yang lolos tanpa proteksi. Middleware hanya memvalidasi tanda
tangan/expiry token dan klaim `sub` — tidak membuka sesi DB per request. Cek user
aktif tetap dilakukan oleh dependency `get_current_user` pada endpoint yang
memerlukannya.
"""

from __future__ import annotations

import logging

from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ..config import settings
from .security import decode_access_token

logger = logging.getLogger(__name__)

# Endpoint publik: (method, path). Selain ini wajib token.
_PUBLIC_ENDPOINTS: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "/health"),
        ("GET", "/health/ready"),
        ("POST", "/api/auth/login"),
        ("POST", "/api/auth/register"),
        ("GET", "/docs"),
        ("GET", "/docs/oauth2-redirect"),
        ("GET", "/redoc"),
        ("GET", "/openapi.json"),
    }
)

# Prefix publik (aset statis hasil analisis gambar).
_PUBLIC_PREFIXES: tuple[str, ...] = ("/static/",)


def _unauthorized(detail: str = "Kredensial tidak valid atau tidak ada.") -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden(detail: str) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": detail})


def _normalize_path(path: str) -> str:
    # `/health/` dan `/health` diperlakukan sama agar redirect 307 tidak jadi 401.
    return path.rstrip("/") or "/"


def _is_public(method: str, path: str) -> bool:
    if (method, path) in _PUBLIC_ENDPOINTS:
        return True
    return any(path.startswith(prefix) for prefix in _PUBLIC_PREFIXES)


def _has_any_user() -> bool:
    """True bila tabel users sudah berisi minimal satu akun (bootstrap selesai)."""
    from ...database import SessionLocal
    from ...models import User

    db = SessionLocal()
    try:
        return db.query(User.id).first() is not None
    finally:
        db.close()


class AuthGateMiddleware:
    """Tolak request tanpa JWT valid saat `AUTH_ENABLED=true`."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not settings.auth_enabled:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET").upper()
        path = _normalize_path(scope.get("path", "/"))

        # Preflight CORS tidak pernah membawa Authorization.
        if method == "OPTIONS" or _is_public(method, path):
            # Registrasi terbuka hanya untuk bootstrap admin pertama. Setelah ada
            # user, pendaftaran mandiri ditutup agar tidak ada akun liar di produksi.
            if method == "POST" and path == "/api/auth/register":
                if await run_in_threadpool(_has_any_user):
                    await _forbidden(
                        "Registrasi ditutup. Hubungi admin untuk pembuatan akun."
                    )(scope, receive, send)
                    return
            await self.app(scope, receive, send)
            return

        header = ""
        for key, value in scope.get("headers", []):
            if key == b"authorization":
                header = value.decode("latin-1")
                break

        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            await _unauthorized()(scope, receive, send)
            return

        try:
            payload = decode_access_token(token.strip())
        except Exception:  # noqa: BLE001 — semua kegagalan decode JWT → 401
            await _unauthorized("Token tidak valid atau kedaluwarsa.")(scope, receive, send)
            return

        subject = payload.get("sub")
        if subject is None or str(subject).strip() == "":
            await _unauthorized("Token tidak memiliki subject.")(scope, receive, send)
            return

        await self.app(scope, receive, send)
