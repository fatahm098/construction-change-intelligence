import re
import cv2
import easyocr

_reader_instance = None


def get_ocr_reader():
    """Singleton EasyOCR reader pada CPU untuk menghindari inisialisasi berulang."""
    global _reader_instance
    if _reader_instance is None:
        _reader_instance = easyocr.Reader(["en"], gpu=False)
    return _reader_instance


def extract_text_and_dimensions(crop_img):
    """
    Mengekstrak teks dan mendeteksi pola dimensi geometris (mm).
    Returns: (raw_text, (width_mm, height_mm) atau None)
    """
    if crop_img is None or crop_img.size == 0:
        return "", None

    reader = get_ocr_reader()

    # Preprocessing kontras sederhana
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY) if len(crop_img.shape) == 3 else crop_img
    norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    results = reader.readtext(norm)
    raw_text = " ".join([text for _, text, _ in results]).strip()

    # Regex toleran untuk dimensi teknis: "300x300", "400*400", "300 x 300"
    matches = re.findall(r"(\d{2,4})\s*[*xX×~]\s*(\d{2,4})", raw_text)

    # Fallback jika karakter 'x' terbaca angka noise: e.g. '3007300'
    if not matches:
        noise_split = re.findall(r"(\d{3})\d(\d{3})", raw_text)
        if noise_split:
            matches = noise_split

    dimensions = None
    if matches:
        try:
            w_mm = int(matches[0][0])
            h_mm = int(matches[0][1])
            # Sanity boundary check konstruksi wajar (100 - 2000 mm)
            if 100 <= w_mm <= 2000 and 100 <= h_mm <= 2000:
                dimensions = (w_mm, h_mm)
        except ValueError:
            pass

    return raw_text, dimensions
