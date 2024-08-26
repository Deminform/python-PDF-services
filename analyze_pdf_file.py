import os
import fitz  # PyMuPDF
import re
import hashlib
import subprocess
from colorama import init, Fore, Style
from prettytable import PrettyTable
import pikepdf

# Инициализация Colorama для цветного вывода в консоли
init(autoreset=True)


def check_pdf_with_qpdf(pdf_path):
    try:
        result = subprocess.run(['qpdf', '--check', pdf_path], capture_output=True, text=True)
        if result.returncode == 0:
            return "Структурно корректен", ""
        else:
            return "Обнаружены проблемы", result.stderr
    except FileNotFoundError:
        return "QPDF не установлен", ""
    except Exception as e:
        return "Ошибка при выполнении проверки", str(e)


def analyze_metadata_with_pikepdf(pdf_path):
    try:
        with pikepdf.open(pdf_path) as pdf:
            metadata = pdf.docinfo
            details = {}
            for key, value in metadata.items():
                details[key] = str(value)
            return "Метаданные найдены", details
    except Exception as e:
        return "Ошибка при анализе метаданных", str(e)


def analyze_pdf_metadata(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata

        creation_date = metadata.get("creationDate", "Неизвестно")
        mod_date = metadata.get("modDate", "Неизвестно")
        producer = metadata.get("producer", "Неизвестно")
        creator = metadata.get("creator", "Неизвестно")

        details = {
            "Дата создания": creation_date,
            "Дата изменения": mod_date,
            "Производитель": producer,
            "Создатель": creator,
        }

        if creation_date != mod_date:
            status = "Даты создания и изменения различаются"
        else:
            status = "Даты совпадают"

        return status, details

    except Exception as e:
        return "Ошибка при анализе метаданных", str(e)


def analyze_trailer_ids(pdf_path):
    try:
        # Открываем PDF файл
        doc = fitz.open(pdf_path)
        trailer_str = doc.pdf_trailer()

        # Используем регулярное выражение для поиска идентификаторов
        id_pattern = re.compile(r'/ID \[ <([^>]+)> <([^>]+)> \]')
        match = id_pattern.search(trailer_str)

        if match:
            id1, id2 = match.groups()
            if id1 == id2:
                return "Идентификаторы совпадают", f"/ID [ <{id1}> <{id2}> ]"
            else:
                return "Идентификаторы различаются", f"Original ID: <{id1}>, Modified ID: <{id2}>"
        else:
            return "Идентификаторы отсутствуют или некорректны", f"/ID {trailer_str}"

    except Exception as e:
        return "Ошибка при анализе идентификаторов", str(e)


def analyze_binary_structure(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            data = f.read()

        file_hash = hashlib.sha256(data).hexdigest()
        suspicious_patterns = []

        if b'ObjStm' in data:
            suspicious_patterns.append("Объектный поток (ObjStm) обнаружен")

        if b'/Encrypt' in data:
            suspicious_patterns.append("Файл зашифрован")

        if suspicious_patterns:
            return "Подозрительные паттерны обнаружены", f"Хэш файла: {file_hash}, {', '.join(suspicious_patterns)}"
        else:
            return "Подозрительные паттерны не обнаружены", f"Хэш файла: {file_hash}"

    except Exception as e:
        return "Ошибка при анализе структуры", str(e)


def analyze_pdf_file(pdf_path):
    table = PrettyTable()
    table.field_names = ["Проверка", "Результат", "Детали"]

    qpdf_status, qpdf_details = check_pdf_with_qpdf(pdf_path)
    table.add_row(["Проверка QPDF", qpdf_status, qpdf_details])

    metadata_status, metadata_details = analyze_pdf_metadata(pdf_path)
    table.add_row(["Анализ метаданных", metadata_status, metadata_details])

    trailer_status, trailer_details = analyze_trailer_ids(pdf_path)
    table.add_row(["Анализ идентификаторов", trailer_status, trailer_details])

    binary_status, binary_details = analyze_binary_structure(pdf_path)
    table.add_row(["Анализ структуры файла", binary_status, binary_details])

    print(table)


def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                print(f"\nОбработка файла: {pdf_path}\n")
                analyze_pdf_file(pdf_path)


if __name__ == "__main__":
    path = 'files'
    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        analyze_pdf_file(path)
    elif os.path.isdir(path):
        process_directory(path)
    else:
        print(Fore.RED + "Указанный путь не является PDF файлом или каталогом.")

    print(Style.BRIGHT + Fore.GREEN + "\nАнализ завершен.")
