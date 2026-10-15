import time
import queue

from Config.settings import (
    CAPTURE_INTERVAL,
    CONFIDENCE_THRESHOLD,
    TARGET_LANGUAGE,
    DEBUG_SAVE_SCREENSHOT,
    SAVE_ONLY_WHEN_TEXT_CHANGES,
)

from Core.capture import capture_screen
from Core.preprocessing import preprocess_image
from Core.ocr import get_reader, extract_text
from Core.translation import translate_text_list
from Core.utils import get_timestamp, save_debug_image


def translation_worker(shared_state, state_lock, output_queue, stop_event):
    last_extracted_text = ""

    while not stop_event.is_set():
        try:
            with state_lock:
                paused = shared_state["paused"]
                capture_region = shared_state["capture_region"]
                force_refresh = shared_state["force_refresh"]
                ocr_profile = shared_state["ocr_profile"]
                force_english_bridge = shared_state["force_english_bridge"]

                if force_refresh:
                    shared_state["force_refresh"] = False

            if force_refresh:
                last_extracted_text = ""

            if paused:
                time.sleep(0.15)
                continue

            reader = get_reader(ocr_profile)

            frame = capture_screen(region=capture_region)
            processed_img = preprocess_image(frame)

            detected_texts, full_text = extract_text(
                reader, processed_img, confidence_threshold=CONFIDENCE_THRESHOLD
            )

            if not full_text.strip():
                if DEBUG_SAVE_SCREENSHOT and not SAVE_ONLY_WHEN_TEXT_CHANGES:
                    timestamp = get_timestamp()
                    save_debug_image(frame, "capture", timestamp)
                    save_debug_image(processed_img, "processed", timestamp)

                time.sleep(CAPTURE_INTERVAL)
                continue

            if full_text == last_extracted_text:
                if DEBUG_SAVE_SCREENSHOT and not SAVE_ONLY_WHEN_TEXT_CHANGES:
                    timestamp = get_timestamp()
                    save_debug_image(frame, "capture", timestamp)
                    save_debug_image(processed_img, "processed", timestamp)

                time.sleep(CAPTURE_INTERVAL)
                continue

            translated_text = translate_text_list(
                detected_texts,
                target_language=TARGET_LANGUAGE,
                force_english_bridge=force_english_bridge,
            )

            if DEBUG_SAVE_SCREENSHOT:
                timestamp = get_timestamp()
                save_debug_image(frame, "capture", timestamp)
                save_debug_image(processed_img, "processed", timestamp)

            payload = {"detected_text": full_text, "translated_text": translated_text}

            try:
                while True:
                    output_queue.get_nowait()
            except queue.Empty:
                pass

            output_queue.put(payload)

            last_extracted_text = full_text
            time.sleep(CAPTURE_INTERVAL)

        except Exception as e:
            output_queue.put(
                {"detected_text": "", "translated_text": f"Erro no processamento: {e}"}
            )
            time.sleep(CAPTURE_INTERVAL)
