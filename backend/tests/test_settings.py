"""Smoke test modul settings: simpan API key (terenkripsi) + jaminan tidak bocor.

Kontrak v1:
  GET  /api/settings/llm       → pengaturan efektif (tanpa API key mentah)
  PUT  /api/settings/llm       → simpan; `api_key` kosong = hapus, None = tetap
  POST /api/settings/llm/test  → uji koneksi (HTTP selalu 200)

Dijalankan pada SQLite lokal. Pengaturan dikembalikan ke kondisi semula setelah
setiap test supaya DB dev tidak tertinggal nilai palsu.
"""

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import AppSetting

client = TestClient(app)

DUMMY_KEY = "sk-test-DUMMYSECRET1234567890abcd"

_RESPONSE_FIELDS = {
    "provider",
    "model",
    "base_url",
    "embedding_model",
    "has_api_key",
    "api_key_masked",
    "source",
}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def restore_settings():
    """Snapshot pengaturan non-rahasia, pulihkan setelah test (key dibersihkan)."""
    before = client.get("/api/settings/llm").json()
    yield
    client.put(
        "/api/settings/llm",
        json={
            "provider": before["provider"],
            "model": before["model"],
            "base_url": before["base_url"],
            "embedding_model": before["embedding_model"],
            "api_key": "",
        },
    )


def test_get_default_shape():
    res = client.get("/api/settings/llm")
    assert res.status_code == 200, res.text
    data = res.json()
    assert set(data) == _RESPONSE_FIELDS
    assert data["source"] in {"db", "env", "none"}
    assert isinstance(data["has_api_key"], bool)


def test_save_key_is_masked_and_never_returned(restore_settings):
    res = client.put("/api/settings/llm", json={"provider": "local", "api_key": DUMMY_KEY})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["has_api_key"] is True
    assert data["source"] == "db"
    assert data["api_key_masked"] and data["api_key_masked"].endswith(DUMMY_KEY[-4:])
    # Raw key TIDAK boleh muncul di respons mana pun.
    assert DUMMY_KEY not in res.text
    assert DUMMY_KEY not in client.get("/api/settings/llm").text

    # Tanpa `api_key` → key lama dibiarkan.
    keep = client.put("/api/settings/llm", json={"model": "model-uji"}).json()
    assert keep["has_api_key"] is True

    # `api_key: ""` → hapus.
    cleared = client.put("/api/settings/llm", json={"api_key": ""}).json()
    assert cleared["has_api_key"] is False
    assert cleared["api_key_masked"] is None


def test_key_encrypted_at_rest(restore_settings):
    client.put("/api/settings/llm", json={"provider": "local", "api_key": DUMMY_KEY})
    db = SessionLocal()
    try:
        row = db.query(AppSetting).first()
        assert row is not None
        assert row.api_key_encrypted, "key tidak tersimpan"
        assert DUMMY_KEY not in row.api_key_encrypted, "key tersimpan sebagai teks biasa!"
    finally:
        db.close()


def test_test_connection_local(restore_settings):
    client.put("/api/settings/llm", json={"provider": "local"})
    res = client.post("/api/settings/llm/test")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    assert set(body) == {"ok", "message", "model"}
