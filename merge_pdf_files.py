import os
from PyPDF2 import PdfMerger


def merge_pdfs(folder_path, output_path):
    """Объединяет все PDF-файлы в указанной папке в один PDF-документ."""
    merger = PdfMerger()

    # Получаем список всех PDF файлов в папке
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        try:
            # Добавляем каждый PDF файл в объединенный документ
            merger.append(pdf_path)
        except Exception as e:
            print(f"Не удалось обработать файл {pdf_path}: {e}")

    # Сохраняем объединенный PDF
    merger.write(output_path)
    merger.close()


if __name__ == '__main__':

    # Укажите путь к папке с PDF файлами
    folder_path = 'C:/Users/EBPO/Documents/emails/Vanderbilt.world/legal@unionpacificcapital.com'
    # Укажите путь и имя выходного файла
    output_path = 'C:/Users/EBPO/Documents/emails/Vanderbilt.world/legal@unionpacificcapital.com/legal_unionpacificcapital_com.pdf'

    merge_pdfs(folder_path, output_path)
