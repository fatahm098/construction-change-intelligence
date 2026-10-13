"""Module registry — tempat modul-modul fituran terdaftar.

Setiap modul adalah paket Python di bawah `app.modules.<nama_modul>` yang
mengekspor `routers` (list APIRouter). `get_module_routers()` mengumpulkan
semua router dari modul terdaftar agar `main.py` tinggal meng-include-nya.

Untuk menambah modul baru:
  1. Buat paket `app/modules/<nama>/` dengan `router.py` yang mengekspor `routers`.
  2. Tambahkan modul itu ke `_MODULE_ROUTERS` di bawah.
"""

from __future__ import annotations

from fastapi import APIRouter

from .change_intel.router import routers as _change_intel_routers
from .doc_qa.router import router as _doc_qa_router

_MODULE_ROUTERS: list[APIRouter] = [
    *_change_intel_routers,
    _doc_qa_router,
]


def get_module_routers() -> list[APIRouter]:
    """Kembalikan seluruh router dari semua modul terdaftar."""
    return list(_MODULE_ROUTERS)
