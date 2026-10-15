import cv2
import numpy as np

from Config.settings import MIN_SIZE


def resize_if_needed(frame, min_size=MIN_SIZE):
    height, width = frame.shape[:2]

    if width < min_size or height < min_size:
        if width < height:
            new_width = min_size
            new_height = int((new_width / width) * height)
        else:
            new_height = min_size
            new_width = int((new_height / height) * width)

        frame = cv2.resize(frame, (new_width, new_height))

    return frame


def preprocess_image(frame):
    frame = resize_if_needed(frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Base geral: texto escuro em fundo claro
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )

    # ---------------------------------------------------------
    # 1) Detecta regiões escuras candidatas a "balão de fala"
    # ---------------------------------------------------------
    _, dark_mask = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)

    kernel_dark = np.ones((5, 5), np.uint8)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel_dark)
    dark_mask = cv2.dilate(dark_mask, kernel_dark, iterations=1)

    contours, _ = cv2.findContours(
        dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    img_h, img_w = gray.shape[:2]
    min_area = (img_h * img_w) * 0.002

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h

        if area < min_area:
            continue
        if w < 40 or h < 25:
            continue

        roi_gray = gray[y : y + h, x : x + w]
        roi_h, roi_w = roi_gray.shape[:2]

        # Região realmente escura
        mean_intensity = float(np.mean(roi_gray))
        if mean_intensity >= 110:
            continue

        # ---------------------------------------------------------
        # 2) Detecta texto claro dentro do ROI escuro
        # ---------------------------------------------------------
        # Aqui usamos THRESH_BINARY para deixar texto claro em branco
        roi_text_mask = cv2.adaptiveThreshold(
            roi_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
        )

        # Limpeza leve
        kernel_open = np.ones((2, 2), np.uint8)
        roi_text_mask = cv2.morphologyEx(roi_text_mask, cv2.MORPH_OPEN, kernel_open)

        # ---------------------------------------------------------
        # 3) Monta um ROI novo todo branco
        # ---------------------------------------------------------
        roi_clean = np.full((roi_h, roi_w), 255, dtype=np.uint8)

        # ---------------------------------------------------------
        # 4) Mantém só componentes que parecem texto
        # ---------------------------------------------------------
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            roi_text_mask, connectivity=8
        )

        for label in range(1, num_labels):
            cx = stats[label, cv2.CC_STAT_LEFT]
            cy = stats[label, cv2.CC_STAT_TOP]
            cw = stats[label, cv2.CC_STAT_WIDTH]
            ch = stats[label, cv2.CC_STAT_HEIGHT]
            c_area = stats[label, cv2.CC_STAT_AREA]

            # ignora ruído muito pequeno
            if c_area < 12:
                continue

            # ignora componentes grandes demais
            if c_area > (roi_h * roi_w) * 0.08:
                continue

            # ignora componentes muito baixos/altos
            if ch < 4 or ch > roi_h * 0.5:
                continue

            # ignora componentes muito estreitos/largos
            if cw < 2 or cw > roi_w * 0.5:
                continue

            # remove componentes que encostam na borda do ROI
            # isso ajuda a descartar o contorno do balão
            if (
                cx <= 0
                or cy <= 0
                or (cx + cw) >= (roi_w - 1)
                or (cy + ch) >= (roi_h - 1)
            ):
                continue

            fill_ratio = c_area / float(cw * ch)
            if fill_ratio < 0.05 or fill_ratio > 0.95:
                continue

            component_mask = labels == label

            # ---------------------------------------------------------
            # 5) Desenha só o texto em preto no ROI branco
            # ---------------------------------------------------------
            roi_clean[component_mask] = 0

        # substitui completamente o ROI antigo pelo ROI limpo
        processed[y : y + h, x : x + w] = roi_clean

    # fechamento final leve
    kernel_close = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel_close)

    return processed
