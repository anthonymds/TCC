import numpy as np

from Core.masking import apply_masks


def test_apply_masks_should_paint_region_white():
    # imagem preta 100x100
    frame = np.zeros((100, 100, 3), dtype=np.uint8)

    masks = [{"x1": 0.10, "y1": 0.10, "x2": 0.30, "y2": 0.30}]

    result = apply_masks(frame.copy(), masks)

    # Região mascarada esperada: de 10 a 30
    masked_region = result[10:30, 10:30]

    # Toda a região deve estar branca
    assert np.all(masked_region == 255)
