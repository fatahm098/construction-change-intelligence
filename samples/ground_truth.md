# Ground truth: Rev A → Rev B

Dipakai sebagai pembanding objektif saat menguji analisis. Kalau sistem melaporkan
perubahan di luar daftar ini, itu false positive; kalau melewatkan salah satu, itu
false negative.

## Perubahan gambar

| # | Perubahan | Detail |
|---|---|---|
| G1 | Bangunan diperlebar 1 bay | Lebar total 10.000 mm → 11.000 mm; sisi kanan bertambah 1.000 mm |
| G2 | Ruang baru | PANTRY di sisi kanan (dulu area kosong) |
| G3 | Kolom baru K2 | 400x400 mm, ditambahkan di sudut kanan atas |
| G4 | Dimensi berubah | "6000" → "7000"; "10000" → "11000" |
| G5 | Dinding partisi | Dinding vertikal baru memisahkan ruang rapat dan pantry |

Yang **tidak** berubah: kolom K1 300x300 (jumlah 3 → 4 karena bay baru),
tinggi lantai 5.500 mm, posisi ruang tamu dan gudang.

## Perubahan BOQ

| Kode | Uraian | Rev A | Rev B | Δ |
|---|---|---|---|---|
| 2.3 | Pondasi footplat K-300 | 24 m³ | 30 m³ | +6 m³ |
| 3.1 | Kolom beton | 18 m³ @ Rp 1.950.000 | 21 m³ @ Rp 2.150.000 | +3 m³, mutu K-300 → K-350 |
| 3.4 | Pembesian D13 | 12.400 kg | 13.800 kg | +1.400 kg |
| 4.1 | Dinding | 420 m² @ Rp 165.000 (bata merah) | 440 m² @ Rp 195.000 (bata ringan AAC) | +20 m², spesifikasi berubah |
| 6.1 | Keramik | 240 m² @ Rp 185.000 (60x60) | 250 m² @ Rp 245.000 (80x80) | +10 m², spesifikasi berubah |
| 6.2 | Plafon gypsum | 240 m² @ Rp 135.000 (9 mm) | 250 m² @ Rp 155.000 (12 mm) | +10 m², tebal berubah |
| 5.4 | Waterproofing atap | — | 260 m² @ Rp 125.000 | item baru |
| 4.4 | Partisi gypsum pantry | — | 24 m² @ Rp 165.000 | item baru |

## Angka acuan

- Total Rev A: **Rp 907.992.000**
- Total Rev B: **Rp 1.025.602.000**
- Selisih: **Rp 117.610.000** (+12,95%)
- Jumlah item: 29 → 31

## Yang seharusnya dihasilkan sistem

1. Minimal 1 region perubahan besar (bay baru + K2) dengan area > 50.000 px².
2. OCR membaca "K2 400x400" pada region tersebut.
3. Verifikasi dimensi kolom 300x300 → 400x400 menghasilkan volume deterministik
   (bukan tebakan LLM): 0,09 m³ → 0,16 m³ per meter tinggi.
4. Cost impact menunjuk ke item BOQ 3.1 dan memakai harga satuan Rp 2.150.000.
5. Dokumen VO yang dibuat memuat dasar perubahan (nomor gambar A-101, rev A → B).

## Catatan kelemahan yang diketahui

- OCR membaca teks dalam satu region sekaligus, jadi kalau satu region memuat
  K1 dan K2, dimensi yang diambil bisa milik kolom pertama. Pecah region atau
  verifikasi manual diperlukan.
- Perubahan teks kecil (mis. "RUANG RAPAT" bergeser) ikut terdeteksi sebagai
  region; ini noise yang wajar dan perlu difilter manusia.
