"""Test gerbang auth global (`AUTH_ENABLED`).

Fokus: memastikan middleware menutup seluruh API saat auth aktif, membuka
endpoint publik minimal, dan tidak mengubah perilaku saat auth nonaktif.

Dijalankan pada SQLite sementara (lihat DATABASE_URL di perintah verifikasi).
User uji dibuat langsung lewat SessionLocal dan dihapus lagi setelah selesai.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.kernel.auth.security import create_access_token, hash_password
from app.kernel.config import settings
from app.main import app
from app.models import User, UserRole

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_auth_flag():
    """Kembalikan `settings.auth_enabled` ke nilai semula, apa pun hasil test."""
    before = settings.auth_enabled
    yield
    settings.auth_enabled = before


@pytest.fixture
def active_user():
    """User aktif sementara + token valid. Dibersihkan setelah test."""
    email = f"gate_{uuid.uuid4().hex[:10]}@example.com"
    db = SessionLocal()
    try:
        user = User(
            email=email,
            hashed_password=hash_password("secret123"),
            full_name="Auth Gate Test",
            role=UserRole.ENGINEER,
            is_active=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    finally:
        db.close()

    yield {"id": user_id, "email": email, "token": create_access_token(user_id)}

    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


def test_auth_enabled_blocks_api_without_token():
    settings.auth_enabled = True

    res = client.get("/api/projects")
    assert res.status_code == 401, res.text
    assert res.headers.get("www-authenticate") == "Bearer"
    assert res.json().get("detail")

    # Endpoint publik tetap terbuka.
    assert client.get("/health").status_code == 200
    assert client.get("/health/ready").status_code == 200
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200

    # Token ngawur juga ditolak.
    bad = client.get("/api/projects", headers={"Authorization": "Bearer not-a-jwt"})
    assert bad.status_code == 401


def test_auth_enabled_allows_valid_token(active_user):
    settings.auth_enabled = True

    res = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {active_user['token']}"},
    )
    assert res.status_code == 200, res.text


def test_auth_disabled_keeps_old_behavior():
    settings.auth_enabled = False

    assert client.get("/api/projects").status_code == 200


def test_options_preflight_always_passes():
    settings.auth_enabled = True

    res = client.options(
        "/api/projects",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code == 200, res.text


def test_register_closed_after_first_user(active_user):
    settings.auth_enabled = True

    res = client.post(
        "/api/auth/register",
        json={
            "email": f"gate_new_{uuid.uuid4().hex[:8]}@example.com",
            "password": "secret123",
            "full_name": "Tidak Boleh",
        },
    )
    assert res.status_code == 403, res.text
    assert res.json().get("detail")
