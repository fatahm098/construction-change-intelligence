"""Modul Settings: pengaturan runtime aplikasi (provider LLM + API key).

API key disimpan terenkripsi di DB (lihat `app.kernel.crypto`) dan tidak pernah
dikirim ke klien. Logika akses data ada di `app.kernel.settings_store`.
"""
