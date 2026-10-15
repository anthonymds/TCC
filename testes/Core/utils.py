import os
import cv2
from datetime import datetime

from Config.settings import SCREENSHOT_DIR, LOG_DIR


def ensure_directories():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_debug_image(image, prefix, timestamp):
    """
    Salva uma imagem de depuração em data/screenshots.
    """
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    cv2.imwrite(filepath, image)
    return filepath
