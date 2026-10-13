"""Modul 4: Progress & EVM (Earned Value Management).

Kurva-S progres periodik + analisis nilai hasil (EVM). Seluruh perhitungan
deterministik (bukan LLM) dan kumulatif dari periode terakhir:

  - BAC = Σ (volume_kontrak × harga_satuan) seluruh item BOQ
  - PV  = planned_pct / 100 × BAC
  - EV  = actual_pct  / 100 × BAC
  - AC  = actual_cost
  - SV  = EV − PV ; CV = EV − AC
  - SPI = EV / PV ; CPI = EV / AC
  - EAC = BAC / CPI ; ETC = EAC − AC ; VAC = BAC − EAC
"""

from __future__ import annotations
