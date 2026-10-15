CAPTURE_INTERVAL = 10
MIN_SIZE = 800
CONFIDENCE_THRESHOLD = 0.35

TARGET_LANGUAGE = "pt"
MASK_FILE = "mask_config.json"

SCREENSHOT_DIR = "data/screenshots"
LOG_DIR = "data/logs"

# adicionar mais linguagens
OCR_LANGUAGE_PROFILES = {
    "ingles": ["en", "pt"],
    "espanhol": ["es", "pt"],
    "italiano": ["it", "pt"],
    "chines simp": ["ch_sim", "en"],
    "coreano": ["ko", "en"],
    "filipino": ["tl", "en"],
    "tailandes": ["th", "en"],
    "russo": ["ru", "en"],
    "japones": ["ja", "en"],
    "alemao": ["de", "en"],
    "frances": ["fr", "en"],
    "latim": ["la", "pt"],
}
DEFAULT_OCR_PROFILE = "ingles"

DEBUG_SAVE_SCREENSHOT = True
SHOW_TRANSLATION_POPUP = True
SAVE_ONLY_WHEN_TEXT_CHANGES = True

CAPTURE_REGION_FILE = "capture_region.json"
CAPTURE_TRIGGER_KEY = "f8"
