"""Data & seeder AHSP (Analisa Harga Satuan Pekerjaan).

Harga satuan dasar memakai asumsi harga pasar Indonesia (2024, indikatif).
Struktur mengikuti pola AHSP: tenaga kerja + bahan + peralatan, masing-masing
dengan koefisien (indeks) dan harga satuan dasar.

Harga satuan AHSP = Σ (koefisien × harga satuan dasar).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import AHSPComponent, AHSPComponentType, AHSPItem

# fmt: off
AHSP_DATA: list[dict] = [
    {
        "code": "AHSP-BTN-25",
        "name": "Beton mutu sedang fc' 25 MPa",
        "unit": "m3",
        "category": "beton",
        "components": [
            # Bahan
            {"type": "material", "name": "Semen Portland", "coefficient": 384.0, "unit": "kg", "base_price": 1300},
            {"type": "material", "name": "Pasir beton", "coefficient": 0.55, "unit": "m3", "base_price": 250000},
            {"type": "material", "name": "Kerikil (split)", "coefficient": 0.75, "unit": "m3", "base_price": 280000},
            {"type": "material", "name": "Air", "coefficient": 215.0, "unit": "liter", "base_price": 20},
            # Tenaga kerja
            {"type": "labor", "name": "Pekerja", "coefficient": 1.65, "unit": "OH", "base_price": 100000},
            {"type": "labor", "name": "Tukang batu", "coefficient": 0.275, "unit": "OH", "base_price": 130000},
            {"type": "labor", "name": "Kepala tukang", "coefficient": 0.028, "unit": "OH", "base_price": 150000},
            {"type": "labor", "name": "Mandor", "coefficient": 0.083, "unit": "OH", "base_price": 160000},
            # Peralatan
            {"type": "equipment", "name": "Concrete mixer", "coefficient": 0.25, "unit": "jam", "base_price": 50000},
            {"type": "equipment", "name": "Vibrator", "coefficient": 0.25, "unit": "jam", "base_price": 30000},
        ],
    },
    {
        "code": "AHSP-BTN-30",
        "name": "Beton mutu tinggi fc' 30 MPa",
        "unit": "m3",
        "category": "beton",
        "components": [
            {"type": "material", "name": "Semen Portland", "coefficient": 413.0, "unit": "kg", "base_price": 1300},
            {"type": "material", "name": "Pasir beton", "coefficient": 0.54, "unit": "m3", "base_price": 250000},
            {"type": "material", "name": "Kerikil (split)", "coefficient": 0.76, "unit": "m3", "base_price": 280000},
            {"type": "material", "name": "Air", "coefficient": 215.0, "unit": "liter", "base_price": 20},
            {"type": "labor", "name": "Pekerja", "coefficient": 1.65, "unit": "OH", "base_price": 100000},
            {"type": "labor", "name": "Tukang batu", "coefficient": 0.275, "unit": "OH", "base_price": 130000},
            {"type": "labor", "name": "Kepala tukang", "coefficient": 0.028, "unit": "OH", "base_price": 150000},
            {"type": "labor", "name": "Mandor", "coefficient": 0.083, "unit": "OH", "base_price": 160000},
            {"type": "equipment", "name": "Concrete mixer", "coefficient": 0.25, "unit": "jam", "base_price": 50000},
            {"type": "equipment", "name": "Vibrator", "coefficient": 0.25, "unit": "jam", "base_price": 30000},
        ],
    },
    {
        "code": "AHSP-BESI",
        "name": "Pembesian / pekerjaan besi beton",
        "unit": "kg",
        "category": "besi",
        "components": [
            {"type": "material", "name": "Besi beton (polos/ulir)", "coefficient": 1.05, "unit": "kg", "base_price": 12500},
            {"type": "material", "name": "Kawat beton", "coefficient": 0.015, "unit": "kg", "base_price": 20000},
            {"type": "labor", "name": "Pekerja", "coefficient": 0.007, "unit": "OH", "base_price": 100000},
            {"type": "labor", "name": "Tukang besi", "coefficient": 0.007, "unit": "OH", "base_price": 130000},
            {"type": "labor", "name": "Kepala tukang", "coefficient": 0.0007, "unit": "OH", "base_price": 150000},
            {"type": "labor", "name": "Mandor", "coefficient": 0.0004, "unit": "OH", "base_price": 160000},
        ],
    },
    {
        "code": "AHSP-BEKISTING",
        "name": "Bekisting (perancah & cetakan)",
        "unit": "m2",
        "category": "bekisting",
        "components": [
            {"type": "material", "name": "Kayu bekisting (papan)", "coefficient": 0.04, "unit": "m3", "base_price": 3500000},
            {"type": "material", "name": "Paku", "coefficient": 0.3, "unit": "kg", "base_price": 20000},
            {"type": "material", "name": "Minyak bekisting", "coefficient": 0.1, "unit": "liter", "base_price": 25000},
            {"type": "labor", "name": "Pekerja", "coefficient": 0.35, "unit": "OH", "base_price": 100000},
            {"type": "labor", "name": "Tukang kayu", "coefficient": 0.18, "unit": "OH", "base_price": 130000},
            {"type": "labor", "name": "Kepala tukang", "coefficient": 0.018, "unit": "OH", "base_price": 150000},
            {"type": "labor", "name": "Mandor", "coefficient": 0.02, "unit": "OH", "base_price": 160000},
        ],
    },
    {
        "code": "AHSP-PLESTER",
        "name": "Plesteran dan acian dinding",
        "unit": "m2",
        "category": "dinding",
        "components": [
            {"type": "material", "name": "Semen Portland", "coefficient": 8.6, "unit": "kg", "base_price": 1300},
            {"type": "material", "name": "Pasir pasang", "coefficient": 0.023, "unit": "m3", "base_price": 230000},
            {"type": "labor", "name": "Pekerja", "coefficient": 0.3, "unit": "OH", "base_price": 100000},
            {"type": "labor", "name": "Tukang batu", "coefficient": 0.15, "unit": "OH", "base_price": 130000},
            {"type": "labor", "name": "Kepala tukang", "coefficient": 0.015, "unit": "OH", "base_price": 150000},
            {"type": "labor", "name": "Mandor", "coefficient": 0.015, "unit": "OH", "base_price": 160000},
        ],
    },
]
# fmt: on

_TYPE_MAP = {
    "labor": AHSPComponentType.LABOR,
    "material": AHSPComponentType.MATERIAL,
    "equipment": AHSPComponentType.EQUIPMENT,
}


def seed_ahsp(db: Session, *, force: bool = False) -> int:
    """Isi tabel AHSP dengan data bawaan. Idempotent berdasarkan `code`.

    Jika `force=True`, item dengan code yang sudah ada akan diperbarui.
    Kembalikan jumlah item AHSP yang dibuat/diperbarui.
    """
    count = 0
    for entry in AHSP_DATA:
        existing = db.query(AHSPItem).filter(AHSPItem.code == entry["code"]).first()

        if existing and not force:
            continue

        if existing and force:
            # Hapus komponen lama, perbarui item
            for comp in list(existing.components):
                db.delete(comp)
            existing.name = entry["name"]
            existing.unit = entry["unit"]
            existing.category = entry.get("category")
            item = existing
        else:
            item = AHSPItem(
                code=entry["code"],
                name=entry["name"],
                unit=entry["unit"],
                category=entry.get("category"),
            )
            db.add(item)

        db.flush()  # dapatkan item.id

        for comp in entry["components"]:
            db.add(
                AHSPComponent(
                    ahsp_item_id=item.id,
                    component_type=_TYPE_MAP[comp["type"]],
                    name=comp["name"],
                    coefficient=comp["coefficient"],
                    unit=comp["unit"],
                    base_price=comp["base_price"],
                )
            )
        count += 1

    db.commit()
    return count
