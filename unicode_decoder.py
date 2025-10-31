#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unicode/Escape Sequence Decoder
Автоматически декодирует все escape-последовательности в текстовых файлах
"""

import os
import sys
import re
import codecs
from pathlib import Path

# Настройка кодировки для Windows консоли
if sys.platform == 'win32':
    # Устанавливаем UTF-8 для stdout/stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# Список расширений текстовых файлов для обработки
TEXT_EXTENSIONS = {
    '.txt', '.json', '.log', '.xml', '.csv', '.html', '.htm',
    '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.c', '.cpp',
    '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
    '.md', '.markdown', '.yaml', '.yml', '.ini', '.cfg', '.conf',
    '.sql', '.sh', '.bat', '.ps1', '.css', '.scss', '.sass', '.less'
}


def detect_encoding(file_path):
    """Определение кодировки файла"""
    # Пробуем разные кодировки
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'cp866', 'latin-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue

    # Если ничего не подошло, используем utf-8 с игнорированием ошибок
    return 'utf-8'


def decode_unicode_escapes(text):
    """
    Декодирует все виды escape-последовательностей в тексте
    """
    original_text = text
    decoded = text

    # 1. Декодируем Unicode escape-последовательности (\uXXXX)
    if '\\u' in text:
        try:
            # Используем регулярное выражение для поиска \uXXXX паттернов
            def replace_unicode(match):
                try:
                    # Преобразуем \uXXXX в символ
                    hex_val = match.group(1)
                    return chr(int(hex_val, 16))
                except:
                    return match.group(0)

            decoded = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, decoded)
        except Exception as e:
            print(f"  Предупреждение: ошибка при декодировании \\uXXXX: {e}", flush=True)

    # 2. Декодируем hex escape-последовательности (\xXX)
    if '\\x' in decoded:
        try:
            def replace_hex(match):
                try:
                    hex_val = match.group(1)
                    return chr(int(hex_val, 16))
                except:
                    return match.group(0)

            decoded = re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, decoded)
        except Exception as e:
            print(f"  Предупреждение: ошибка при декодировании \\xXX: {e}", flush=True)

    # 3. Декодируем экранированные слеши (JSON)
    if r'\/' in decoded:
        decoded = decoded.replace(r'\/', '/')

    # 4. Управляющие символы (\n, \r, \t и другие) НЕ декодируем - оставляем как есть

    # 5. Проверяем, изменился ли текст
    return decoded


def is_text_file(file_path):
    """Проверка, является ли файл текстовым"""
    # Проверяем расширение
    if file_path.suffix.lower() in TEXT_EXTENSIONS:
        return True

    # Для файлов без расширения или с неизвестным расширением
    # пробуем прочитать первые байты
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(512)
            # Проверяем на наличие null-байтов (признак бинарного файла)
            if b'\x00' in chunk:
                return False
            # Пытаемся декодировать как текст
            chunk.decode('utf-8')
            return True
    except:
        return False


def process_file(file_path):
    """Обработка одного файла"""
    try:
        # Определяем кодировку
        encoding = detect_encoding(file_path)

        # Читаем файл
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        # Декодируем escape-последовательности
        decoded_content = decode_unicode_escapes(content)

        # Проверяем, изменился ли контент
        if decoded_content == content:
            print("  [SKIP] Изменений не обнаружено", flush=True)
            return False

        # Создаем имя для нового файла
        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent

        new_file_path = parent / f"{stem}_decoded{suffix}"

        # Сохраняем декодированный файл
        with open(new_file_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(decoded_content)

        # Получаем размеры для статистики
        original_size = os.path.getsize(file_path)
        new_size = os.path.getsize(new_file_path)

        print(f"  [OK] Создан: {new_file_path.name}", flush=True)
        print(f"    Размер: {original_size:,} -> {new_size:,} байт", flush=True)

        return True

    except Exception as e:
        print(f"  [ERROR] Ошибка: {e}", flush=True)
        return False


def main():
    """Основная функция"""
    print("=" * 70)
    print("  Unicode/Escape Sequence Decoder")
    print("  Декодирование escape-последовательностей в текстовых файлах")
    print("=" * 70)
    print()

    # Получаем текущую директорию
    current_dir = Path.cwd()
    print(f"Рабочая директория: {current_dir}")
    print()

    # Получаем список всех файлов
    all_files = [f for f in current_dir.iterdir() if f.is_file()]

    # Фильтруем текстовые файлы и исключаем уже обработанные
    files_to_process = []
    for file_path in all_files:
        # Пропускаем сам скрипт
        if file_path.name == os.path.basename(__file__):
            continue

        # Пропускаем уже обработанные файлы
        if '_decoded' in file_path.stem:
            continue

        # Проверяем, является ли файл текстовым
        if is_text_file(file_path):
            files_to_process.append(file_path)

    if not files_to_process:
        print("Текстовые файлы для обработки не найдены.")
        print()
        return

    print(f"Найдено файлов для обработки: {len(files_to_process)}")
    print()

    # Обрабатываем каждый файл
    processed_count = 0
    skipped_count = 0
    error_count = 0

    for i, file_path in enumerate(files_to_process, 1):
        print(f"[{i}/{len(files_to_process)}] Обработка: {file_path.name}")

        result = process_file(file_path)

        if result is True:
            processed_count += 1
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1

        print()

    # Итоговая статистика
    print("=" * 70)
    print("Обработка завершена!")
    print(f"  Успешно обработано: {processed_count}")
    print(f"  Пропущено (без изменений): {skipped_count}")
    print(f"  Ошибок: {error_count}")
    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nОбработка прервана пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        sys.exit(1)
