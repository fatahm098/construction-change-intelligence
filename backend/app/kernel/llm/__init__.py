"""Lapisan LLM pluggable.

Provider abstraksi (`base.py`) dengan implementasi konkret per provider
(`ollama.py`, `openai.py`) dan factory (`factory.py`) yang memilih berdasarkan
`settings.llm_provider`.

Prinsip guardrail: LLM TIDAK PERNAH menghitung volume/biaya. Lapisan ini hanya
untuk klasifikasi, narasi, retrieval bersitasi, dan ekstraksi terstruktur.
"""
