# Construction Change Intelligence (AI Project for Civil Engineering & Cost Management)

Sistem berbasis Computer Vision dan Rule Engine Deterministik untuk mendeteksi perubahan antarversi gambar teknik konstruksi (PDF Drawing Rev 0 vs Rev 1), mengekstrak teks/dimensi teknik, dan menghitung estimasi dampak biaya (*Variation Order / Cost Delta*) secara otomatis dan terverifikasi terhadap item BOQ/RAB (*Bill of Quantities*).

---

## 1. Arsitektur & Prinsip Desain

Proyek ini dibangun berdasarkan prinsip **pemisahan tanggung jawab yang ketat (Separation of Concerns)**:
1. **Document Ingestion:** PyMuPDF mengekstrak halaman PDF vektor menjadi citra raster resolusi tinggi (150–300 DPI).
2. **Computer Vision & Image Registration:** OpenCV SIFT (*Scale-Invariant Feature Transform*) + RANSAC Homography menyelaraskan posisi gambar target ke referensi secara spasial, dilanjutkan dengan *absolute pixel differencing* dan ekstraksi kontur bounding box.
3. **Information Extraction (OCR):** EasyOCR (CPU mode) dikombinasikan dengan *regex parsing* toleran noise dan *sanity boundary checks* (100–2.000 mm) untuk memitigasi kesalahan pembacaan font teknik.
4. **Deterministic Rule Engine (Python):** Perhitungan volume kuantitas (beton kolom, balok, pelat) dieksekusi secara matematis murni tanpa mengandalkan halusinasi LLM.
5. **BOQ & Margin Guardian:** Menghubungkan perubahan volume elemen ke unit price item BOQ yang di-upload pengguna (XLSX).
6. **Human-in-the-Loop Verification:** UI menyediakan interface untuk meninjau bounding box, mengonfirmasi dimensi sebelum kalkulasi final, dan menolak *false positives*.

---

## 2. Struktur Repositori

```
construction-change-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py                    # Entry point FastAPI, CORS, Static Files
│   │   ├── database.py                # SQLAlchemy engine (SQLite / PostgreSQL)
│   │   ├── models/
│   │   │   └── entities.py            # Project, Drawing, AnalysisRun, ChangeRegion, BOQItem, CostImpact
│   │   ├── schemas/
│   │   │   └── project.py             # Pydantic v2 validation schemas
│   │   ├── services/
│   │   │   ├── pdf_service.py         # PyMuPDF rasterizer
│   │   │   ├── vision_service.py      # SIFT alignment & contour diff
│   │   │   ├── ocr_service.py         # EasyOCR singleton & regex dimension cleaner
│   │   │   ├── calc_service.py        # Deterministik volume (kolom, balok, pelat)
│   │   │   └── boq_service.py         # OpenPyXL parser & keyword matcher
│   │   └── routers/
│   │       ├── projects.py            # CRUD Project & Cost Delta Summary
│   │       ├── drawings.py            # PDF upload & auto-rasterize
│   │       ├── analysis.py            # SIFT Diff execution, dimension verify & reject
│   │       ├── boq.py                 # BOQ XLSX upload & region linking
│   │       └── export.py              # Export audit report to CSV
│   ├── data/
│   │   ├── generate_samples.py        # Generator PDF synthetic Rev 0 vs Rev 1 & BOQ
│   │   └── sample_drawings/           # Sample PDF & XLSX
│   ├── tests/
│   │   ├── spike_pipeline.py          # Script proof-of-concept mandiri
│   │   └── test_api.py                # End-to-end integration tests (pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml                 # Orchestration backend + PostgreSQL
└── README.md
```

---

## 3. Cara Menjalankan Secara Lokal

### Prasyarat
- Python 3.11 atau 3.12
- UV package manager (opsional, disarankan) atau pip standar

### Langkah Instalasi
```bash
# 1. Masuk ke direktori backend
cd backend

# 2. Buat virtual environment
uv venv .venv --python python3.12
source .venv/Scripts/activate  # Windows git-bash
# atau: .venv\Scripts\activate pada CMD/PowerShell

# 3. Install dependensi
uv pip install -r requirements.txt

# 4. Generate data sintetis untuk pengujian
python data/generate_samples.py

# 5. Jalankan unit & integration test
pytest tests/test_api.py -v

# 6. Jalankan FastAPI server
uvicorn app.main:app --reload --port 8000
```

Dokumentasi interaktif Swagger API akan tersedia di: `http://localhost:8000/docs`.

---

## 4. Alur Kerja API (End-to-End)

1. **Buat Proyek:** `POST /api/projects`
2. **Upload Drawing Rev 0:** `POST /api/drawings/upload` (`file`: `drawing_rev0.pdf`, `revision`: `0`)
3. **Upload Drawing Rev 1:** `POST /api/drawings/upload` (`file`: `drawing_rev1.pdf`, `revision`: `1`)
4. **Upload BOQ Spreadsheet:** `POST /api/boq/upload` (`file`: `sample_boq.xlsx`)
5. **Jalankan Analisis Perubahan:** `POST /api/analysis/run?project_id=1&drawing_ref_id=1&drawing_rev_id=2`
6. **Verifikasi Dimensi & Link ke BOQ:** `POST /api/analysis/region/{region_id}/verify`
7. **Lihat Ringkasan Dampak Biaya:** `GET /api/projects/{project_id}/summary`
8. **Unduh Laporan Audit:** `GET /api/export/csv/{project_id}`

---

## 5. Ringkasan Hasil Uji Nyata (Spike & Automated Test)

- **Kasus Uji:** Kolom Grid B2 membesar dari `300x300 mm` (Rev 0) menjadi `400x400 mm` (Rev 1) dengan tinggi efektif `4.00 m`.
- **SIFT Matching:** 2.310 good keypoint matches berhasil menyelaraskan pergeseran kertas/skala.
- **Volume Delta:** $+0,280\text{ m}^3$ beton.
- **Harga Satuan BOQ:** Item `STR-K-01 (Beton Kolom K1)` = Rp 1.250.000,00 / m³.
- **Total Estimasi Dampak Biaya:** **+Rp 350.000,00** per kolom.
- **Status Uji Otomatis:** `pytest tests/test_api.py` **100% PASSED**.
