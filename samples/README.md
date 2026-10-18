# Paket dokumen uji

Dokumen contoh untuk mencoba platform dari ujung ke ujung tanpa memakai data klien.
Semua file dibuat sintetis tetapi mengikuti format nyata (RKS, RAB/BOQ, denah).

| File | Isi | Dipakai untuk |
|---|---|---|
| `gambar_denah_rev_A.pdf` | Denah lantai 1, revisi A | Drawing ref (sebelum) |
| `gambar_denah_rev_B.pdf` | Denah lantai 1, revisi B | Drawing rev (sesudah) |
| `boq_rev_A.xlsx` | RAB 29 item, Rp 907.992.000 | BOQ kontrak |
| `boq_rev_B.xlsx` | RAB 31 item, Rp 1.025.602.000 | BOQ revisi |
| `rks_gedung_2lantai.pdf` | RKS 7 pasal (mutu beton, dinding, K3, dll.) | Doc QA / RAG |
| `ground_truth.md` | Daftar perubahan yang seharusnya terdeteksi | Pembanding hasil |

## Cara pakai (alur uji lengkap)

1. **Buat proyek** di halaman utama, misal "Gedung Kantor 2 Lantai".
2. **Upload BOQ**: `boq_rev_A.xlsx` → tab BOQ/RAB. Cek 29 item masuk.
3. **Upload gambar**: `gambar_denah_rev_A.pdf` sebagai ref, `gambar_denah_rev_B.pdf` sebagai rev.
4. **Jalankan analisis** di tab Change Intelligence. Target: region perubahan utama
   (bay baru + kolom K2) terdeteksi dengan area > 50.000 px².
5. **Verifikasi region** → pilih tipe elemen `column`, isi dimensi 300x300 (sebelum)
   dan 400x400 (sesudah), tinggi 3,5 m. Volume dihitung sistem, bukan LLM.
6. **Link ke item BOQ** "Kolom beton K-300 300x300" → cek cost impact.
7. **Doc QA**: upload `rks_gedung_2lantai.pdf`, tanya "berapa mutu beton kolom?"
   dan "berapa tebal plafon gypsum?" — jawaban harus menyebut K-300 dan 9 mm
   dengan kutipan halaman.

## Regenerasi

```bash
backend/.venv/Scripts/python.exe samples/generate_samples.py
```

Angka BOQ dihitung ulang otomatis; kalau `ITEMS` diubah, perbarui `ground_truth.md`.
