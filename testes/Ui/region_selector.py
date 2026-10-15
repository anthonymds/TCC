import cv2
from pynput import keyboard

from Config.settings import CAPTURE_REGION_FILE
from Core.capture import capture_screen
from Core.region import save_capture_region

drawing = False
start_point = None
current_point = None
selected_region = None


def draw_overlay(base_img, temp_region=None, final_region=None):
    img = base_img.copy()
    overlay = img.copy()

    region_to_draw = final_region if final_region else temp_region

    if region_to_draw:
        x1, y1, x2, y2 = region_to_draw
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])

        cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2)

        width = x_max - x_min
        height = y_max - y_min
        info_text = f"x={x_min}, y={y_min}, w={width}, h={height}"

        cv2.putText(
            img,
            info_text,
            (x_min, max(25, y_min - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    alpha = 0.20
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    instructions = [
        "Arraste o mouse para definir a area de captura",
        "S = salvar | C = limpar | ESC = sair sem salvar",
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
    global drawing, start_point, current_point, selected_region

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
            selected_region = (x1, y1, x2, y2)

        start_point = None
        current_point = None


def _matches_trigger(key, trigger_key):
    trigger_key = trigger_key.strip().lower()

    function_key = getattr(keyboard.Key, trigger_key, None)
    if function_key is not None and key == function_key:
        return True

    try:
        return hasattr(key, "char") and key.char and key.char.lower() == trigger_key
    except AttributeError:
        return False


def wait_for_capture_trigger(trigger_key):
    print(f"Abra a tela desejada e pressione {trigger_key.upper()} para capturar.")

    trigger_pressed = {"value": False}

    def on_press(key):
        if _matches_trigger(key, trigger_key):
            trigger_pressed["value"] = True
            return False

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    return trigger_pressed["value"]


def configure_capture_region(trigger_key="f8"):
    global drawing, start_point, current_point, selected_region

    pressed = wait_for_capture_trigger(trigger_key)
    if not pressed:
        print("Captura cancelada.")
        return None

    base_img = capture_screen()

    drawing = False
    start_point = None
    current_point = None
    selected_region = None

    window_name = "Configurar Area de Captura"

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    saved_region = None

    while True:
        temp_region = None
        if drawing and start_point and current_point:
            temp_region = (*start_point, *current_point)

        display = draw_overlay(
            base_img, temp_region=temp_region, final_region=selected_region
        )

        cv2.imshow(window_name, display)
        key = cv2.waitKey(20) & 0xFF

        if key == ord("s"):
            if selected_region:
                x1, y1, x2, y2 = selected_region
                x_min, x_max = sorted([x1, x2])
                y_min, y_max = sorted([y1, y2])

                width = x_max - x_min
                height = y_max - y_min

                save_capture_region(
                    x=x_min,
                    y=y_min,
                    width=width,
                    height=height,
                    region_file=CAPTURE_REGION_FILE,
                )

                saved_region = (x_min, y_min, width, height)
                print(f"Area de captura salva em {CAPTURE_REGION_FILE}")
                print(f"x={x_min}, y={y_min}, width={width}, height={height}")
                break
            else:
                print("Nenhuma area foi selecionada.")

        elif key == ord("c"):
            selected_region = None

        elif key == 27:
            print("Saindo sem salvar.")
            break

    cv2.destroyAllWindows()
    return saved_region
