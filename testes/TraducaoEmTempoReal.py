import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import easyocr
from googletrans import Translator
from langdetect import detect
import time

# Inicializa EasyOCR
# chines simplificado no EasyOCR ch_sim
reader = easyocr.Reader(["ch_sim", "en"])

# Inicializa o tradutor
translator = Translator()


# Função para verificar se o idioma é complexo
def is_complex_language(lang_code):
    complex_languages = ["zh-cn", "ja", "ko", "ar"]
    return lang_code in complex_languages


# Tamanho mínimo da captura
min_size = 800

print("Iniciando captura da tela... Pressione Ctrl+C para sair.")

try:
    while True:
        # Captura a tela (em memória, sem salvar)
        screenshot = pyautogui.screenshot()

        # Converte para numpy array (OpenCV)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Redimensiona se necessário
        height, width = frame.shape[:2]
        if width < min_size or height < min_size:
            if width < height:
                new_width = min_size
                new_height = int((new_width / width) * height)
            else:
                new_height = min_size
                new_width = int((new_height / height) * width)
            frame = cv2.resize(frame, (new_width, new_height))

        # --- BLOQUEAR REGIÕES INDESEJADAS ---
        # Footer: y=1079 até 1032
        frame[1032:1079, :] = 255  # branco
        # Header: y=0 até 106
        frame[0:106, :] = 255
        # Lateral esquerda: x=0 até 525
        frame[:, 0:525] = 255
        # Lateral direita: x=1374 até 1919
        frame[:, 1374:1919] = 255

        # Escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Binarização
        _, bw = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

        # Ajuste de contraste
        pil_image = Image.fromarray(bw)
        enhancer = ImageEnhance.Contrast(pil_image)
        processed_img = enhancer.enhance(1.2)
        processed_img = np.array(processed_img)

        # OCR
        results = reader.readtext(processed_img)

        # laco passando pelo texto e traduzindo por partes por conta
        # de bugs na hr de traducao de textos longos
        extracted_text = " ".join([res[1] for res in results])

        if results:

            # Lista para armazenar cada trecho traduzido
            translated_parts = []

            # Detecta idioma
            for res in results:
                text_part = res[1].strip()
                if text_part == "":
                    continue
                try:
                    detected_language = detect(text_part)

                    # Tradução por partes
                    if is_complex_language(detected_language):
                        temp = translator.translate(
                            text_part, src=detected_language, dest="en"
                        ).text
                        # linha para debug
                        # print("Texto em ingles:" + temp)
                        translated_text = translator.translate(
                            temp, src="en", dest="pt"
                        ).text
                    else:
                        translated_text = translator.translate(
                            text_part, src=detected_language, dest="pt"
                        ).text

                    translated_parts.append(translated_text)
                except Exception as e:
                    print(f"Erro ao traduzir trecho '{text_part}': {e}")
                    translated_parts.append(text_part)  # mantém original se erro

            # Junta todas as partes traduzidas
            full_translated_text = " ".join(translated_parts)

            # Junta todas as partes extraídas para referência
            extracted_text = " ".join([res[1] for res in results])

            print("Texto Detectado:", extracted_text)
            print("Traduzido:", full_translated_text)
            print("---------------------------------------------------")

        # Sleep para dar tempo do OCR processar e não sobrecarregar a CPU
        time.sleep(2)  # 2 segundos por captura

except KeyboardInterrupt:
    print("Captura finalizada.")
