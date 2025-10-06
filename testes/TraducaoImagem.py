# Imports
import easyocr  # type: ignore
import cv2  # type: ignore
from googletrans import Translator
from PIL import Image, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt  # type: ignore
from langdetect import detect  # type: ignore

# Caminho da imagem
CAMINHO_IMAGEM = r"C:\Users\antho\Downloads\teste5.png"

# Carregar a imagem com OpenCV
image = cv2.imread(CAMINHO_IMAGEM)

# Converter a imagem para escala de cinza
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Binarização: converte a imagem para preto e branco
_, image_bw = cv2.threshold(image_gray, 128, 255, cv2.THRESH_BINARY)


# Ajustar o contraste da imagem (opcional)
pil_image = Image.fromarray(image_bw)  # Converte para o formato PIL
enhancer = ImageEnhance.Contrast(pil_image)
image_contrast = enhancer.enhance(1)  # Aumenta o contraste

# Salvar a imagem processada para visualização (opcional)
image_contrast.save("processed_image.jpg")

# Exibir a imagem processada com Matplotlib
plt.imshow(image_bw, cmap="gray")
plt.axis("off")  # Remover eixos
plt.show()


# Função para verificar se o idioma é mais complexo
def is_complex_language(lang_code):
    complex_languages = ["zh-cn", "ja", "ko", "ar"]  # Chinês, Japonês, Coreano, Árabe
    return lang_code in complex_languages


# ch_sim = chines
# Inicializa o EasyOCR
LINGUA_ESCOLHIDA = "ko"
reader = easyocr.Reader([LINGUA_ESCOLHIDA, "en"])

# Lê o texto da imagem processada
result = reader.readtext(
    np.array(image_contrast)
)  # Convertendo de volta para um array do OpenCV

extracted_text = ""
for detection in result:
    extracted_text += detection[1] + " "  # Concatenando os textos detectados

print("---------------------------------------------------\n")

print("Texto Extraído ():", extracted_text)
# Detecta o idioma do texto extraído
detected_language = detect(extracted_text)
print(f"Idioma Detectado: {detected_language}")

# Traduz o texto extraído para o inglês usando googletrans
translator = Translator()
if is_complex_language(detected_language):
    # Se for um idioma mais complexo (como chinês, japonês, coreano, árabe), traduza para inglês primeiro
    translated_text = translator.translate(
        extracted_text, src=detected_language, dest="en"
    ).text
    print("Texto Traduzido para o Inglês:", translated_text)
    translated_text = translator.translate(
        translated_text, src="en", dest="pt"
    ).text  # Depois para português
    print("Texto Traduzido para o Português:", translated_text)
else:
    # Se for um idioma mais simples, traduza direto para o português
    translated_text = translator.translate(
        extracted_text, src=detected_language, dest="pt"
    ).text
    print("Texto Traduzido para o Português:", translated_text)
print("---------------------------------------------------\n")

# Exibe o texto extraído
for detection in result:
    print(detection[1])  # Texto extraído

print("---------------------------------------------------\n")
