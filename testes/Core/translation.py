from googletrans import Translator

translator = Translator()


def translate_text(text, target_language="pt", force_english_bridge=False):
    text = text.strip()
    if not text:
        return ""

    try:
        if force_english_bridge:
            temp = translator.translate(text, dest="en").text
            return translator.translate(temp, dest=target_language).text

        return translator.translate(text, dest=target_language).text

    except Exception:
        try:
            temp = translator.translate(text, dest="en").text
            return translator.translate(temp, dest=target_language).text
        except Exception as e:
            print(f"Erro ao traduzir texto '{text}': {e}")
            return text


def translate_text_list(text_list, target_language="pt", force_english_bridge=False):
    full_text = " ".join(t.strip() for t in text_list if t and t.strip()).strip()

    if not full_text:
        return ""

    return translate_text(
        full_text,
        target_language=target_language,
        force_english_bridge=force_english_bridge,
    )
