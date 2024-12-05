import fitz  # PyMuPDF
import os
from PIL import Image

# Caminhos dos arquivos
input_file = "original.pdf"
output_file = "traduzido_1.pdf"
temp_folder = "temp_pages"

# Função para criar o diretório temporário
def criar_diretorio_temp(temp_folder):
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
        print(f"Diretório {temp_folder} criado com sucesso!")
    else:
        print(f"Diretório {temp_folder} já existe.")

# Função para traduzir e manter o layout original
def traduzir_pdf(input_path, temp_folder):
    doc = fitz.open(input_path)
    translated_pages = []

    print("Iniciando a tradução...")

    for page_num, page in enumerate(doc):
        print(f"Processando a página {page_num + 1}...")

        # Criar uma nova imagem para a página
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Salvar a imagem como PDF
        temp_file = os.path.join(temp_folder, f"pagina_{page_num + 1}.pdf")
        img.save(temp_file, "PDF")
        translated_pages.append(temp_file)
        print(f"Página {page_num + 1} traduzida com sucesso!")

    return translated_pages

# Função para combinar as páginas traduzidas e adicionar as imagens do arquivo original
def combinar_pdfs(input_path, translated_pages, output_path):
    final_doc = fitz.open()

    for temp_page in translated_pages:
        temp_doc = fitz.open(temp_page)
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

# Executar a função para criar o diretório temporário
criar_diretorio_temp(temp_folder)

# Executar a função para traduzir o PDF
translated_pages = traduzir_pdf(input_file, temp_folder)

# Combinar as páginas traduzidas e adicionar as imagens do arquivo original
combinar_pdfs(input_file, translated_pages, output_file)
