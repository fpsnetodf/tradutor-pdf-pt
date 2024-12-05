import fitz  # PyMuPDF
from googletrans import Translator

# Caminho do arquivo PDF de entrada e saída
input_file = "original.pdf"
output_file = "traduzido.pdf"

def traduzir_pdf(input_path, output_path):
    translator = Translator()
    doc = fitz.open(input_path)  # Abrir o PDF original
    translated_doc = fitz.open()  # Criar um novo PDF para salvar o resultado

    print("Iniciando a tradução...")

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text("text")  # Extrair texto da página

        # Tradução do texto
        try:
            translated_text = translator.translate(text, src="en", dest="pt").text
        except Exception as e:
            print(f"Erro ao traduzir a página {page_number + 1}: {e}")
            translated_text = "Erro ao traduzir esta página."

        # Criar uma nova página com as mesmas dimensões da original
        new_page = translated_doc.new_page(width=page.rect.width, height=page.rect.height)

        # Reinserir imagens e gráficos (se existirem)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n >= 4:  # CMYK ou com canal alfa
                pix = fitz.Pixmap(fitz.csRGB, pix)
            new_page.insert_image(page.rect, pixmap=pix)

        # Adicionar o texto traduzido à nova página
        text_rect = fitz.Rect(50, 50, page.rect.width - 50, page.rect.height - 50)
        new_page.insert_textbox(text_rect, translated_text, fontsize=10, color=(0, 0, 0))

        print(f"Página {page_number + 1} processada com sucesso!")

    # Salvar o PDF traduzido
    translated_doc.save(output_path)
    translated_doc.close()
    doc.close()

    print(f"Tradução concluída! PDF salvo em: {output_path}")

# Executar a função
traduzir_pdf(input_file, output_file)
