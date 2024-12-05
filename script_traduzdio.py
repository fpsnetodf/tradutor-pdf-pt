import fitz  # PyMuPDF
import os
from googletrans import Translator
from PyPDF2 import PdfMerger

# Caminho dos arquivos
input_file = "original.pdf"
output_file = "traduzido.pdf"
temp_folder = "temp_pages"  # Pasta temporária para salvar as páginas traduzidas

# Função para criar arquivos PDF temporários com as páginas traduzidas
def criar_pagina_pdf(temp_pdf_path, translated_text, page_rect):
    # Criar um novo documento PDF para salvar a página traduzida
    translated_doc = fitz.open()
    new_page = translated_doc.new_page(width=page_rect.width, height=page_rect.height)

    # Adicionar o texto traduzido na nova página
    text_rect = fitz.Rect(50, 50, page_rect.width - 50, page_rect.height - 50)
    new_page.insert_textbox(text_rect, translated_text, fontsize=10, color=(0, 0, 0))

    # Salvar o PDF temporário
    translated_doc.save(temp_pdf_path)
    translated_doc.close()

# Função principal para traduzir o PDF
def traduzir_pdf(input_path, output_path):
    # Criar a pasta temporária para salvar as páginas traduzidas
    os.makedirs(temp_folder, exist_ok=True)
    
    doc = fitz.open(input_path)  # Abrir o PDF original
    translator = Translator()
    pdf_merger = PdfMerger()  # Usar PdfMerger para combinar PDFs temporários

    print("Iniciando a tradução...")

    # Processar cada página
    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text("text")  # Extrair texto da página

        # Traduzir o texto extraído
        try:
            translated_text = translator.translate(text, src="en", dest="pt").text
        except Exception as e:
            print(f"Erro ao traduzir a página {page_number + 1}: {e}")
            translated_text = "Erro ao traduzir esta página."

        # Caminho para o arquivo PDF temporário
        temp_pdf_path = os.path.join(temp_folder, f"pagina_{page_number + 1}.pdf")
        
        # Criar o PDF temporário com a página traduzida
        criar_pagina_pdf(temp_pdf_path, translated_text, page.rect)
        
        # Adicionar o PDF temporário ao merger
        pdf_merger.append(temp_pdf_path)
        print(f"Página {page_number + 1} traduzida e salva como PDF temporário!")

    # Salvar o PDF final com as páginas traduzidas
    pdf_merger.write(output_path)
    pdf_merger.close()

    # Remover arquivos temporários
    # for temp_file in os.listdir(temp_folder):
    #     os.remove(os.path.join(temp_folder, temp_file))
    # os.rmdir(temp_folder)

    print(f"Tradução concluída! PDF final salvo em: {output_path}")

# Executar a função
traduzir_pdf(input_file, output_file)
