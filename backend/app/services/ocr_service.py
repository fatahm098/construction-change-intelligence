import re
import cv2
import easyocr

_reader_instance = None

# Dimensi dengan pemisah eksplisit: "300x300", "400*400", "300 x 300".
_CROSS_RE = re.compile(r"(\d{2,4})\s*[*xX×~]\s*(\d{2,4})")

# Dimensi yang terbaca OCR sebagai dua angka terpisah spasi, mis. "K2 400 400".
# Hanya dipakai bila didahului label elemen agar angka garis (mis. "7000") tidak ikut.
_SPACE_DIM_RE = re.compile(
    r"\b(?:KOLOM\s*K|KOLOM|K|S|B)\s*\d{0,2}\s+(\d{3,4})\s+(\d{3,4})\b",
    re.IGNORECASE,
)

# Fallback bila karakter 'x' hilang: "3007300".
_NOISE_SPLIT_RE = re.compile(r"(\d{3})\d(\d{3})")

MIN_DIM_MM = 100
MAX_DIM_MM = 2000


def get_ocr_reader():
    """Singleton EasyOCR reader pada CPU untuk menghindari inisialisasi berulang."""
    global _reader_instance
    if _reader_instance is None:
        _reader_instance = easyocr.Reader(["en"], gpu=False)
    return _reader_instance


def _is_valid_dims(dims) -> bool:
    return MIN_DIM_MM <= dims[0] <= MAX_DIM_MM and MIN_DIM_MM <= dims[1] <= MAX_DIM_MM


def _bbox_from_points(points) -> tuple[int, int, int, int]:
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    x1, y1 = int(min(xs)), int(min(ys))
    x2, y2 = int(max(xs)), int(max(ys))
    return x1, y1, x2 - x1, y2 - y1


def _line_candidates(text: str, confidence: float, bbox: tuple[int, int, int, int]) -> list[dict]:
    """Ambil semua kandidat dimensi dari satu baris OCR, urut posisi kemunculan."""
    found = []

    for m in _CROSS_RE.finditer(text):
        found.append((m.start(), m.group(0), (int(m.group(1)), int(m.group(2)))))

    for m in _SPACE_DIM_RE.finditer(text):
        found.append((m.start(), m.group(0), (int(m.group(1)), int(m.group(2)))))

    if not found:
        for m in _NOISE_SPLIT_RE.finditer(text):
            found.append((m.start(), m.group(0), (int(m.group(1)), int(m.group(2)))))

    found.sort(key=lambda item: item[0])

    candidates = []
    seen = set()
    for _, matched_text, dims in found:
        if not _is_valid_dims(dims) or dims in seen:
            continue
        seen.add(dims)
        candidates.append(
            {
                "text": matched_text.strip(),
                "dims": dims,
                "bbox": bbox,
                "confidence": float(confidence),
            }
        )
    return candidates


def extract_text_and_candidates(crop_img) -> tuple[str, list[dict]]:
    """Ekstrak seluruh teks crop beserta semua kandidat dimensi per baris OCR.

    Returns: (raw_text, list of {"text", "dims", "bbox", "confidence"})
    """
    if crop_img is None or crop_img.size == 0:
        return "", []

    reader = get_ocr_reader()

    # Preprocessing kontras sederhana
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY) if len(crop_img.shape) == 3 else crop_img
    norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    results = reader.readtext(norm)
    raw_text = " ".join([text for _, text, _ in results]).strip()

    candidates = []
    for points, text, confidence in results:
        candidates.extend(_line_candidates(text, confidence, _bbox_from_points(points)))

    return raw_text, candidates


def extract_dimension_candidates(crop_img) -> list[dict]:
    """Semua kandidat dimensi dalam crop, bukan hanya yang pertama."""
    return extract_text_and_candidates(crop_img)[1]


def extract_text_and_dimensions(crop_img):
    """
    Mengekstrak teks dan mendeteksi pola dimensi geometris (mm).
    Returns: (raw_text, (width_mm, height_mm) atau None)

    Dipertahankan untuk kompatibilitas: memakai kandidat pertama.
    """
    raw_text, candidates = extract_text_and_candidates(crop_img)
    return raw_text, (candidates[0]["dims"] if candidates else None)
