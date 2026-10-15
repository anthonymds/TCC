# import queue
# import threading

# from Config.settings import (
#     SHOW_TRANSLATION_POPUP,
#     CAPTURE_REGION_FILE,
#     CAPTURE_TRIGGER_KEY,
#     DEFAULT_OCR_PROFILE,
#     CAPTURE_INTERVAL,
# )

# from Core.region import load_capture_region
# from Core.utils import ensure_directories
# from Core.worker import translation_worker
# from Ui.translation_popup import TranslationPopup


# def main():
#     print("Iniciando sistema de tradução de tela...")

#     ensure_directories()

#     capture_region = load_capture_region(CAPTURE_REGION_FILE)

#     shared_state = {
#         "capture_region": capture_region,
#         "capture_trigger_key": CAPTURE_TRIGGER_KEY,
#         "paused": False,
#         "force_refresh": False,
#         "ocr_profile": DEFAULT_OCR_PROFILE,
#         "force_english_bridge": False,
#         "capture_interval": CAPTURE_INTERVAL,
#     }

#     state_lock = threading.Lock()
#     message_queue = queue.Queue()
#     stop_event = threading.Event()

#     worker = threading.Thread(
#         target=translation_worker,
#         args=(shared_state, state_lock, message_queue, stop_event),
#         daemon=True,
#     )
#     worker.start()

#     if SHOW_TRANSLATION_POPUP:
#         popup = TranslationPopup(
#             message_queue=message_queue,
#             stop_event=stop_event,
#             shared_state=shared_state,
#             state_lock=state_lock,
#         )
#         popup.run()
#     else:
#         stop_event.set()

#     worker.join(timeout=2)
#     print("Sistema encerrado.")


# if __name__ == "__main__":
#     main()

import queue
import threading

from Config.settings import (
    SHOW_TRANSLATION_POPUP,
    CAPTURE_REGION_FILE,
    CAPTURE_TRIGGER_KEY,
    DEFAULT_OCR_PROFILE,
    CAPTURE_INTERVAL,
)

from Core.region import load_capture_region
from Core.utils import ensure_directories
from Core.worker import translation_worker
from Ui.translation_popup import TranslationPopup


def main():
    print("Iniciando sistema de tradução de tela...")

    ensure_directories()

    capture_region = load_capture_region(CAPTURE_REGION_FILE)

    shared_state = {
        "capture_region": capture_region,
        "capture_trigger_key": CAPTURE_TRIGGER_KEY,
        "paused": False,
        "force_refresh": False,
        "ocr_profile": DEFAULT_OCR_PROFILE,
        "force_english_bridge": False,
        "capture_interval": CAPTURE_INTERVAL,
    }

    state_lock = threading.Lock()
    message_queue = queue.Queue()
    stop_event = threading.Event()

    worker = threading.Thread(
        target=translation_worker,
        args=(shared_state, state_lock, message_queue, stop_event),
        daemon=True,
    )
    worker.start()

    if SHOW_TRANSLATION_POPUP:
        popup = TranslationPopup(
            message_queue=message_queue,
            stop_event=stop_event,
            shared_state=shared_state,
            state_lock=state_lock,
        )
        popup.run()
    else:
        stop_event.set()

    worker.join(timeout=2)
    print("Sistema encerrado.")


if __name__ == "__main__":
    main()
