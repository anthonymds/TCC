import json
import os


def load_masks(mask_file):
    """
    Carrega as máscaras salvas no arquivo JSON.
    Retorna uma lista vazia se o arquivo não existir
    ou estiver inválido.
    """
    if not os.path.exists(mask_file):
        return []

    try:
        with open(mask_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_masks(rectangles, width, height, mask_file):
    """
    Salva os retângulos desenhados pelo usuário em formato proporcional,
    para funcionar em diferentes resoluções.

    rectangles: lista de tuplas (x1, y1, x2, y2)
    width, height: dimensões da imagem usada no editor
    """
    normalized_masks = []

    for x1, y1, x2, y2 in rectangles:
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])

        normalized_masks.append(
            {
                "x1": x_min / width,
                "y1": y_min / height,
                "x2": x_max / width,
                "y2": y_max / height,
            }
        )

    with open(mask_file, "w", encoding="utf-8") as f:
        json.dump(normalized_masks, f, indent=4, ensure_ascii=False)


def apply_masks(frame, masks):
    """
    Aplica as máscaras sobre a imagem, pintando as regiões de branco.
    As máscaras são esperadas em formato proporcional:
    {
        "x1": 0.0,
        "y1": 0.0,
        "x2": 1.0,
        "y2": 1.0
    }
    """
    if frame is None:
        return frame

    height, width = frame.shape[:2]

    for mask in masks:
        try:
            x1 = int(mask["x1"] * width)
            y1 = int(mask["y1"] * height)
            x2 = int(mask["x2"] * width)
            y2 = int(mask["y2"] * height)

            x_min, x_max = sorted([x1, x2])
            y_min, y_max = sorted([y1, y2])

            frame[y_min:y_max, x_min:x_max] = 255
        except (KeyError, TypeError, ValueError):
            continue

    return frame
