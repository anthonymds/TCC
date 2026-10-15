import pyautogui
import cv2
import numpy as np


def capture_screen(region=None):
    """
    Captura a tela inteira ou apenas uma região específica.
    region deve ser uma tupla no formato:
    (x, y, width, height)
    """
    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()

    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame
