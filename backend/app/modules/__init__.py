"""Module registry — tempat modul-modul fituran terdaftar.

Setiap modul adalah paket Python di bawah `app.modules.<nama_modul>` dengan
minimal:
  - `__init__.py`
  - `router.py`  (APIRouter; boleh meng-include sub-router)

`main.py` meng-include router dari setiap modul terdaftar di sini.
"""
