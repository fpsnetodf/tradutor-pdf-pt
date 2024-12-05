import fitz  # PyMuPDF
import os

# Caminhos dos arquivos
input_file = "original.pdf"
output_file = "traduzido_13.pdf"
temp_folder = "temp_pages"

# Função para combinar as páginas traduzidas e adicionar as imagens do arquivo original
def combinar_pdfs(input_path, temp_folder, output_path):
    final_doc = fitz.open()

    # Adicionar as páginas traduzidas
    for temp_file in sorted(os.listdir(temp_folder)):
        if temp_file.endswith(".pdf"):
            temp_path = os.path.join(temp_folder, temp_file)
            temp_doc = fitz.open(temp_path)
            final_doc.insert_pdf(temp_doc)

    # Adicionar as imagens do arquivo original
    original_doc = fitz.open(input_path)
    for page_num, page in enumerate(original_doc):
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(original_doc, xref)
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
            final_doc[page_num].insert_image(img_rect, pixmap=pix)

    # Salvar o PDF final
    final_doc.save(output_path)
    final_doc.close()

    print(f"PDF final salvo em: {output_path}")

# Combinar as páginas traduzidas e adicionar as imagens do arquivo original
combinar_pdfs(input_file, temp_folder, output_file)
