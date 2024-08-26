from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, TextStringObject
from datetime import datetime
import os


def show_metadata(metadata):
    """Функция для отображения текущих метаданных."""
    print("\nТекущие метаданные PDF:")
    simplified_metadata = {}
    for key, value in metadata.items():
        readable_key = key.strip('/')  # Убираем префикс `/` для показа
        if readable_key in ["CreationDate", "ModDate"]:
            value = format_pdf_date(value)  # Форматируем дату для показа
        simplified_metadata[readable_key] = value
        print(f"{readable_key}: {value}")
    return simplified_metadata


def format_pdf_date(pdf_date_str):
    """Форматирует дату из формата PDF в человекочитаемый американский вид (MM-DD-YYYY HH:MM:SS)."""
    try:
        # Ожидаем формат D:YYYYMMDDHHMMSS
        date = datetime.strptime(pdf_date_str[:16], "D:%Y%m%d%H%M%S")
        return date.strftime("%m-%d-%Y %H:%M:%S")
    except ValueError:
        return pdf_date_str  # Если дата не в ожидаемом формате, возвращаем как есть


def unformat_pdf_date(human_readable_date):
    """Преобразует дату из американского формата MM-DD-YYYY HH:MM:SS обратно в формат PDF."""
    try:
        # Преобразуем обратно в формат D:MMDDYYYYHHMMSS
        date = datetime.strptime(human_readable_date, "%m-%d-%Y %H:%M:%S")
        return date.strftime("D:%Y%m%d%H%M%S")
    except ValueError:
        return human_readable_date  # Если формат не распознается, возвращаем как есть


def prompt_for_metadata_change(metadata):
    """Функция для изменения метаданных на основе ввода пользователя."""
    while True:
        # Показываем текущие метаданные и упрощаем их для пользователя
        simplified_metadata = show_metadata(metadata)

        # Спрашиваем, какое поле пользователь хочет изменить
        field_to_change = input(
            "\nВведите ключ метаданных, который хотите изменить (например, Title), или 'exit' для выхода: ")

        if field_to_change.lower() == "exit":
            break

        # Проверяем, существует ли такой ключ в метаданных
        if field_to_change in simplified_metadata:
            current_value = simplified_metadata[field_to_change]
            new_value = input(f"Введите новое значение для {field_to_change} (текущее: '{current_value}'): ")

            # Возвращаем дату в оригинальный формат при сохранении
            if field_to_change in ["CreationDate", "ModDate"]:
                new_value = unformat_pdf_date(new_value)

            # Обновляем метаданные с использованием NameObject для ключей и TextStringObject для значений
            metadata[NameObject(f"/{field_to_change}")] = TextStringObject(new_value)
            print(f"Значение {field_to_change} изменено на '{new_value}'")
        else:
            print(f"Ключ '{field_to_change}' не найден в метаданных. Пожалуйста, попробуйте снова.")

        # Спрашиваем, хочет ли пользователь изменить еще что-то
        more_changes = input("Хотите изменить что-то еще? (y/n): ").strip().lower()
        if more_changes != 'y':
            break


def modify_pdf_metadata(input_pdf_path, output_pdf_path):
    """Функция для отображения и изменения метаданных PDF."""
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Копируем страницы
    for page in reader.pages:
        writer.add_page(page)

    # Получаем текущие метаданные
    current_metadata = reader.metadata

    # Спрашиваем пользователя о новых значениях метаданных
    prompt_for_metadata_change(current_metadata)

    # Добавляем новые метаданные в PDF
    writer.add_metadata(current_metadata)

    # Сохраняем новый файл с обновленными метаданными
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

    print(f"\nМетаданные обновлены и сохранены в {output_pdf_path}")


def main():
    input_pdf_path = input("Введите путь к вашему PDF-файлу: ")

    # Генерация имени выходного файла с префиксом "md__"
    base_dir = os.path.dirname(input_pdf_path)
    base_name = os.path.basename(input_pdf_path)
    output_pdf_path = os.path.join(base_dir, f"md__{base_name}")

    print(f"\nФайл будет сохранен как: {output_pdf_path}")

    modify_pdf_metadata(input_pdf_path, output_pdf_path)


if __name__ == "__main__":
    main()
