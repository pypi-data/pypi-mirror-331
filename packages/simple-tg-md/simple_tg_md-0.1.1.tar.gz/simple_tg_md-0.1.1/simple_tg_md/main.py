import re


def pre_process_markdown(text: str) -> str:
    """
    Предварительная обработка текста: замена двойных маркеров на одинарные.

    Args:
        text (str): Исходный текст

    Returns:
        str: Текст с унифицированными маркерами форматирования
    """
    # Заменяем **текст** на *текст* (жирный)
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)

    # Заменяем ~~текст~~ на ~текст~ (зачеркнутый)
    text = re.sub(r'~~(.*?)~~', r'~\1~', text)

    return text


def process_headers(text: str) -> str:
    """
    Преобразование заголовков в жирный текст.

    Args:
        text (str): Исходный текст

    Returns:
        str: Текст с преобразованными заголовками
    """
    lines = []
    for line in text.split('\n'):
        # Проверяем, является ли строка заголовком (начинается с #)
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if header_match:
            # Извлекаем текст заголовка
            header_text = header_match.group(2)
            # Преобразуем в жирный текст
            lines.append(f'*{header_text}*')
        else:
            lines.append(line)

    return '\n'.join(lines)


def find_formatting_regions(line: str) -> tuple[tuple[int, int, str], ...]:
    """
    Находит области форматирования в строке.

    Args:
        line (str): Строка для анализа

    Returns:
        List[Tuple[int, int, str]]: Список регионов форматирования
    """
    formatting_regions = []

    # Жирный текст
    for match in re.finditer(r'\*(.*?)\*', line):
        start, end = match.span()
        formatting_regions.append((start, start + 1, "format_start"))
        formatting_regions.append((end - 1, end, "format_end"))

    # Курсив
    for match in re.finditer(r'_(.*?)_', line):
        start, end = match.span()
        # Проверяем, что это не часть слова
        prev_char = line[start - 1] if start > 0 else ' '
        next_char = line[end] if end < len(line) else ' '
        if not (prev_char.isalnum() and next_char.isalnum()):
            formatting_regions.append((start, start + 1, "format_start"))
            formatting_regions.append((end - 1, end, "format_end"))

    # Зачеркнутый текст
    for match in re.finditer(r'~(.*?)~', line):
        start, end = match.span()
        formatting_regions.append((start, start + 1, "format_start"))
        formatting_regions.append((end - 1, end, "format_end"))

    # Спойлер
    for match in re.finditer(r'\|\|(.*?)\|\|', line):
        start, end = match.span()
        formatting_regions.append((start, start + 2, "format_start"))
        formatting_regions.append((end - 2, end, "format_end"))

    # Код встроенный
    for match in re.finditer(r'`(.*?)`', line):
        start, end = match.span()
        formatting_regions.append((start, start + 1, "code_start"))
        formatting_regions.append((end - 1, end, "code_end"))

    # Ссылки
    for match in re.finditer(r'\[(.*?)\]\((.*?)\)', line):
        start, end = match.span()
        text_end = line.find(']', start)
        url_start = text_end + 1
        formatting_regions.append((start, start + 1, "link_text_start"))
        formatting_regions.append((text_end, text_end + 1, "link_text_end"))
        formatting_regions.append((url_start, url_start + 1, "link_url_start"))
        # Внутри URL экранируем только ) и \
        for j in range(url_start + 1, end - 1):
            if line[j] in [')', '\\']:
                formatting_regions.append((j, j + 1, "link_url_escape"))
        formatting_regions.append((end - 1, end, "link_url_end"))

    return tuple(sorted(formatting_regions, key=lambda x: x[0]))


def process_code_block(code_block_lines: list[str]) -> list[str]:
    """
    Обработка блока кода с экранированием специальных символов.

    Args:
        code_block_lines (List[str]): Строки блока кода

    Returns:
        List[str]: Обработанные строки блока кода
    """
    processed_lines = []
    for code_line in code_block_lines:
        # Экранируем только ` и \ внутри блока кода
        escaped_line = ''.join('\\' + char if char in ['`', '\\'] else char for char in code_line)
        processed_lines.append(escaped_line)
    return processed_lines


def escape_line(line: str, formatting_regions: tuple[tuple[int, int, str], ...]) -> str:
    """
    Экранирование специальных символов в строке с учетом форматирования.

    Args:
        line (str): Исходная строка
        formatting_regions (List[Tuple[int, int, str]]): Области форматирования

    Returns:
        str: Обработанная строка с экранированием
    """
    processed_line = ''
    i = 0
    in_code = False
    in_link_url = False

    while i < len(line):
        # Проверяем текущий регион форматирования
        current_region = next((region for region in formatting_regions if region[0] == i), None)

        if current_region:
            start, end, region_type = current_region

            if region_type == "code_start":
                in_code = True
                processed_line += '`'
                i = end
            elif region_type == "code_end":
                in_code = False
                processed_line += '`'
                i = end
            elif region_type == "link_url_start":
                in_link_url = True
                processed_line += '('
                i = end
            elif region_type == "link_url_end":
                in_link_url = False
                processed_line += ')'
                i = end
            elif region_type == "link_url_escape":
                # Внутри URL экранируем ) и \
                processed_line += '\\' + line[i]
                i = end
            elif region_type in ["format_start", "format_end", "link_text_start", "link_text_end"]:
                # Добавляем форматирование без изменений
                processed_line += line[start:end]
                i = end
            else:
                # Неизвестный тип региона
                processed_line += line[i]
                i += 1
        else:
            # Не в форматированной области
            if in_code:
                # В коде экранируем только ` и \
                processed_line += '\\' + line[i] if line[i] in ['`', '\\'] else line[i]
            elif in_link_url:
                # В URL экранируем только ) и \
                processed_line += '\\' + line[i] if line[i] in [')', '\\'] else line[i]
            else:
                # Обычный текст - экранируем специальные символы
                processed_line += ('\\' + line[i]) if line[i] in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+',
                                                                  '-', '=', '|', '{', '}', '.', '!'] else line[i]
            i += 1

    return processed_line


def convert_to_md2(text: str) -> str:
    """
    Конвертирует текст в формат Markdown V2 для Telegram с учетом правил экранирования.

    Функция разбивает исходный текст на сегменты: кодовые блоки (огражденные тройными обратными кавычками)
    и обычный текст. Для кодовых блоков применяется функция process_code_block для экранирования символов ` и \,
    а для обычного текста — предварительная обработка с помощью pre_process_markdown и process_headers,
    а затем экранирование специальных символов с использованием escape_line.

    Аргументы:
        text (str): Исходный текст для конвертации.

    Возвращает:
        str: Текст, преобразованный в формат Markdown V2, готовый для использования в Telegram.
    """

    segments = re.split(r'(```.*?```)', text, flags=re.DOTALL)
    result_segments = []

    for seg in segments:
        if seg.startswith('```') and seg.endswith('```'):
            code_content = seg[3:-3]
            code_lines = code_content.split('\n')
            # Обрабатываем строки кода для экранирования ` и \
            processed_code_lines = process_code_block(code_lines[1:])
            # Собираем кодовый блок обратно с тройными обратными кавычками
            result_segments.append(f'```{code_lines[0]}\n' + '\n'.join(processed_code_lines) + '\n```')
        else:
            seg = pre_process_markdown(seg)
            seg = process_headers(seg)
            lines = seg.split('\n')
            processed_lines = []
            for line in lines:
                formatting_regions = find_formatting_regions(line)
                processed_lines.append(escape_line(line, formatting_regions))
            result_segments.append('\n'.join(processed_lines))

    return ''.join(result_segments)
