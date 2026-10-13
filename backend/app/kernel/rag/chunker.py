"""Chunking dokumen teks.

Memecah teks panjang menjadi potongan (chunk) dengan overlap agar konteks
tidak terpotong di tengah kalimat/paragraf.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    page: int | None = None
    char_start: int = 0
    char_end: int = 0


def chunk_text(
    text: str,
    *,
    page: int | None = None,
    chunk_size: int = 1000,
    overlap: int = 150,
    start_index: int = 0,
) -> list[Chunk]:
    """Pecah satu blok teks menjadi chunk berukuran `chunk_size` karakter.

    Pemotongan diutamakan pada batas paragraf/baris terdekat agar lebih rapi.
    """
    text = text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    pos = 0
    idx = start_index
    n = len(text)

    while pos < n:
        end = min(pos + chunk_size, n)

        # Usahakan potong di batas paragraf atau baris terdekat
        if end < n:
            for sep in ("\n\n", "\n", ". "):
                cut = text.rfind(sep, pos + chunk_size // 2, end)
                if cut != -1:
                    end = cut + len(sep)
                    break

        piece = text[pos:end].strip()
        if piece:
            chunks.append(
                Chunk(
                    text=piece,
                    chunk_index=idx,
                    page=page,
                    char_start=pos,
                    char_end=end,
                )
            )
            idx += 1

        if end >= n:
            break
        pos = max(end - overlap, pos + 1)

    return chunks


def chunk_pages(pages: list[tuple[int, str]], **kwargs) -> list[Chunk]:
    """Chunk banyak halaman sekaligus, dengan nomor halaman terlacak.

    `pages`: daftar (nomor_halaman, teks_halaman).
    """
    all_chunks: list[Chunk] = []
    idx = 0
    for page_no, page_text in pages:
        page_chunks = chunk_text(page_text, page=page_no, start_index=idx, **kwargs)
        all_chunks.extend(page_chunks)
        idx += len(page_chunks)
    return all_chunks
