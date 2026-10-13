"""Pipeline RAG (Retrieval-Augmented Generation).

Alur: dokumen → chunk → embed → store → retrieve → konteks untuk LLM.

`store.py` saat ini in-memory (untuk dev). Interface-nya disiapkan agar bisa
diganti pgvector tanpa mengubah retriever/service.
"""
