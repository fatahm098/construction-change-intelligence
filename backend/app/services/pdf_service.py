import os
import pymupdf


def rasterize_pdf_page(pdf_path: str, page_number: int = 0, dpi: int = 150, output_dir: str = None) -> tuple[str, int, int]:
    """
    Rasterize satu halaman PDF ke file PNG.
    Returns: (output_png_path, width_px, height_px)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File PDF tidak ditemukan: {pdf_path}")

    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)

    os.makedirs(output_dir, exist_ok=True)

    doc = pymupdf.open(pdf_path)
    if page_number >= len(doc):
        raise IndexError(f"Page number {page_number} melebihi jumlah halaman ({len(doc)})")

    page = doc[page_number]
    pix = page.get_pixmap(dpi=dpi)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_filename = f"{base_name}_p{page_number}_{dpi}dpi.png"
    out_path = os.path.join(output_dir, out_filename)

    pix.save(out_path)
    doc.close()

    return out_path, pix.width, pix.height
