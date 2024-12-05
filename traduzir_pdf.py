import fitz  # PyMuPDF
import os
from googletrans import Translator

# Caminhos dos arquivos
input_file = "original.pdf"
output_file = "traduzido.pdf"
temp_folder = "temp_pages"

# Função para traduzir e manter o layout original
def traduzir_pdf(input_path, output_path):
    # Criar pasta temporária
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    doc = fitz.open(input_path)
    translator = Translator()
    translated_pages = []

    print("Iniciando a tradução...")

    for page_num, page in enumerate(doc):
        print(f"Processando a página {page_num + 1}...")

        # Extrair o texto com formatação
        text_dict = page.get_text("dict")
        if not text_dict or "blocks" not in text_dict:
            print(f"A página {page_num + 1} não possui texto. Pulando...")
            continue

        text_blocks = text_dict["blocks"]
        translated_blocks = []

        try:
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            original_text = span.get("text", "")
                            bbox = span.get("bbox")  # Verificar coordenadas
                            if not bbox or len(bbox) != 4:
                                continue  # Ignorar spans sem coordenadas válidas

                            if original_text.strip():  # Evitar spans vazios
                                # Traduzir o texto
                                translated_text = translator.translate(original_text, src="en", dest="pt").text
                                span["text"] = translated_text  # Substituir o texto traduzido
                                translated_blocks.append({"text": translated_text, "bbox": bbox, "font": span.get("font"), "size": span.get("size"), "color": span.get("color")})
        except Exception as e:
            print(f"Erro ao traduzir a página {page_num + 1}: {e}")
            continue

        # Criar uma nova página com as mesmas dimensões da original
        translated_doc = fitz.open()
        new_page = translated_doc.new_page(width=page.rect.width, height=page.rect.height)

        # Adicionar os blocos de texto traduzidos
        for block in translated_blocks:
            bbox = block["bbox"]
            if len(bbox) == 4:  # Garantir que as coordenadas são válidas
                rect = fitz.Rect(bbox)
                font = block.get("font", "Helvetica")
                size = block.get("size", 10)
                color = block.get("color", 0)  # Preto padrão
                new_page.insert_text(rect, block["text"], fontsize=size, fontname=font, color=color)

        # Adicionar as imagens da página original mantendo a proporção
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n >= 4:  # CMYK ou com canal alfa
                pix = fitz.Pixmap(fitz.csRGB, pix)

            # Calcular proporção da imagem
            img_width, img_height = pix.width, pix.height
            page_width, page_height = page.rect.width, page.rect.height
            aspect_ratio = img_width / img_height

            # Ajustar a largura e altura proporcionalmente
            if img_width > page_width or img_height > page_height:
                if img_width > img_height:  # Largura maior, ajustar por largura
                    scale_factor = page_width / img_width
                else:  # Altura maior, ajustar por altura
                    scale_factor = page_height / img_height
                img_width *= scale_factor
                img_height *= scale_factor

            # Inserir a imagem centralizada
            img_rect = fitz.Rect(
                (page_width - img_width) / 2,
                (page_height - img_height) / 2,
                (page_width + img_width) / 2,
                (page_height + img_height) / 2,
            )
            new_page.insert_image(img_rect, pixmap=pix)

        # Salvar a página temporária
        temp_file = os.path.join(temp_folder, f"pagina_{page_num + 1}.pdf")
        translated_doc.save(temp_file)
        translated_pages.append(temp_file)
        print(f"Página {page_num + 1} traduzida com sucesso!")

    # Combinar todas as páginas traduzidas em um único PDF
    final_doc = fitz.open()
    for temp_page in translated_pages:
        final_doc.insert_pdf(fitz.open(temp_page))

    # Salvar o PDF final
    final_doc.save(output_path)
    final_doc.close()

    # Limpar arquivos temporários
    # for temp_file in translated_pages:
    #     os.remove(temp_file)
    # os.rmdir(temp_folder)

    print(f"Tradução concluída! PDF salvo em: {output_path}")

# Executar a função com os caminhos definidos
traduzir_pdf(input_file, output_file)
