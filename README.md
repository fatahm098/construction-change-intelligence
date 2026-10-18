# Construction Change Intelligence

Platform AI untuk kontraktor dan konsultan Indonesia: mendeteksi perubahan antarrevisi
gambar teknik, memverifikasi dimensi, lalu menghitung dampak biaya terhadap BOQ/RAB —
dengan perhitungan yang **deterministik dan bisa diaudit**, bukan tebakan LLM.

Repositori ini berisi backend FastAPI, frontend Next.js, modul RAG untuk dokumen
regulasi konstruksi (SNI, AHSP, SMKK), serta paket dokumen uji siap pakai.

---

## 1. Fitur

### 1.1 Change Intelligence (inti produk)
- Upload dua revisi gambar PDF (rev 0 vs rev 1); halaman diraster otomatis 150 DPI.
- Penyelarasan gambar dengan **SIFT + RANSAC homography** agar pergeseran hasil scan
  tidak dianggap perubahan.
- Deteksi region berubah lewat *absolute pixel differencing*, dilasi, dan ekstraksi
  kontur (ambang luas region dapat diatur, default 350 px²).
- **OCR per region** (EasyOCR) yang mengekstrak *kandidat dimensi* per baris teks,
  sehingga satu region berisi `K1 300x300` dan `K2 400x400` tidak lagi tertukar.
- UI human-in-the-loop: tinjau bounding box, konfirmasi dimensi, atau tolak
  *false positive* sebelum biaya dihitung.
- Volume dihitung rumus murni untuk elemen **kolom, balok, dan pelat**.
- Penautan region ke item BOQ (dengan saran otomatis berbasis kata kunci) menghasilkan
  **cost impact** per region dan total *cost delta* proyek.
- Ekspor audit trail ke CSV.
- Analisis bisa dijalankan sinkron atau sebagai **background job** (ARQ + Redis).

### 1.2 BOQ & RAB
- Upload RAB/BOQ dari Excel (`.xlsx`/`.xls`) dengan parser header fleksibel.
- Katalog **AHSP** (Analisa Harga Satuan Pekerjaan) + endpoint seeding.
- Rekap RAB per proyek.

### 1.3 Document Q&A (RAG)
- Upload dokumen PDF (RKS, SNI, AHSP, SMKK) → chunking → embedding → vector store.
- Tanya jawab dengan **sitasi halaman**; riwayat percakapan tersimpan per proyek.
- Vector store dihidrasi ulang otomatis saat startup.
- Provider embedding dapat diganti (lihat §6) dan korpus dapat di-reindex tanpa upload ulang.

### 1.4 Progress & EVM
- Input progress periodik (upsert per periode).
- Perhitungan **BAC, PV, EV, AC, SV, CV, SPI, CPI, EAC, ETC, VAC** dari BOQ kontrak.

### 1.5 Variation Order & RFI
- CRUD Variation Order lengkap dengan alur status.
- RFI (Request for Information): buat, jawab, dan catat waktu jawaban.

### 1.6 QC / Mutu
- Inspeksi berbasis checklist per kategori pekerjaan.
- Update hasil per item, ringkasan *pass rate* dan rekap per kategori.

### 1.7 K3 / Keselamatan
- Laporan K3 harian dengan kategori, tingkat keparahan, dan status tindak lanjut.
- Ringkasan per proyek untuk pelaporan (mendukung kewajiban SMKK).

### 1.8 Laporan siap unduh
- **RAB**: Excel (`.xlsx`) dan PDF.
- **EVM**: Excel.
- **QC**: Excel.
- Tombol unduh tersedia langsung di UI (membawa token auth, bukan tautan publik).

### 1.9 Auth & pengaturan runtime
- JWT Bearer + role (`ADMIN`, `ENGINEER`, dst.); user pertama otomatis `ADMIN`.
- **Gerbang auth global** (middleware): saat `AUTH_ENABLED=true`, seluruh API wajib
  token kecuali `/health`, `/health/ready`, login/register, docs, dan `/static/*`.
- Registrasi mandiri ditutup setelah admin pertama ada.
- Halaman **Pengaturan** untuk API key LLM: disimpan **terenkripsi (Fernet)** di server,
  hanya ditampilkan dalam bentuk mask, tidak pernah dikirim balik ke browser.
- Uji koneksi provider langsung dari UI.

### 1.10 LLM pluggable
Empat provider dengan antarmuka sama: `deepseek` (default), `openai`, `ollama`, dan
`local` (offline, tanpa API key — untuk demo).

### 1.11 Observability & deployment
- Log JSON terstruktur + `X-Request-ID` per request.
- `/health` (liveness) dan `/health/ready` (cek DB + status konfigurasi LLM).
- Dockerfile backend & frontend, `docker-compose.yml` (dev) dan
  `docker-compose.prod.yml` (produksi, auth wajib aktif).

---

## 2. Prinsip desain: LLM tidak boleh menghitung

Pembagian tugasnya tegas:

| Lapisan | Tugas | Boleh pakai LLM? |
|---|---|---|
| Vision (OpenCV) | Alignment & deteksi region | Tidak |
| OCR (EasyOCR) | Baca teks/dimensi | Tidak |
| Rule engine (Python) | Volume, biaya, EVM | Tidak |
| LLM | Ringkasan, tanya jawab dokumen, saran | Ya |

Semua angka yang masuk ke Variation Order berasal dari fungsi murni yang bisa diuji
ulang. LLM hanya membantu membaca dan menjelaskan, sehingga hasilnya tidak bisa
"berhalusinasi" menjadi nilai kontrak.

---

## 3. Struktur repositori

```
construction-change-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Entry point, CORS, auth gate, static files
│   │   ├── database.py             # SQLAlchemy (SQLite dev / Postgres prod)
│   │   ├── models/entities.py      # Seluruh entitas ORM
│   │   ├── schemas/                # Pydantic v2
│   │   ├── kernel/
│   │   │   ├── config.py           # Settings dari .env
│   │   │   ├── crypto.py           # Fernet untuk API key
│   │   │   ├── settings_store.py   # Prioritas DB → env → default
│   │   │   ├── auth/               # JWT, dependency role, middleware gate
│   │   │   ├── llm/                # base, openai, deepseek, ollama, local, embedding
│   │   │   ├── rag/                # chunker, embedder, store, retriever
│   │   │   └── observability/      # logging JSON, request-id, health
│   │   ├── modules/                # Registry fitur (lihat modules/__init__.py)
│   │   │   ├── change_intel/       # projects, drawings, analysis, boq, export
│   │   │   ├── boq_rab/  doc_qa/  progress/  vo_rfi/
│   │   │   ├── qc/  safety/  reports/  settings/  auth/  jobs/
│   │   └── services/               # pdf, vision, ocr, calc, boq, ahsp_seed
│   ├── migrations/                 # Alembic
│   ├── tests/                      # pytest (23 test)
│   ├── scripts/                    # seed_demo.py, seed_ahsp.py, test_rag.py (manual)
│   ├── data/reference/             # PDF regulasi (tidak di-commit, ~45 MB)
│   ├── pytest.ini  ruff.toml  Dockerfile  requirements.txt
├── frontend/
│   └── src/
│       ├── app/                    # /, change-intel, boq-rab, doc-qa, progress,
│       │                           # vo-rfi, qc, k3, settings, login
│       ├── components/             # Sidebar, dsb.
│       └── lib/                    # api.ts, reports.ts, types.ts
├── samples/                        # Paket dokumen uji + ground truth
├── DEPLOY.md                       # Panduan deploy produksi
├── docker-compose.yml              # Dev (backend + Postgres)
└── docker-compose.prod.yml         # Produksi (auth wajib aktif)
```

---

## 4. Menjalankan secara lokal

### Prasyarat
- Python 3.11/3.12
- Node.js 18+
- EasyOCR berjalan di CPU (sudah termasuk dependensi Python)

### Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate        # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

> **Windows, cara tercepat:** setelah venv dan `npm install` selesai sekali,
> klik dua kali **`start-web.bat`** di root repo. Backend (:8000) dan frontend
> (:3000) menyala sekaligus, lalu browser terbuka otomatis.

API docs: http://localhost:8000/docs · Health: http://localhost:8000/health

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:3000

### Konfigurasi awal
Salin `.env.example` → `.env` di root repo, lalu isi minimal salah satu:

```env
# Pakai LLM sungguhan
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
DEEPSEEK_API_KEY=sk-...

# Atau mode offline tanpa biaya
LLM_PROVIDER=local
```

API key juga bisa diisi lewat halaman **Pengaturan** di UI (disimpan terenkripsi di DB
dan mengalahkan nilai `.env`). Restart backend setelah mengubah `.env`.

### Demo cepat (data contoh sekali jalan)

Setelah backend dan frontend hidup:

```bash
cd backend
./.venv/Scripts/python.exe scripts/seed_demo.py
```

Script ini membuat proyek **"Gedung Kantor 2 Lantai — Demo"** berisi data di semua
modul, memakai file dari `samples/`:

| Modul | Isi demo |
|---|---|
| BOQ/RAB | 29 item, total Rp 907.992.000 |
| Change Intelligence | 12 region dari denah rev A vs rev B; region terbesar terverifikasi kolom 300×300 → 400×400 |
| Cost impact | Rp 477.750 dari volume 0,315 → 0,560 m³ × harga satuan BOQ |
| VO / RFI | VO-001 (submitted) dan RFI-001 yang sudah dijawab |
| Progress / EVM | 2 periode (Feb–Mar 2026) |
| QC | 2 inspeksi: satu gagal (selimut beton), satu lulus → pass rate 50% |
| K3 | 1 laporan *unsafe act* severity tinggi |
| Doc Q&A | RKS 7 pasal terindeks, siap ditanya dengan sitasi halaman |

Script bersifat idempoten: kalau proyek demo sudah ada, tidak ada yang diubah.
Untuk memulai dari nol, hapus proyek demo lewat UI lalu jalankan ulang.

---

## 5. Paket dokumen uji (`samples/`)

| File | Isi |
|---|---|
| `gambar_denah_rev_A.pdf` / `_rev_B.pdf` | Denah lantai 1, dua revisi (bay + kolom baru) |
| `boq_rev_A.xlsx` / `_rev_B.xlsx` | RAB 29 → 31 item, Rp 907,9 jt → Rp 1.025,6 jt |
| `rks_gedung_2lantai.pdf` | RKS 7 pasal untuk uji Document Q&A |
| `ground_truth.md` | Daftar perubahan yang seharusnya terdeteksi |
| `generate_samples.py` | Generator ulang seluruh file di atas |

Alur uji lengkap ada di `samples/README.md`. Regenerasi:

```bash
backend/.venv/Scripts/python.exe samples/generate_samples.py
```

---

## 6. Konfigurasi

| Variabel | Default | Keterangan |
|---|---|---|
| `LLM_PROVIDER` | `deepseek` | `deepseek` \| `openai` \| `ollama` \| `local` |
| `LLM_MODEL` | `deepseek-chat` | Model chat |
| `LLM_BASE_URL` | `https://api.deepseek.com/v1` | Endpoint OpenAI-compatible |
| `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` | — | Kunci provider (bisa juga via UI) |
| `EMBEDDING_PROVIDER` | `hash` | `hash` (offline) \| `openai` (semantik) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Model embedding |
| `EMBEDDING_API_KEY` | — | Kosong = fallback `OPENAI_API_KEY` |
| `AUTH_ENABLED` | `false` | `true` = seluruh API wajib JWT |
| `JWT_SECRET` | — | **Wajib diganti di produksi** |
| `SETTINGS_ENCRYPTION_KEY` | — | Kunci enkripsi API key di DB |
| `JOBS_ENABLED` | `false` | `true` = analisis async via ARQ |
| `REDIS_URL` | `redis://localhost:6379/0` | Broker job |
| `DATABASE_URL` | SQLite `backend/construction.db` | Postgres untuk produksi |
| `CORS_ORIGINS` | `http://localhost:3000` | Dipisah koma |

**Mengganti provider embedding** mengubah dimensi vektor, jadi korpus harus dihitung
ulang:

```bash
curl -X POST http://localhost:8000/api/doc-qa/reindex \
  -H "Authorization: Bearer <token>"
```

---

## 7. Ringkasan API (49 endpoint)

| Grup | Path | Fungsi |
|---|---|---|
| Projects | `GET/POST /api/projects`, `GET /api/projects/{id}` | CRUD proyek + ringkasan |
| Drawings | `POST /api/drawings/upload` | Upload PDF + raster otomatis |
| Analysis | `POST /api/analysis/run`, `POST /api/analysis/region/{id}/verify` | Diff, verifikasi dimensi |
| BOQ | `POST /api/boq/upload`, `POST /api/boq/link-region` | RAB + cost impact |
| AHSP | `GET /api/ahsp`, `POST /api/ahsp/seed` | Katalog harga satuan |
| Doc Q&A | `POST /api/projects/{id}/documents`, `POST /api/projects/{id}/chat` | RAG + sitasi |
| Reindex | `POST /api/doc-qa/reindex` | Hitung ulang embedding korpus |
| Progress | `GET/POST /api/progress/{id}/entries` | EVM |
| VO / RFI | `GET/POST /api/vo/{id}`, `POST /api/rfi/{id}/answer` | Perubahan & pertanyaan |
| QC | `GET/POST /api/qc/{id}`, `PATCH /api/qc/item/{id}`, `PATCH /api/qc/inspection/{id}/status` | Inspeksi mutu + finalisasi lulus/gagal |
| K3 | `GET/POST /api/k3/{id}`, `PATCH /api/k3/{id}/status` | Laporan keselamatan |
| Reports | `GET /api/reports/{rab,evm,qc}/{id}.xlsx`, `GET /api/reports/rab/{id}.pdf` | Unduhan |
| Settings | `GET/PUT /api/settings/llm`, `POST /api/settings/llm/test` | API key terenkripsi |
| Auth | `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me` | JWT |
| Jobs | `POST /api/jobs/analysis`, `GET /api/jobs/{id}` | Async |
| Ops | `GET /health`, `GET /health/ready` | Liveness & readiness |

Dokumentasi interaktif lengkap: `/docs`.

---

## 8. Testing & kualitas

```bash
cd backend
./.venv/Scripts/python.exe -m ruff check app --select F,E9
DATABASE_URL=sqlite:///./tmp_test.db ./.venv/Scripts/python.exe -m pytest -q
rm -f tmp_test.db
```

Cakupan saat ini: 23 test (alur end-to-end proyek, job async, settings/API key,
gerbang auth, embedding + reindex, OCR per region dengan sample gambar).

Frontend:

```bash
cd frontend
npx tsc --noEmit
npm run build
```

---

## 9. Deploy produksi

Panduan lengkap ada di **[DEPLOY.md](DEPLOY.md)**. Ringkasnya:

```bash
cp .env.example .env    # isi JWT_SECRET, SETTINGS_ENCRYPTION_KEY, API key, CORS
docker compose -f docker-compose.prod.yml up -d --build
```

`docker-compose.prod.yml` memaksa `AUTH_ENABLED=true` dan menolak jalan bila secret
kosong. Setelah container hidup, daftarkan admin pertama lewat UI `/login`, lalu
registrasi tertutup otomatis.

---

## 10. Batasan yang diketahui

- **Gambar harus PDF** (belum mendukung DWG/DXF).
- OCR membaca per baris, bukan per simbol; region yang sangat padat teks masih perlu
  verifikasi manusia.
- Deteksi perubahan berbasis piksel: teks yang bergeser sedikit ikut terdeteksi sebagai
  region (noise wajar, perlu difilter pengguna).
- Dokumen hasil scan tanpa layer teks (mis. UU 2/2017) belum bisa masuk RAG karena
  butuh OCR terlebih dahulu.
- Belum ada versioning dokumen teks (RKS rev A vs rev B); saat ini perbandingan revisi
  baru tersedia untuk gambar.
- Vector store masih in-memory yang dihidrasi dari DB — cocok untuk satu instance,
  belum untuk multi-instance (rencana: pgvector).

---

## 11. Lisensi & catatan

Proyek internal/eksperimental untuk alur kerja konstruksi. Dokumen regulasi di
`backend/data/reference/` tidak disertakan dalam repositori karena ukuran dan hak
distribusinya; unduh dari sumber resmi (JDIH PUPR, BSN) lalu unggah melalui UI.
