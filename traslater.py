from PyPDF2 import PdfReader, PdfWriter
from googletrans import Translator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Caminhos dos arquivos
input_file = "original.pdf"
output_file = "traduzido.pdf"
temp_folder = "temp_pages"

# Função para criar um arquivo PDF temporário com o texto traduzido
def criar_pagina_pdf(texto, pagina_num):
    temp_file = os.path.join(temp_folder, f"pagina_{pagina_num}.pdf")
    c = canvas.Canvas(temp_file, pagesize=letter)
    c.drawString(50, 750, f"Página {pagina_num}")  # Título da página
    text_obj = c.beginText(50, 700)  # Início do texto
    text_obj.setFont("Helvetica", 10)

    # Dividir o texto em linhas para evitar transbordamento
    for linha in texto.split("\n"):
        if len(linha) > 100:  # Quebrar linhas muito longas
            for i in range(0, len(linha), 100):
                text_obj.textLine(linha[i:i+100])
        else:
            text_obj.textLine(linha)

    c.drawText(text_obj)
    c.showPage()
    c.save()
    return temp_file

# Função principal para traduzir o PDF
def traduzir_pdf(input_path, output_path):
    os.makedirs(temp_folder, exist_ok=True)  # Criar pasta temporária
    reader = PdfReader(input_path)
    writer = PdfWriter()
    translator = Translator()

    print("Iniciando a tradução...")
    for index, page in enumerate(reader.pages):
        # Extrair o texto da página original
        original_text = page.extract_text()
        if not original_text.strip():
            continue  # Pular páginas em branco

        try:
            # Traduzir o texto para português
            translated_text = translator.translate(original_text, src="en", dest="pt").text
        except Exception as e:
            print(f"Erro ao traduzir a página {index + 1}: {e}")
            translated_text = "Erro ao traduzir esta página."

        # Criar uma página traduzida como PDF temporário
        temp_pdf_path = criar_pagina_pdf(translated_text, index + 1)
        temp_pdf = PdfReader(temp_pdf_path)

        # Adicionar a página traduzida ao PDF final
        writer.add_page(temp_pdf.pages[0])
        print(f"Página {index + 1} traduzida com sucesso!")

    # Salvar o PDF traduzido
    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)

    # Limpar arquivos temporários
    # for temp_file in os.listdir(temp_folder):
    #     os.remove(os.path.join(temp_folder, temp_file))
    # os.rmdir(temp_folder)

    print(f"Tradução concluída! PDF salvo em: {output_path}")

# Executar a função com os caminhos definidos
traduzir_pdf(input_file, output_file)


