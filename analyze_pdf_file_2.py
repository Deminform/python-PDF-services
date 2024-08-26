import os
import fitz  # PyMuPDF
import hashlib
from colorama import init, Fore, Style
import pikepdf
from lxml import etree

# Инициализация Colorama для цветного вывода в консоли
init(autoreset=True)


def analyze_pdf_objects(doc):
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Используем load_page для явной загрузки страницы
        print(f"\n{Fore.CYAN}Страница {page_num + 1}:")
        print(f"{Fore.CYAN}Объекты на странице:")
        text = page.get_text("dict")
        for block in text.get("blocks", []):
            print(f"{Fore.YELLOW}Текстовый блок: {block['bbox']}")
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    print(f"  Линия: {line['bbox']}, Текст: {span['text']}")




def analyze_pdf_images(doc):
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"\n{Fore.CYAN}Страница {page_num + 1}:")
        images = page.get_images(full=True)
        if not images:
            print(f"{Fore.YELLOW}На странице нет изображений.")
        for img in images:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_hash = hashlib.md5(base_image.get("image", b"")).hexdigest()
            # Отображаем только важные метаданные
            print(f"{Fore.YELLOW}Изображение {xref}:")
            print(f"  MD5 хэш изображения: {image_hash}")
            print(f"  Расширение: {base_image.get('ext')}")
            print(f"  Размеры: {base_image.get('width')}x{base_image.get('height')}")
            print(f"  Цветовое пространство: {base_image.get('cs-name')}")
            print(f"  Биты на компонент: {base_image.get('bpc')}")
            print(f"  Разрешение: {base_image.get('xres')}x{base_image.get('yres')} DPI")



def analyze_pdf_fonts(doc):
    print(f"\n{Fore.CYAN}Проверка целостности шрифтов:")
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            fonts = page.get_fonts(full=True)
            for font in fonts:
                font_name = font[3]
                font_flags = font[6]
                if font_flags & 4:  # Проверка на встраивание шрифта
                    print(f"{Fore.GREEN}Шрифт '{font_name}' встроен на странице {page_num + 1}.")
                else:
                    print(f"{Fore.YELLOW}Шрифт '{font_name}' не встроен на странице {page_num + 1}. Это может быть подозрительно.")
    except Exception as e:
        print(f"Ошибка при проверке шрифтов: {e}")

def analyze_trailer_and_metadata(doc):
    print(f"\n{Fore.CYAN}Анализ трейлера и метаданных документа:")
    trailer = doc.pdf_trailer()
    print(f"{Fore.YELLOW}Трейлер: {trailer}")

    metadata = doc.metadata
    print(f"{Fore.YELLOW}Метаданные документа: {metadata}")

    pdf_version = metadata.get("format", "Неизвестно")
    print(f"{Fore.YELLOW}Версия PDF: {pdf_version}")


def extract_xmp_metadata(pdf_path):
    print(f"\n{Fore.CYAN}Извлечение XMP-метаданных:")
    try:
        with pikepdf.open(pdf_path) as pdf:
            xmp_data = pdf.open_metadata()

            if xmp_data is not None:
                xmp_xml_str = ''.join([str(part) for part in xmp_data]).strip()

                if xmp_xml_str:  # Проверяем, не является ли строка пустой
                    xmp_xml = etree.fromstring(xmp_xml_str.encode('utf-8'))
                    namespaces = {
                        'xmp': 'http://ns.adobe.com/xap/1.0/',
                        'dc': 'http://purl.org/dc/elements/1.1/',
                        'pdf': 'http://ns.adobe.com/pdf/1.3/',
                        'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
                        'tiff': 'http://ns.adobe.com/tiff/1.0/',
                        'exif': 'http://ns.adobe.com/exif/1.0/',
                        'xmpMM': 'http://ns.adobe.com/xap/1.0/mm/'
                    }

                    for elem in xmp_xml.findall('.//xmp:*', namespaces):
                        print(f"{elem.tag} -> {elem.text}")

                    for elem in xmp_xml.findall('.//xmpMM:History', namespaces):
                        print("\nИстория ревизий:")
                        for item in elem:
                            print(f"{item.tag} -> {item.text}")

                    print("\nДополнительные метаданные:")
                    for elem in xmp_xml.findall('.//pdf:*', namespaces):
                        print(f"{elem.tag} -> {elem.text}")
                else:
                    print(f"{Fore.RED}XMP-метаданные пусты или отсутствуют.")
            else:
                print(f"{Fore.RED}XMP-метаданные отсутствуют в документе.")

    except Exception as e:
        print(f"Ошибка при извлечении XMP-метаданных: {e}")

def check_for_hidden_streams(doc):
    hidden_streams = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        for img in images:
            xref = img[0]
            image_stream = doc.extract_image(xref)
            if b'/ObjStm' in image_stream['image']:
                hidden_streams.append((page_num, xref))
    return hidden_streams

def check_incremental_updates(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            data = f.read()
        if b'startxref' in data:
            xrefs = data.split(b'startxref')
            if len(xrefs) > 2:
                return True  # Документ имеет инкрементальные обновления
    except Exception as e:
        print(f"Ошибка при проверке инкрементальных обновлений: {e}")
    return False

def custom_check_xref(doc):
    xref_table = {}
    errors = []  # Инициализация списка ошибок

    for page_num in range(len(doc)):
        page = doc[page_num]
        contents = page.get_contents()  # Получаем все XRef на странице

        if contents:  # Проверяем, не пуст ли список объектов содержимого страницы
            for xref in contents:
                try:
                    obj = doc.xref_object(xref)
                    position = obj if obj else None

                    if position is None:
                        errors.append(f"XRef {xref} не найден или поврежден.")
                    elif xref in xref_table:
                        xref_table[xref].append(position)
                    else:
                        xref_table[xref] = [position]

                except Exception as e:
                    errors.append(f"Ошибка при обработке XRef {xref}: {str(e)}")

    for xref, positions in xref_table.items():
        if len(positions) > 1:
            errors.append(f"Объект {xref} встречается несколько раз в позициях: {positions}")
        elif positions[0] == 0:
            errors.append(f"Объект {xref} имеет неверное смещение: {positions[0]}")

    return errors if errors else None

def check_for_javascript(doc):
    print(f"\n{Fore.CYAN}Проверка на наличие JavaScript:")
    try:
        js_actions = doc.get_js()
        if js_actions:
            print(f"{Fore.RED}Обнаружен JavaScript в документе.")
        else:
            print(f"{Fore.GREEN}JavaScript отсутствует в документе.")
    except Exception as e:
        print(f"Ошибка при проверке JavaScript: {e}")


def check_fonts_integrity(doc):
    print(f"\n{Fore.CYAN}Проверка целостности шрифтов:")
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            fonts = page.get_fonts(full=True)
            for font in fonts:
                font_name = font[3]
                font_flags = font[6]
                if font_flags & 4:  # Проверка на встраивание шрифта
                    print(f"{Fore.GREEN}Шрифт '{font_name}' встроен на странице {page_num + 1}.")
                else:
                    print(f"{Fore.YELLOW}Шрифт '{font_name}' не встроен на странице {page_num + 1}. Это может быть подозрительно.")
    except Exception as e:
        print(f"Ошибка при проверке шрифтов: {e}")


def scan_document_for_hidden_changes(pdf_path):
    doc = fitz.open(pdf_path)

    print(f"{Style.BRIGHT + Fore.CYAN}Сканирование PDF файла: {pdf_path}\n")

    hidden_streams = check_for_hidden_streams(doc)
    if hidden_streams:
        print(f"{Fore.RED}Обнаружены скрытые потоки данных на страницах:")
        for page_num, xref in hidden_streams:
            print(f"Страница {page_num + 1}, Объект XRef: {xref}")
    else:
        print(f"{Fore.GREEN}Скрытые потоки данных не обнаружены.")

    incremental_updates = check_incremental_updates(pdf_path)
    if incremental_updates:
        print(f"{Fore.RED}Документ содержит инкрементальные обновления, возможны изменения после создания.")
    else:
        print(f"{Fore.GREEN}Инкрементальные обновления отсутствуют.")

    xref_errors = custom_check_xref(doc)
    if xref_errors:
        print(f"{Fore.RED}Ошибки в перекрестных ссылках:")
        for error in xref_errors:
            print(f"  {error}")
    else:
        print(f"{Fore.GREEN}Ошибки в перекрестных ссылках отсутствуют.")

def full_pdf_analysis(pdf_path):
    doc = fitz.open(pdf_path)

    print(f"{Style.BRIGHT + Fore.CYAN}Анализ PDF файла: {pdf_path}\n")

    analyze_pdf_objects(doc)
    analyze_pdf_images(doc)
    analyze_pdf_fonts(doc)
    analyze_trailer_and_metadata(doc)
    extract_xmp_metadata(pdf_path)
    scan_document_for_hidden_changes(pdf_path)
    check_for_javascript(doc)
    check_fonts_integrity(doc)
    # check_pdf_version(doc)

if __name__ == "__main__":
    path = 'files/Request for Financial Info March 23, 2023_1.pdf'
    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        full_pdf_analysis(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_pdf_analysis(os.path.join(root, file))
    else:
        print(Fore.RED + "Указанный путь не является PDF файлом или каталогом.")
    print(Style.BRIGHT + Fore.GREEN + "\nАнализ завершен.")
