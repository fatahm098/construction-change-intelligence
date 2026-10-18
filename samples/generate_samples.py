"""Generator paket dokumen uji untuk platform (dijalankan sekali, hasilnya di-commit).

Menghasilkan:
  - gambar_denah_rev_A.pdf / gambar_denah_rev_B.pdf  (denah + revisi, untuk change intelligence)
  - boq_rev_A.xlsx / boq_rev_B.xlsx                  (RAB/BOQ, untuk cost impact)
  - rks_gedung_2lantai.pdf                           (spesifikasi teknis, untuk doc QA)

Perubahan Rev A -> Rev B sengaja dibuat eksplisit agar hasil analisis bisa
dibandingkan dengan `ground_truth.md`.

Jalankan: backend/.venv/Scripts/python.exe samples/generate_samples.py
"""

from __future__ import annotations

import os

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Gambar denah
# ---------------------------------------------------------------------------

# (x, y, lebar, tinggi) area denah dalam point
PLAN_X, PLAN_Y = 110, 300
WALL = 3.0


def _line(c, x1, y1, x2, y2, w=WALL):
    c.setLineWidth(w)
    c.line(x1, y1, x2, y2)


def _rect(c, x, y, w, h, width=WALL):
    c.setLineWidth(width)
    c.rect(x, y, w, h)


def _column(c, x, y, size, label):
    c.setFillGray(0.25)
    c.rect(x - size / 2, y - size / 2, size, size, stroke=0, fill=1)
    c.setFillGray(0)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x, y - size / 2 - 10, label)


def _dim_h(c, x1, x2, y, text):
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)
    for x in (x1, x2):
        c.line(x, y - 4, x, y + 4)
    c.setFont("Helvetica", 7)
    c.drawCentredString((x1 + x2) / 2, y + 5, text)


def _dim_v(c, y1, y2, x, text):
    c.setLineWidth(0.5)
    c.line(x, y1, x, y2)
    for y in (y1, y2):
        c.line(x - 4, y, x + 4, y)
    c.saveState()
    c.translate(x - 6, (y1 + y2) / 2)
    c.rotate(90)
    c.setFont("Helvetica", 7)
    c.drawCentredString(0, 0, text)
    c.restoreState()


def _title_block(c, rev: str, date: str, note: str):
    c.setLineWidth(1)
    _rect(c, 500, 60, 290, 110, width=1)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(510, 152, "PROYEK PEMBANGUNAN GEDUNG KANTOR 2 LANTAI")
    c.setFont("Helvetica", 9)
    c.drawString(510, 136, "Lokasi: Jl. Soekarno-Hatta No. 12, Bandung")
    c.drawString(510, 122, "Pemberi Tugas: PT Graha Nusantara")
    c.drawString(510, 108, f"Nomor Gambar: A-101    Revisi: {rev}    Tanggal: {date}")
    c.drawString(510, 94, "Skala: 1 : 100    Kertas: A4")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(510, 76, note)


def build_drawing(path: str, rev: str) -> None:
    c = canvas.Canvas(path, pagesize=landscape(A4))
    page_w, page_h = landscape(A4)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, page_h - 50, f"DENAH LANTAI 1 — REVISI {rev}")

    if rev == "A":
        width, height = 300, 170
        note = "Gambar kerja awal, untuk pelaksanaan."
    else:
        width, height = 340, 170
        note = "Revisi: penambahan 1 bay ruang rapat dan kolom K2."

    x0, y0 = PLAN_X, PLAN_Y
    x1, y1 = x0 + width, y0 + height

    # Dinding luar
    _rect(c, x0, y0, width, height)

    # Dinding tengah vertikal
    mid_x = x0 + 120
    _line(c, mid_x, y0, mid_x, y1)
    # Dinding horizontal kiri (membagi 2 ruang)
    _line(c, x0, y0 + 80, mid_x, y0 + 80)
    # Dinding horizontal kanan
    if rev == "A":
        _line(c, mid_x, y0 + 60, x1, y0 + 60)
    else:
        extra_x = x1 - 70
        _line(c, mid_x, y0 + 60, extra_x, y0 + 60)
        _line(c, extra_x, y0, extra_x, y1)

    # Pintu (bukaan dinding) digambar sebagai garis putih
    c.setStrokeGray(1)
    c.setLineWidth(5)
    c.line(x0 + 40, y0, x0 + 65, y0)          # pintu masuk
    c.line(mid_x, y0 + 30, mid_x, y0 + 55)    # pintu antar ruang
    c.setStrokeGray(0)

    # Kolom
    _column(c, x0 + 6, y0 + 6, 14, "K1 300x300")
    _column(c, x1 - 6, y0 + 6, 14, "K1 300x300")
    _column(c, x0 + 6, y1 - 6, 14, "K1 300x300")
    if rev == "A":
        _column(c, x1 - 6, y1 - 6, 14, "K1 300x300")
    else:
        _column(c, x1 - 6, y1 - 6, 18, "K2 400x400")
        _column(c, mid_x + 6, y0 + 6, 14, "K1 300x300")

    # Label ruang
    c.setFont("Helvetica", 8)
    c.drawCentredString(x0 + 60, y0 + 120, "RUANG TAMU")
    c.drawCentredString(x0 + 60, y0 + 40, "GUDANG")
    if rev == "A":
        c.drawCentredString(mid_x + 90, y0 + 110, "RUANG RAPAT")
    else:
        c.drawCentredString(mid_x + 60, y0 + 110, "RUANG RAPAT")
        c.drawCentredString(x1 - 35, y0 + 110, "PANTRY")

    # Dimensi
    _dim_h(c, x0, mid_x, y0 - 25, "4000")
    _dim_h(c, mid_x, x1, y0 - 25, "6000" if rev == "A" else "7000")
    _dim_h(c, x0, x1, y0 - 50, "10000" if rev == "A" else "11000")
    _dim_v(c, y0, y1, x0 - 25, "5500")

    _title_block(c, rev, "2026-02-10" if rev == "A" else "2026-04-18", note)
    c.showPage()
    c.save()


# ---------------------------------------------------------------------------
# BOQ / RAB
# ---------------------------------------------------------------------------

# (kode, uraian, satuan, volume A, harga satuan)
ITEMS = [
    ("1", "PEKERJAAN PERSIAPAN", "", None, None),
    ("1.1", "Pembersihan lahan dan pengukuran", "m2", 240, 18500),
    ("1.2", "Pembuatan direksi keet dan gudang", "ls", 1, 12500000),
    ("2", "PEKERJAAN TANAH DAN PONDASI", "", None, None),
    ("2.1", "Galian tanah pondasi", "m3", 96, 42000),
    ("2.2", "Urugan pasir bawah pondasi", "m3", 18, 210000),
    ("2.3", "Pondasi footplat beton K-300", "m3", 24, 1850000),
    ("2.4", "Pondasi batu kali", "m3", 32, 780000),
    ("3", "PEKERJAAN STRUKTUR", "", None, None),
    ("3.1", "Kolom beton K-300 300x300", "m3", 18, 1950000),
    ("3.2", "Balok beton K-300", "m3", 26, 1900000),
    ("3.3", "Plat beton K-300 tebal 120 mm", "m3", 42, 1875000),
    ("3.4", "Pembesian besi ulir D13", "kg", 12400, 14500),
    ("3.5", "Bekisting kolom dan balok", "m2", 380, 95000),
    ("4", "PEKERJAAN DINDING DAN PLESTERAN", "", None, None),
    ("4.1", "Dinding bata merah 1/2 bata", "m2", 420, 165000),
    ("4.2", "Plesteran dan acian", "m2", 840, 62000),
    ("4.3", "Pengecatan dinding interior", "m2", 840, 38000),
    ("5", "PEKERJAAN ATAP", "", None, None),
    ("5.1", "Rangka atap baja ringan", "m2", 260, 145000),
    ("5.2", "Penutup atap genteng metal", "m2", 260, 165000),
    ("5.3", "Lisplang GRC", "m", 96, 85000),
    ("6", "PEKERJAAN LANTAI DAN PLAFON", "", None, None),
    ("6.1", "Keramik lantai 60x60", "m2", 240, 185000),
    ("6.2", "Plafon gypsum 9 mm", "m2", 240, 135000),
    ("6.3", "List plafon gypsum", "m", 180, 32000),
    ("7", "PEKERJAAN KUSEN, PINTU DAN JENDELA", "", None, None),
    ("7.1", "Kusen aluminium 4 inci", "m", 120, 210000),
    ("7.2", "Pintu panel kayu", "unit", 8, 1650000),
    ("7.3", "Jendela kaca tempered 8 mm", "m2", 36, 620000),
    ("8", "PEKERJAAN SANITASI DAN MEKANIKAL", "", None, None),
    ("8.1", "Instalasi air bersih PVC", "ls", 1, 8500000),
    ("8.2", "Instalasi air kotor PVC", "ls", 1, 7200000),
    ("8.3", "Sanitair set kamar mandi", "unit", 4, 2450000),
    ("9", "PEKERJAAN LISTRIK", "", None, None),
    ("9.1", "Instalasi titik lampu", "titik", 42, 285000),
    ("9.2", "Instalasi titik saklar dan stop kontak", "titik", 28, 265000),
    ("10", "PEKERJAAN PENUTUP AKHIR", "", None, None),
    ("10.1", "Pembersihan akhir dan serah terima", "ls", 1, 4500000),
]

# Perubahan volume Rev A -> Rev B (harga satuan ikut berubah bila spesifikasi berubah)
REV_B_DELTA = {
    "2.3": {"volume": 30},                      # footplat bertambah
    "3.1": {"volume": 21, "price": 2150000},    # kolom K-350
    "3.4": {"volume": 13800},                   # pembesian bertambah
    "4.1": {"volume": 440, "price": 195000},    # bata ringan AAC
    "6.1": {"volume": 250, "price": 245000},    # keramik 80x80
    "6.2": {"volume": 250, "price": 155000},    # gypsum 12 mm
}

REV_B_NEW_ITEMS = [
    ("5.4", "Waterproofing membran atap", "m2", 260, 125000),
    ("4.4", "Partisi gypsum ruang pantry", "m2", 24, 165000),
]


def build_boq(path: str, rev: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = f"RAB Rev {rev}"

    ws["A1"] = "REKAPITULASI BIAYA (RAB)"
    ws["A2"] = "Proyek: Pembangunan Gedung Kantor 2 Lantai"
    ws["A3"] = f"Revisi: {rev}    Tanggal: {'2026-02-10' if rev == 'A' else '2026-04-18'}"

    header = ["No", "Kode", "Uraian Pekerjaan", "Satuan", "Volume", "Harga Satuan (Rp)", "Jumlah (Rp)"]
    ws.append([])
    ws.append(header)

    rows = []
    for code, desc, unit, vol, price in ITEMS:
        if unit == "":  # baris judul kelompok
            rows.append((code, "", desc, "", None, None))
            continue
        v = vol
        p = price
        if rev == "B" and code in REV_B_DELTA:
            d = REV_B_DELTA[code]
            v = d.get("volume", v)
            p = d.get("price", p)
        rows.append((code, code, desc, unit, v, p))

    if rev == "B":
        for code, desc, unit, vol, price in REV_B_NEW_ITEMS:
            rows.append((code, code, desc, unit, vol, price))

    total = 0.0
    for no, code, desc, unit, vol, price in rows:
        if unit == "":
            ws.append([no, "", desc, "", "", "", ""])
            continue
        amount = (vol or 0) * (price or 0)
        total += amount
        ws.append([no, code, desc, unit, vol, price, amount])

    ws.append([])
    ws.append(["", "", "JUMLAH TOTAL", "", "", "", total])
    ws.append(["", "", "PPN 11%", "", "", "", round(total * 0.11)])
    ws.append(["", "", "GRAND TOTAL", "", "", "", round(total * 1.11)])

    widths = {"A": 6, "B": 10, "C": 52, "D": 10, "E": 12, "F": 20, "G": 22}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for cell in ws[6]:
        cell.font = cell.font.copy(bold=True)

    wb.save(path)


# ---------------------------------------------------------------------------
# RKS (spesifikasi teknis)
# ---------------------------------------------------------------------------

RKS_SECTIONS = [
    ("PASAL 1 — LINGKUP PEKERJAAN", [
        "Pekerjaan meliputi pembangunan gedung kantor 2 (dua) lantai beserta pekerjaan "
        "struktur, arsitektur, mekanikal, elektrikal, dan plumbing (MEP).",
        "Penyedia jasa wajib melaksanakan pekerjaan sesuai gambar kerja, RKS ini, dan "
        "Bill of Quantity (BOQ) yang menjadi bagian dari dokumen kontrak.",
        "Semua perbedaan antara gambar, RKS, dan BOQ wajib dilaporkan kepada pengawas "
        "sebelum pelaksanaan. Perbedaan yang tidak dilaporkan menjadi tanggung jawab penyedia.",
    ]),
    ("PASAL 2 — STANDAR DAN PERATURAN", [
        "SNI 2847:2019 Persyaratan beton struktural untuk bangunan gedung.",
        "SNI 1726:2019 Tata cara perencanaan ketahanan gempa untuk struktur bangunan gedung.",
        "SNI 1727:2020 Beban desain minimum dan kriteria terkait untuk bangunan gedung.",
        "Peraturan Menteri PUPR Nomor 10 Tahun 2021 tentang Pedoman Sistem Manajemen "
        "Keselamatan dan Kesehatan Kerja (SMKK).",
        "Undang-Undang Nomor 2 Tahun 2017 tentang Jasa Konstruksi.",
    ]),
    ("PASAL 3 — MUTU BETON DAN MATERIAL STRUKTUR", [
        "Mutu beton struktur kolom, balok, dan plat lantai adalah K-300 (fc' 24,9 MPa) "
        "dengan slump 12 ± 2 cm.",
        "Beton harus memakai semen Portland tipe I sesuai SNI 7064, agregat halus dan kasar "
        "sesuai SNI 03-2461-1991, dan air bersih bebas bahan organik.",
        "Baja tulangan memakai baja ulir BJTS 420A dengan tegangan leleh minimum 420 MPa.",
        "Selimut beton minimal 40 mm untuk elemen yang berhubungan dengan tanah dan 25 mm "
        "untuk elemen di atas tanah.",
        "Setiap pengecoran wajib disertai uji slump dan benda uji silinder 28 hari minimal "
        "2 buah per 20 m3 beton.",
    ]),
    ("PASAL 4 — PEKERJAAN DINDING DAN FINISHING", [
        "Dinding memakai bata merah ukuran 230 x 110 x 55 mm dengan campuran spesi 1:4.",
        "Plesteran tebal 15 mm dan acian tebal 3 mm dengan permukaan rata, tidak berlubang, "
        "dan tidak retak.",
        "Pengecatan memakai cat interior berbasis akrilik, 1 lapis primer dan 2 lapis finish.",
    ]),
    ("PASAL 5 — PEKERJAAN LANTAI DAN PLAFON", [
        "Keramik lantai memakai ukuran 60 x 60 cm tipe homogeneous tile kelas PEI 4.",
        "Plafon memakai papan gypsum tebal 9 mm dengan rangka hollow galvanis 40 x 40 mm "
        "jarak 60 cm.",
    ]),
    ("PASAL 6 — KESELAMATAN DAN KESEHATAN KERJA", [
        "Penyedia jasa wajib menyusun Rencana Keselamatan Konstruksi (RKK) sebelum "
        "mobilisasi dan memperbaruinya setiap perubahan metode kerja.",
        "Alat pelindung diri wajib dipakai seluruh pekerja: helm, sepatu keselamatan, "
        "rompi reflektif, dan sarung tangan.",
        "Pekerjaan di ketinggian lebih dari 1,8 meter wajib memakai full body harness "
        "dengan anchor point yang diperiksa setiap hari.",
        "Setiap kecelakaan kerja wajib dilaporkan maksimal 1 x 24 jam kepada pengawas "
        "dan dicatat dalam laporan K3 mingguan.",
    ]),
    ("PASAL 7 — PENGUJIAN DAN SERAH TERIMA", [
        "Pengujian meliputi uji slump, uji kuat tekan beton, uji kepadatan tanah, dan uji "
        "instalasi MEP.",
        "Serah terima pertama dilakukan setelah 100% pekerjaan selesai dan daftar cacat "
        "(punch list) ditutup.",
        "Masa pemeliharaan adalah 180 hari kalender sejak berita acara serah terima pertama.",
    ]),
]


def build_rks(path: str) -> None:
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, height - 70, "RENCANA KERJA DAN SYARAT-SYARAT (RKS)")
    c.setFont("Helvetica", 11)
    c.drawString(60, height - 90, "Pembangunan Gedung Kantor 2 Lantai")
    c.drawString(60, height - 106, "PT Graha Nusantara — Bandung, 2026")
    c.showPage()

    y = height - 70
    for title, paragraphs in RKS_SECTIONS:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, title)
        y -= 20
        c.setFont("Helvetica", 9)
        for para in paragraphs:
            for line in _wrap(para, 92):
                if y < 70:
                    c.showPage()
                    y = height - 70
                    c.setFont("Helvetica", 9)
                c.drawString(60, y, line)
                y -= 13
            y -= 5
        y -= 12
        if y < 90:
            c.showPage()
            y = height - 70

    c.showPage()
    c.save()


def _wrap(text: str, limit: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= limit:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    build_drawing(os.path.join(OUT, "gambar_denah_rev_A.pdf"), "A")
    build_drawing(os.path.join(OUT, "gambar_denah_rev_B.pdf"), "B")
    build_boq(os.path.join(OUT, "boq_rev_A.xlsx"), "A")
    build_boq(os.path.join(OUT, "boq_rev_B.xlsx"), "B")
    build_rks(os.path.join(OUT, "rks_gedung_2lantai.pdf"))
    print("Selesai: 5 file dibuat di", OUT)
