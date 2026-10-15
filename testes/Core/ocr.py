import easyocr

from Config.settings import OCR_LANGUAGE_PROFILES, DEFAULT_OCR_PROFILE

_reader_cache = {}


def get_reader(profile_name=None):
    """
    Retorna um reader EasyOCR com cache, baseado no perfil informado.
    """
    if profile_name is None:
        profile_name = DEFAULT_OCR_PROFILE

    if profile_name not in OCR_LANGUAGE_PROFILES:
        raise ValueError(f"Perfil OCR inválido: {profile_name}")

    if profile_name not in _reader_cache:
        lang_list = OCR_LANGUAGE_PROFILES[profile_name]
        _reader_cache[profile_name] = easyocr.Reader(lang_list, gpu=False)

    return _reader_cache[profile_name]


def extract_text(reader, processed_img, confidence_threshold=0.35):
    results = reader.readtext(
        processed_img,
        detail=0,
        paragraph=True,
        mag_ratio=3,
        decoder="beamsearch",
        beamWidth=5,
        contrast_ths=0.1,
        adjust_contrast=0.5,
    )

    detected_texts = [
        text.strip() for text in results if isinstance(text, str) and text.strip()
    ]

    full_text = " ".join(detected_texts).strip()
    return detected_texts, full_text
