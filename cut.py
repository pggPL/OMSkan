import os
import sys
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path

districts = ['GD', 'KA', 'KR', 'LO', 'LU', 'PO', 'RZ', 'SZ', 'TO', 'WA', 'WR', 'final']
tmp_path = './tmp_files'

# create subdir for each district if not exists
for district in districts:
    if not os.path.exists(tmp_path + '/' + district):
        os.makedirs(tmp_path + '/' + district)

if len(sys.argv) != 3:
    print('Usage: python cut.py <file_path> <district>')
    sys.exit(1)

# get file path from sysarg
file_path = sys.argv[1]
district_save = sys.argv[2]

assert district_save in districts, 'District not found'
# check if correct path
if not os.path.exists(file_path):
    print('File not found')
    sys.exit(1)

# check if pdf
if not file_path.endswith('.pdf'):
    print('File is not a pdf')
    sys.exit(1)


# Funkcja do dzielenia PDF na strony i zapisywania ich jako PDF i PNG
def split_pdf_to_pages_and_convert(file_path):
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    file_name = os.path.basename(file_path)

    for i in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        output_pdf_path = os.path.join(tmp_path, f'{district_save}/{file_name}_{(i + 1)}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf_file:
            writer.write(output_pdf_file)

        # Konwersja strony PDF na PNG
        images = convert_from_path(output_pdf_path)
        for image in images:
            output_image_path = os.path.join(tmp_path, f'{district_save}/{file_name}_{i + 1}.png')
            image.save(output_image_path, 'PNG')

split_pdf_to_pages_and_convert(file_path)

