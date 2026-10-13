"""Modul 6: Reports (unduhan Excel & PDF).

Menghasilkan berkas yang bisa diunduh untuk sebuah proyek:

  - RAB (Rencana Anggaran Biaya) — Excel & PDF
  - EVM (Earned Value Management) — Excel
  - QC (inspeksi mutu) — Excel

Seluruh angka berasal dari service yang sudah ada (`boq_rab`, `progress`) dan
kueri langsung ke `Inspection`/`InspectionItem`. Tidak ada perhitungan ulang
dan tidak melibatkan LLM.
"""

from __future__ import annotations
