"""
Script untuk men-generate synthetic structural drawing (Rev 0 vs Rev 1)
dan BOQ file untuk keperluan validasi spike dan testing deterministik.
"""

import os
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
import openpyxl

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_drawings")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_grid_and_columns(c, width, height, rev_num):
    # Set background white
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Title Block
    c.setStrokeColorRGB(0.1, 0.1, 0.1)
    c.setLineWidth(2)
    c.rect(40, 40, width - 80, height - 80)

    # Header info
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(60, height - 70, "PROYEK GEDUNG KANTOR 4 LANTAI")
    c.setFont("Helvetica", 14)
    c.drawString(60, height - 90, f"GAMBAR DENAH KOLOM & BALOK LT. 1 — REVISI {rev_num}")

    # Revision box
    c.setFont("Helvetica-Bold", 12)
    c.rect(width - 240, height - 100, 180, 50)
    c.drawString(width - 230, height - 75, f"STATUS: REV.{rev_num}")
    c.setFont("Helvetica", 10)
    c.drawString(width - 230, height - 90, "SCALE 1:100  |  DATE: OCT 2026")

    # Grid definition (3x3 grid)
    x_coords = [300, 550, 800]
    y_coords = [200, 420, 640]
    grid_x_labels = ["1", "2", "3"]
    grid_y_labels = ["A", "B", "C"]

    # Draw grid lines
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.8)
    c.setDash(6, 3)

    for x in x_coords:
        c.line(x, 150, x, 700)
    for y in y_coords:
        c.line(220, y, 880, y)

    c.setDash()  # solid

    # Grid bubbles
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    for i, x in enumerate(x_coords):
        c.circle(x, 720, 14, stroke=True, fill=False)
        c.drawCentredString(x, 715, grid_x_labels[i])
    for j, y in enumerate(y_coords):
        c.circle(200, y, 14, stroke=True, fill=False)
        c.drawCentredString(200, y - 4, grid_y_labels[j])

    # Connecting beams
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.setLineWidth(1.5)
    for y in y_coords:
        c.line(x_coords[0], y, x_coords[-1], y)
    for x in x_coords:
        c.line(x, y_coords[0], x, y_coords[-1])

    # Columns at intersections
    # Grid (2, B) at (550, 420) is the one that changes!
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0.85, 0.85, 0.85)

    for i, x in enumerate(x_coords):
        for j, y in enumerate(y_coords):
            # Check if this is grid B2
            is_target_column = (i == 1 and j == 1)

            if is_target_column:
                if rev_num == 0:
                    # Rev 0: Kolom K1 (30x30 pt scale representation)
                    size = 28
                    dim_text = "K1 (300x300)"
                else:
                    # Rev 1: Kolom K1 diperbesar jadi 400x400
                    size = 38
                    dim_text = "K1 (400x400)"
            else:
                # Kolom standar lainnya: 300x300
                size = 28
                dim_text = "K1 (300x300)"

            # Draw filled column
            half = size / 2.0
            c.rect(x - half, y - half, size, size, fill=True, stroke=True)

            # Hatch lines inside column
            c.setLineWidth(0.5)
            c.line(x - half, y - half, x + half, y + half)
            c.line(x - half, y + half, x + half, y - half)
            c.setLineWidth(1.5)

            # Annotation text
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(x + half + 6, y - 4, dim_text)

    # General Notes
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, 140, "CATATAN STRUKTUR:")
    c.setFont("Helvetica", 9)
    c.drawString(60, 125, "1. Mutu beton struktur: fc' = 25 MPa (K-300).")
    c.drawString(60, 110, "2. Tinggi kolom efektif lantai 1 = 4.00 meter.")
    c.drawString(60, 95, "3. Seluruh dimensi dalam milimeter (mm) kecuali dinyatakan lain.")


def generate_synthetic_drawings():
    rev0_path = os.path.join(OUTPUT_DIR, "drawing_rev0.pdf")
    rev1_path = os.path.join(OUTPUT_DIR, "drawing_rev1.pdf")

    # Generate Rev 0
    c0 = canvas.Canvas(rev0_path, pagesize=landscape(A3))
    w, h = landscape(A3)
    draw_grid_and_columns(c0, w, h, rev_num=0)
    c0.save()
    print(f"Generated Rev 0: {rev0_path}")

    # Generate Rev 1
    c1 = canvas.Canvas(rev1_path, pagesize=landscape(A3))
    draw_grid_and_columns(c1, w, h, rev_num=1)
    c1.save()
    print(f"Generated Rev 1: {rev1_path}")


def generate_sample_boq():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "RAB Struktur"

    headers = [
        "No",
        "Kode Item",
        "Uraian Pekerjaan",
        "Satuan",
        "Volume Kontrak",
        "Harga Satuan (IDR)",
        "Total (IDR)",
    ]
    ws.append(headers)

    items = [
        [1, "STR-K-01", "Pekerjaan Beton Kolom K1 (fc' 25 MPa / K-300)", "m3", 15.5, 1250000, 19375000],
        [2, "STR-K-02", "Pekerjaan Pembesian Kolom K1 (BJTS 420B)", "kg", 2480, 15500, 38440000],
        [3, "STR-K-03", "Pekerjaan Bekisting Kolom K1 2x Pakai", "m2", 120.0, 185000, 22200000],
        [4, "STR-B-01", "Pekerjaan Beton Balok B1 (fc' 25 MPa / K-300)", "m3", 22.0, 1250000, 27500000],
        [5, "STR-P-01", "Pekerjaan Beton Pelat Lantai t=12cm", "m3", 35.0, 1250000, 43750000],
    ]

    for item in items:
        ws.append(item)

    boq_path = os.path.join(OUTPUT_DIR, "sample_boq.xlsx")
    wb.save(boq_path)
    print(f"Generated Sample BOQ: {boq_path}")


if __name__ == "__main__":
    generate_synthetic_drawings()
    generate_sample_boq()
