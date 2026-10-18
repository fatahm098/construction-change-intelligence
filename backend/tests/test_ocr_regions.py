"""Uji end-to-end kandidat dimensi OCR pada sample denah rev A vs rev B.

Alur: rasterize PDF -> SIFT alignment -> deteksi region -> kandidat OCR.
Membuktikan region yang memuat K1 300x300 dan K2 400x400 tidak lagi
kehilangan kandidat 400x400.
"""

import os

import cv2
import pytest

from app.services.ocr_service import extract_dimension_candidates
from app.services.pdf_service import rasterize_pdf_page
from app.services.vision_service import align_drawings_sift, detect_changed_regions

SAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "samples"))
PDF_REV_A = os.path.join(SAMPLES_DIR, "gambar_denah_rev_A.pdf")
PDF_REV_B = os.path.join(SAMPLES_DIR, "gambar_denah_rev_B.pdf")


def test_revision_b_region_has_400_candidate(tmp_path):
    if not (os.path.exists(PDF_REV_A) and os.path.exists(PDF_REV_B)):
        pytest.skip("sample gambar_denah_rev_A/B.pdf tidak tersedia")

    png_a, _, _ = rasterize_pdf_page(PDF_REV_A, dpi=150, output_dir=str(tmp_path))
    png_b, _, _ = rasterize_pdf_page(PDF_REV_B, dpi=150, output_dir=str(tmp_path))

    img_v0 = cv2.imread(png_a)
    img_v1 = cv2.imread(png_b)
    assert img_v0 is not None and img_v1 is not None

    aligned_v0, _ = align_drawings_sift(img_v1, img_v0)
    regions, _ = detect_changed_regions(aligned_v0, img_v1, min_area=350, output_dir=str(tmp_path))
    assert regions, "tidak ada region perubahan yang terdeteksi"

    regions_with_400 = []
    for region in regions:
        candidates = extract_dimension_candidates(region["crop_v1"])
        if any(c["dims"] == (400, 400) for c in candidates):
            regions_with_400.append(region)

    assert regions_with_400, "tidak ada region revisi B yang menghasilkan kandidat (400, 400)"

    # Region yang sama harus tetap memuat kandidat lama 300x300 pada revisi A,
    # sehingga pasangan 300x300 -> 400x400 bisa dipilih oleh analysis_service.
    region = regions_with_400[0]
    dims_v0 = {c["dims"] for c in extract_dimension_candidates(region["crop_v0"])}
    assert (300, 300) in dims_v0


def test_dimension_lines_without_element_label_are_ignored(tmp_path):
    if not os.path.exists(PDF_REV_B):
        pytest.skip("sample gambar_denah_rev_B.pdf tidak tersedia")

    png_b, _, _ = rasterize_pdf_page(PDF_REV_B, dpi=150, output_dir=str(tmp_path))
    img_v1 = cv2.imread(png_b)
    assert img_v1 is not None

    # Crop kecil di sekitar angka garis "7000" (tanpa label elemen).
    crop = img_v1[600:700, 600:780]
    candidates = extract_dimension_candidates(crop)
    assert all(c["dims"] != (7000, 7000) for c in candidates)
    assert all(100 <= c["dims"][0] <= 2000 and 100 <= c["dims"][1] <= 2000 for c in candidates)
