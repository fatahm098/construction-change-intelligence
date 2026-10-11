import openpyxl


def parse_boq_excel(file_path: str) -> list[dict]:
    """
    Membaca spreadsheet BOQ / RAB konstruksi (XLSX).
    Format fleksibel: mencari kolom No, Kode Item, Uraian Pekerjaan, Satuan, Volume, Harga Satuan.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    items = []
    # Mencari baris header
    header_row_idx = None
    for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        row_str = " ".join([str(c).lower() for c in row if c is not None])
        if "uraian" in row_str or "pekerjaan" in row_str or "harga" in row_str:
            header_row_idx = row_idx
            break

    if header_row_idx is None:
        header_row_idx = 1

    for row in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
        if not row or all(c is None for c in row):
            continue

        # Kolom minimal: deskripsi dan harga satuan
        # Asumsi layout standar: [No, Kode, Uraian, Satuan, Vol, Harga, Total]
        try:
            code = str(row[1]).strip() if len(row) > 1 and row[1] else f"ITEM-{len(items)+1}"
            description = str(row[2]).strip() if len(row) > 2 and row[2] else ""
            unit = str(row[3]).strip() if len(row) > 3 and row[3] else "ls"
            contract_vol = float(row[4]) if len(row) > 4 and row[4] is not None else 0.0
            price = float(row[5]) if len(row) > 5 and row[5] is not None else 0.0

            if description and price > 0:
                items.append({
                    "code": code,
                    "description": description,
                    "unit": unit,
                    "contract_volume": contract_vol,
                    "unit_price": price,
                })
        except (ValueError, TypeError, IndexError):
            continue

    return items


def suggest_boq_item(element_type: str, items: list) -> dict | None:
    """
    Memberikan rekomendasi item BOQ berdasarkan kata kunci tipe elemen.
    """
    keyword_map = {
        "column": ["kolom", "column"],
        "beam": ["balok", "beam"],
        "slab": ["pelat", "plat", "slab"],
    }

    keywords = keyword_map.get(element_type.lower(), [])
    for it in items:
        desc = it.description.lower()
        if any(kw in desc for kw in keywords) and "beton" in desc:
            return it

    # Fallback tanpa kata 'beton'
    for it in items:
        desc = it.description.lower()
        if any(kw in desc for kw in keywords):
            return it

    return None
