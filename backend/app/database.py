"""Shim kompatibilitas.

Implementasi asli kini berada di `app.kernel.db`. Modul ini dipertahankan agar
import lama (`from app.database import Base, engine, get_db`) tetap berfungsi
selama migrasi bertahap ke struktur kernel + modules.
"""

from .kernel.db import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
