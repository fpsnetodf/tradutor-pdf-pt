import fitz  # PyMuPDF
import os
from googletrans import Translator
from PyPDF2 import PdfMerger

# Caminho dos arquivos
input_file = "original.pdf"
translated_file = "traduzido.pdf"
output_file = "8_final_com_imagens.pdf"
temp_folder = "temp_pages"  # Pasta temporária para salvar as páginas processadas

# import fitz  # PyMuPDF
# import os
# from googletrans import Translator
# from PyPDF2 import PdfMerger

# # Caminho dos arquivos
# input_file = "caminho/para/o/arquivo/original.pdf"
# translated_file = "caminho/para/o/arquivo/traduzido.pdf"
# output_file = "caminho/para/o/arquivo/final_com_imagens.pdf"
# temp_folder = "temp_pages"  # Pasta temporária para salvar as páginas processadas

# Função para inserir as imagens no PDF (sem alteração)
def inserir_imagens(temp_pdf_path, image_list, page_rect, translated_text, doc, links):
    # Criar um novo documento PDF para salvar a página final
    translated_doc = fitz.open()
    new_page = translated_doc.new_page(width=page_rect.width, height=page_rect.height)

    # Adicionar as imagens da página original ao novo PDF (sem alteração de proporção ou posição)
    for img_index, img in enumerate(image_list):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)  # Passar o doc aqui para que o PyMuPDF consiga carregar a imagem
        new_page.insert_image(page_rect, pixmap=pix)  # Inserir a imagem no PDF

    # Adicionar o texto traduzido na nova página, preservando formatação original
    text_rect = fitz.Rect(50, 50, page_rect.width - 50, page_rect.height - 50)
    new_page.insert_textbox(text_rect, translated_text, fontsize=10, color=(0, 0, 0))

    # Inserir os links da página original no novo PDF
    for link in links:
        link_rect = link.get("from")  # Posição do link na página

        if link.get("uri"):
            # Para links externos (URLs)
            new_page.insert_link({
                "uri": link["uri"],
                "from": link_rect
            })
        elif link.get("kind") == fitz.LINK_GOTO and "to" in link:
            # Para links internos (navegação entre páginas)
            page_number = link.get("to")  # Destino do link
            if page_number is not None:
                new_page.insert_link({
                    "kind": fitz.LINK_GOTO,
                    "from": link_rect,
                    "to": page_number
                })
        else:
            # Log para links problemáticos
            print(f"Link ignorado: {link}")

    # Salvar o PDF temporário
    translated_doc.save(temp_pdf_path)
    translated_doc.close()

# Função principal para combinar o PDF traduzido com as imagens do PDF original
def combinar_com_imagens(input_path, translated_path, output_path):
    # Criar a pasta temporária para salvar as páginas processadas
    os.makedirs(temp_folder, exist_ok=True)
    
    doc = fitz.open(input_path)  # Abrir o PDF original (com imagens)
    translated_doc = fitz.open(translated_path)  # Abrir o PDF já traduzido
    pdf_merger = PdfMerger()  # Usar PdfMerger para combinar PDFs temporários

    print("Iniciando a combinação do texto traduzido com as imagens...")

    # Processar cada página
    for page_number in range(len(doc)):
        page = doc[page_number]
        translated_page = translated_doc[page_number]
        
        # Obter o texto traduzido mantendo a formatação original (incluindo cores e fontes)
        text_dict = translated_page.get_text("dict")  # Usar o formato 'dict' para preservar a formatação

        # Criar o texto traduzido com a formatação preservada
        translated_text = ""
        for block in text_dict["blocks"]:
            for line in block["lines"]:
                for span in line["spans"]:
                    color = span["color"]  # Cor do texto original
                    font = span["font"]  # Fonte do texto original
                    translated_text += span["text"]  # Concatenar os textos preservando a estrutura

        # Verificar se o texto está vazio, e se estiver, colocar um texto de fallback
        if not translated_text:
            print(f"Erro de tradução na página {page_number + 1}. Inserindo texto de fallback.")
            translated_text = "Erro ao traduzir esta página."

        # Extrair imagens e links da página original
        image_list = page.get_images(full=True)
        links = page.get_links()  # Extrair links da página

        # Caminho para o arquivo PDF temporário
        temp_pdf_path = os.path.join(temp_folder, f"pagina_{page_number + 1}.pdf")
        
        # Inserir as imagens e links no PDF traduzido e criar o PDF temporário
        inserir_imagens(temp_pdf_path, image_list, page.rect, translated_text, doc, links)
        
        # Adicionar o PDF temporário ao merger
        pdf_merger.append(temp_pdf_path)
        print(f"Página {page_number + 1} processada com sucesso!")

    # Salvar o PDF final com as páginas traduzidas e imagens
    pdf_merger.write(output_path)
    pdf_merger.close()

    # Deixar a pasta temporária para que não seja apagada
    print(f"Combinação concluída! PDF final salvo em: {output_path}")
    print(f"A pasta temporária foi mantida em: {temp_folder}")

# Executar a função
combinar_com_imagens(input_file, translated_file, output_file)
