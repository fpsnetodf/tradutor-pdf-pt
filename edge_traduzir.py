import fitz  # PyMuPDF
import os
from deep_translator import GoogleTranslator
from PIL import Image

# Caminhos dos arquivos
input_file = "original.pdf"
output_file = "traduzido.pdf"
temp_folder = "temp_pages"

# Função para traduzir e manter o layout original
def traduzir_pdf(input_file, output_file):
    # Criar pasta temporária
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    doc = fitz.open(input_file)
    translated_pages = []

    print("Iniciando a tradução...")

    for page_num, page in enumerate(doc):
        print(f"Processando a página {page_num + 1}...")

        # Extrair o texto com formatação
        text_dict = page.get_text("dict")
        if not text_dict or "blocks" not in text_dict:
            print(f"A página {page_num + 1} não possui texto. Pulando...")
            continue

        translated_text = ""
        try:
            for block in text_dict["blocks"]:
                if "lines" in block and block["lines"]:
                    for line in block["lines"]:
                        if "spans" in line and line["spans"]:
                            for span in line["spans"]:
                                original_text = span.get("text", "")
                                if original_text.strip():  # Evitar spans vazios
                                    # Traduzir o texto
                                    translated_text += GoogleTranslator(source='en', target='pt').translate(original_text) + "\n"
        except Exception as e:
            print(f"Erro ao traduzir a página {page_num + 1}: {e}")
            continue

        # Criar uma nova imagem para a página
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Salvar a imagem como PDF
        temp_file = os.path.join(temp_folder, f"pagina_{page_num + 1}.pdf")
        img.save(temp_file, "PDF")

        # Adicionar texto traduzido na imagem (opcional)
        translated_pages.append((temp_file, translated_text))
        print(f"Página {page_num + 1} traduzida com sucesso!")

    # Combinar todas as páginas traduzidas em um único PDF
    final_doc = fitz.open()
    for temp_page, text in translated_pages:
        final_doc.insert_pdf(fitz.open(temp_page))
        
    # Salvar o PDF final
    final_doc.save(output_file)
    final_doc.close()

    # Limpar arquivos temporários
    # for temp_file in os.listdir(temp_folder):
    #     os.remove(os.path.join(temp_folder, temp_file))
    # os.rmdir(temp_folder)

    print(f"Tradução concluída! PDF salvo em: {output_file}")

# Executar a função com os caminhos definidos
traduzir_pdf(input_file, output_file)
