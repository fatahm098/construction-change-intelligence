"""Seed katalog AHSP ke database. Jalankan: python scripts/seed_ahsp.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal  # noqa: E402
from app.models import AHSPItem  # noqa: E402
from app.services.ahsp_seed import seed_ahsp  # noqa: E402

db = SessionLocal()
created = seed_ahsp(db, force=True)
print(f"Seeded/updated {created} AHSP items.")

for item in db.query(AHSPItem).all():
    print(f"  {item.code:16s} {item.name[:40]:42s} {item.unit:5s} Rp {item.unit_price:,.0f}")

db.close()
