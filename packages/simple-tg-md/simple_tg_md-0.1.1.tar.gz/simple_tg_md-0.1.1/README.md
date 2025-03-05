# simple-tg-md
Библиотека, которая поможет конвертировать текст в специфичный Telegram MarkdownV2, корректно экранируя символы не относящиеся к стандартному форматированию Markdown

[![PyPI version](https://badge.fury.io/py/simple-tg-md.svg)](https://badge.fury.io/py/simple-tg-md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions](https://img.shields.io/pypi/pyversions/simple-tg-md.svg)

## Установка

```bash
pip install simple-tg-md
```

## Требования

- Python 3.9 или выше

## Возможности

Библиотека поддерживает преобразование следующих форматов:

- Жирный текст (`*текст*`)
- Курсив (`_текст_`)
- Зачеркнутый текст (`~текст~`)
- Спойлер (`||текст||`)
- Встроенный код (`` `код` ``)
- Блоки кода (` ```код``` `)
- Ссылки (`[текст](ссылка)`)
- Заголовки (преобразуются в жирный текст)

## Примеры использования

```python
from simple_tg_md import convert_to_md2

# Простой пример
text = "**Жирный текст** и _курсив_"
markdown_text = convert_to_md2(text)
print(markdown_text)

# Пример со ссылкой
link_text = "Посетите [Telegram](https://telegram.org)"
markdown_link = convert_to_md2(link_text)
print(markdown_link)

# Пример с блоком кода
code_text = """
# Пример кода
def hello():
    print("Hello, World!")
"""
markdown_code = convert_to_md2(code_text)
print(markdown_code)
```

## Правила конвертации

1. Специальные символы Telegram Markdown V2 автоматически экранируются
2. Двойные маркеры форматирования (`**текст**`, `~~текст~~`) преобразуются в одинарные
3. Заголовки преобразуются в жирный текст
4. Поддерживается вложенное форматирование
