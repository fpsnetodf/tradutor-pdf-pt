
import fitz  # PyMuPDF
import os

# Caminhos dos arquivos
input_file = "original.pdf"
output_file = "traduzido_13.pdf"
temp_folder = "temp_pages"


from 13_copilot import combinar_pdfs




combinar_pdfs(input_file, temp_folder, output_file)