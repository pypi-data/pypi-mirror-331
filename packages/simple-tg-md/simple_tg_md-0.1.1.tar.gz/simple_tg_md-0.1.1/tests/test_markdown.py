import unittest
from simple_tg_md import convert_to_md2


class TestMarkdownConverter(unittest.TestCase):
    def test_basic_formatting(self):
        """Тест базовых форматов форматирования"""
        test_cases = [
            # Жирный текст
            ("**Жирный текст**", "*Жирный текст*"),
            # Курсив
            ("_Курсивный текст_", "_Курсивный текст_"),
            # Зачеркнутый текст
            ("~~Зачеркнутый текст~~", "~Зачеркнутый текст~"),
            # Спойлер
            ("||Спойлер||", "||Спойлер||"),
            # Встроенный код
            ("`Код`", "`Код`"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(convert_to_md2(input_text), expected)

    def test_headers(self):
        """Тест преобразования заголовков"""
        test_cases = [
            ("# Заголовок 1", "*Заголовок 1*"),
            ("## Заголовок 2", "*Заголовок 2*"),
            ("### Заголовок 3", "*Заголовок 3*"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(convert_to_md2(input_text), expected)

    def test_no_formatting(self):
        """Тест текста без форматирования"""
        input_text = "Обычный текст без форматирования"

        self.assertEqual(convert_to_md2(input_text), input_text)


if __name__ == '__main__':
    unittest.main()
