"""Modul 3: BOQ & RAB (Rencana Anggaran Biaya) berbasis AHSP.

Perhitungan RAB deterministik:
  - RAB kontrak  = Σ (volume_kontrak × harga_satuan)
  - RAB adjusted = Σ ((volume_kontrak + Δvolume variasi) × harga_satuan)
  - Δ RAB        = RAB adjusted − RAB kontrak
Tidak melibatkan LLM.
"""
