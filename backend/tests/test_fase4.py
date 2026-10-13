"""Smoke test Fase 4: auth (register/login/me) + jobs (enqueue + status).

Dijalankan pada SQLite lokal. Karena `jobs_enabled=false` (default), endpoint
`/api/jobs/analysis` mengeksekusi analisis secara sinkron sehingga tidak butuh
Redis/worker.
"""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_drawings")
PDF_REV0 = os.path.join(DATA_DIR, "drawing_rev0.pdf")
PDF_REV1 = os.path.join(DATA_DIR, "drawing_rev1.pdf")


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


def _unique_email() -> str:
    return f"tester_{uuid.uuid4().hex[:8]}@example.com"


def test_auth_register_login_me():
    email = _unique_email()

    res = client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Tester Fase 4"},
    )
    assert res.status_code == 200, res.text
    user = res.json()
    assert user["email"] == email
    assert user["is_active"] is True

    # Email duplikat → 409.
    assert client.post("/api/auth/register", json={"email": email, "password": "secret123"}).status_code == 409

    # Password terlalu pendek → 400.
    weak = client.post("/api/auth/register", json={"email": _unique_email(), "password": "short"})
    assert weak.status_code == 400

    # Login sukses → token.
    res_login = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    assert res_login.status_code == 200, res_login.text
    token = res_login.json()["access_token"]
    assert token

    # Profil dengan token.
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["email"] == email

    # Tanpa token → 401.
    assert client.get("/api/auth/me").status_code == 401

    # Password salah → 401.
    assert client.post("/api/auth/login", json={"email": email, "password": "wrongpass"}).status_code == 401


def test_jobs_analysis_sync_fallback():
    res = client.post("/api/projects", json={"name": "Proyek Uji Jobs", "description": "verifikasi jobs"})
    assert res.status_code == 200
    project_id = res.json()["id"]

    with open(PDF_REV0, "rb") as f0:
        r0 = client.post(
            "/api/drawings/upload",
            data={"project_id": project_id, "revision": 0},
            files={"file": ("drawing_rev0.pdf", f0, "application/pdf")},
        )
    with open(PDF_REV1, "rb") as f1:
        r1 = client.post(
            "/api/drawings/upload",
            data={"project_id": project_id, "revision": 1},
            files={"file": ("drawing_rev1.pdf", f1, "application/pdf")},
        )
    assert r0.status_code == 200 and r1.status_code == 200
    ref_id, rev_id = r0.json()["id"], r1.json()["id"]

    # Enqueue analisis (jobs_enabled=false → sinkron).
    res_job = client.post(
        "/api/jobs/analysis",
        json={"project_id": project_id, "drawing_ref_id": ref_id, "drawing_rev_id": rev_id, "min_area": 350},
    )
    assert res_job.status_code == 200, res_job.text
    job_id = res_job.json()["job_id"]
    assert job_id > 0

    # Status job selesai + membawa hasil run.
    res_get = client.get(f"/api/jobs/{job_id}")
    assert res_get.status_code == 200, res_get.text
    job = res_get.json()
    assert job["job_type"] == "analysis_run"
    assert job["status"] == "success"
    assert job["result"]["analysis_run_id"] > 0
    assert job["finished_at"] is not None

    # Project tidak ada → 404.
    bad = client.post("/api/jobs/analysis", json={"project_id": 999999, "drawing_ref_id": ref_id, "drawing_rev_id": rev_id})
    assert bad.status_code == 404

    # Job tidak ada → 404.
    assert client.get("/api/jobs/999999").status_code == 404
