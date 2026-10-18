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
    """Laporkan provider LLM efektif (DB > env) tanpa panggilan jaringan."""
    provider = (settings.llm_provider or "").lower()
    base_url = settings.ollama_base_url
    has_key = bool(settings.deepseek_api_key or settings.openai_api_key)

    # Halaman Pengaturan menyimpan pilihan provider di DB; readiness harus
    # mencerminkan konfigurasi yang benar-benar dipakai, bukan default env.
    try:
        from ...database import SessionLocal
        from ..settings_store import effective_settings

        db = SessionLocal()
        try:
            cfg = effective_settings(db)
        finally:
            db.close()
        provider = (cfg.get("provider") or provider).lower()
        base_url = cfg.get("base_url") or base_url
        has_key = bool(cfg.get("has_api_key"))
    except Exception:  # noqa: BLE001 — DB belum siap → pakai env
        pass

    if provider == "local":
        configured = True
    elif provider == "ollama":
        configured = bool(base_url)
    else:
        configured = has_key

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
