# Tradutor de Tela em Tempo Real

Aplicação em Python para captura de uma região da tela, extração de texto com OCR e tradução automática para português em tempo  .

## Visão Geral

O projeto foi desenvolvido como protótipo funcional para um Trabalho de Conclusão de Curso, com foco em:

- captura periódica de tela
- reconhecimento óptico de caracteres (OCR)
- tradução automática
- exibição do resultado em uma janela popup

A aplicação permite configurar visualmente a área de captura e alterar parâmetros importantes durante a execução, sem necessidade de reiniciar o programa.

## Funcionalidades

- captura contínua da tela em intervalos configuráveis
- seleção visual da área de captura
- reconfiguração da área sem reiniciar a aplicação
- popup de tradução sempre visível
- processamento em thread separada para manter a interface responsiva
- pré-processamento de imagem para melhorar o OCR
- perfis de OCR por grupo de idiomas
- opção de tradução intermediária via inglês
- prevenção de retradução quando o conteúdo não muda
- suporte a salvamento de imagens de depuração

## Estrutura do Projeto

```text
tradutor_tela_tcc/
│
├── main.py
├── requirements.txt
├── README.md
├── capture_region.json
│
├── core/
│   ├── __init__.py
│   ├── capture.py
│   ├── preprocessing.py
│   ├── ocr.py
│   ├── translation.py
│   ├── region.py
│   ├── worker.py
│   └── utils.py
│
├── ui/
│   ├── __init__.py
│   ├── region_selector.py
│   └── translation_popup.py
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── data/
│   ├── screenshots/
│   └── logs/
│
└── tests/
    └── test_masking.py


##Instalação 
pip install -r requirements.txt

##Execução
python main.py

##Observações Técnicas
- O sistema opera em tempo real
- A qualidade da tradução depende diretamente da qualidade do OCR
- Fontes pequenas, baixo contraste e ruído visual podem prejudicar os resultados
- Ampliar a área de captura ou melhorar o enquadramento pode aumentar a precisão
- O uso de perfis de OCR evita incompatibilidades entre idiomas no EasyOCR

##Limitações Atuais
- A qualidade do OCR varia conforme o idioma e a qualidade visual da tela
- A tradução automática pode apresentar inconsistências em frases complexas
- Alguns idiomas exigem perfis separados por limitação da biblioteca OCR
- A precisão final depende do texto reconhecido corretamente

##Tecnologias
- Python
- OpenCV
- EasyOCR
- PyAutoGUI
- Pillow
- NumPy
- Tkinter
- googletrans
- pynput
