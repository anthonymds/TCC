import cv2

from Config.settings import MASK_FILE
from Core.capture import capture_screen
from Core.masking import save_masks

drawing = False
start_point = None
current_point = None
rectangles = []


def draw_overlay(base_img, saved_rectangles, temp_rectangle=None):
    """
    Desenha os retângulos já criados e o retângulo temporário na tela.
    """
    img = base_img.copy()
    overlay = img.copy()

    # Retângulos salvos
    for x1, y1, x2, y2 in saved_rectangles:
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])

        cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (0, 0, 255), -1)
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

    # Retângulo sendo desenhado
    if temp_rectangle:
        x1, y1, x2, y2 = temp_rectangle
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])

        cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2)

    alpha = 0.25
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    instructions = [
        "Arraste o mouse para criar mascaras",
        "S = salvar | Z = desfazer | C = limpar | ESC = sair",
    ]

    y = 30
    for text in instructions:
        cv2.putText(
            img,
            text,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        y += 30

    return img


def mouse_callback(event, x, y, flags, param):
    """
    Callback do mouse para desenhar retângulos.
    """
    global drawing, start_point, current_point, rectangles

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        current_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        current_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)

        x1, y1 = start_point
        x2, y2 = end_point

        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
            rectangles.append((x1, y1, x2, y2))

        start_point = None
        current_point = None


def configure_masks():
    """
    Abre a interface visual para configuração das máscaras.
    """
    global rectangles, drawing, start_point, current_point

    base_img = capture_screen()
    height, width = base_img.shape[:2]

    rectangles = []
    drawing = False
    start_point = None
    current_point = None

    window_name = "Configurar Regioes Ignoradas"

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        temp_rectangle = None
        if drawing and start_point and current_point:
            temp_rectangle = (*start_point, *current_point)

        display = draw_overlay(base_img, rectangles, temp_rectangle)
        cv2.imshow(window_name, display)

        key = cv2.waitKey(20) & 0xFF

        if key == ord("s"):
            save_masks(rectangles, width, height, MASK_FILE)
            print(f"Mascaras salvas em {MASK_FILE}")
            break

        elif key == ord("z"):
            if rectangles:
                rectangles.pop()

        elif key == ord("c"):
            rectangles.clear()

        elif key == 27:  # ESC
            print("Saindo sem salvar.")
            break

    cv2.destroyAllWindows()
