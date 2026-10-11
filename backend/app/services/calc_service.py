from ..models.entities import ElementType


def calculate_element_volumes(
    element_type: ElementType,
    dim_before_w_mm: float,
    dim_before_h_mm: float,
    dim_after_w_mm: float,
    dim_after_h_mm: float,
    height_or_length_m: float = 4.0,
) -> tuple[float, float, float]:
    """
    Kalkulasi volume deterministik m3:
    1. Kolom (Column): Vol = (w/1000) * (h/1000) * Tinggi_m
    2. Balok (Beam): Vol = (b/1000) * (h/1000) * Panjang_m
    3. Pelat (Slab): Vol = Panjang_m * Lebar_m * (tebal_mm / 1000)
    Returns: (vol_before_m3, vol_after_m3, delta_volume_m3)
    """
    if element_type in (ElementType.COLUMN, ElementType.BEAM):
        w0_m = dim_before_w_mm / 1000.0
        h0_m = dim_before_h_mm / 1000.0
        vol0 = w0_m * h0_m * height_or_length_m

        w1_m = dim_after_w_mm / 1000.0
        h1_m = dim_after_h_mm / 1000.0
        vol1 = w1_m * h1_m * height_or_length_m

    elif element_type == ElementType.SLAB:
        # Untuk pelat, dim_w dan dim_h adalah luasan lantai (m) dan tebal_m
        vol0 = (dim_before_w_mm / 1000.0) * (dim_before_h_mm / 1000.0) * height_or_length_m
        vol1 = (dim_after_w_mm / 1000.0) * (dim_after_h_mm / 1000.0) * height_or_length_m
    else:
        # Default box representation
        vol0 = (dim_before_w_mm / 1000.0) * (dim_before_h_mm / 1000.0) * height_or_length_m
        vol1 = (dim_after_w_mm / 1000.0) * (dim_after_h_mm / 1000.0) * height_or_length_m

    delta = vol1 - vol0
    return round(vol0, 4), round(vol1, 4), round(delta, 4)
