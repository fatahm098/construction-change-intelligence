"""Readiness probe: verifikasi dependensi tanpa melakukan panggilan jaringan LLM.

`GET /health/ready` (didaftarkan di `app.main`) mengembalikan 200 bila cek
database lulus, 503 bila tidak. Cek LLM hanya melaporkan apakah provider
terkonfigurasi (berdasarkan settings), tidak memanggil jaringan.
"""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse
from sqlalchemy import text

from ...database import engine
from ..config import settings


def check_database() -> dict[str, Any]:
    """Cek konektivitas DB dengan `SELECT 1`."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def check_llm() -> dict[str, Any]:
    """Laporkan apakah provider LLM terkonfigurasi (tanpa panggilan jaringan)."""
    provider = (settings.llm_provider or "").lower()

    if provider == "ollama":
        configured = bool(settings.ollama_base_url)
    elif provider == "openai":
        configured = bool(settings.openai_api_key)
    else:
        configured = False

    return {"provider": provider, "configured": configured}


def readiness() -> JSONResponse:
    """Bangun respons readiness (200 bila DB OK, 503 bila tidak)."""
    db_check = check_database()
    checks: dict[str, Any] = {"database": db_check, "llm": check_llm()}

    if db_check["ok"]:
        return JSONResponse(status_code=200, content={"status": "ready", "checks": checks})

    return JSONResponse(
        status_code=503, content={"status": "not_ready", "checks": checks}
    )
