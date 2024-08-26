import os
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path):
    """Извлекает текст из PDF файла."""
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


def remove_duplicate_pdfs_by_content(folder_path):
    """Удаляет PDF файлы с одинаковым текстовым содержимым в указанной папке."""
    files = os.listdir(folder_path)
    seen_texts = {}

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith('.pdf'):
            try:
                text = extract_text_from_pdf(file_path)
                if text in seen_texts:
                    print(f"Удаление дубликата: {file_path}")
                    os.remove(file_path)
                else:
                    seen_texts[text] = file_path
            except Exception as e:
                print(f"Не удалось обработать файл {file_path}: {e}")


if __name__ == '__main__':

    folder_path = 'C:/Users/EBPO/Documents/emails/Vanderbilt.world/legal@unionpacificcapital.com'
    remove_duplicate_pdfs_by_content(folder_path)
