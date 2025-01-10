import json
import unittest
import requests
from main import CurrenciesList, ConcreteDecoratorJSON, ConcreteDecoratorCSV


class TestCurrenciesList(unittest.TestCase):
    def setUp(self):
        """Инициализация объекта"""
        self.currencies = CurrenciesList()

    def test_empty_ids_list(self):
        """Тест на случай, если передан пустой список ID валют"""
        result = self.currencies.get_currencies([])
        self.assertEqual(result, [], "Результат должен быть пустым списком")

    def test_invalid_id(self):
        """Тест на случай, если передан несуществующий ID валюты"""
        result = self.currencies.get_currencies(['INVALID_ID'])
        self.assertEqual(len(result), 1, "Должен быть один элемент в результате для несуществующего ID")
        self.assertEqual(result[0], {'INVALID_ID': None},
                         "Результат должен содержать None для несуществующего ID")

    def test_multiple_ids(self):
        """Тест на случай, если переданы несколько валидных ID валют"""
        result = self.currencies.get_currencies(['R01235', 'R01239'])  # USD и EUR
        self.assertTrue(len(result) == 2, "Результат должен быть списком из двух элементов")

    def test_mixed_ids(self):
        """Тест на случай, если переданы валидные и невалидные ID валют"""
        result = self.currencies.get_currencies(['R01235', 'INVALID_ID'])
        self.assertTrue(len(result) == 2, "Результат должен содержать два элемента")

    def test_csv_format(self):
        """Тест на получение данных в CSV-формате."""
        csv_decorator = ConcreteDecoratorCSV()
        result = csv_decorator.get_currencies(['R01235'])  # USD
        self.assertIn('Currency Code', result, "Результат должен содержать заголовок 'Currency Code'")

    def test_cur_lst_update(self):
        """Тест на обновление словаря cur_lst при получении валют"""
        self.currencies.get_currencies(['R01235'])  # USD
        self.assertIn('Доллар США', self.currencies.cur_lst, "Словарь cur_lst должен содержать 'Доллар США'")

    def test_json_format(self):
        """Тест на получение данных в JSON-формате."""
        json_decorator = ConcreteDecoratorJSON()
        result = json_decorator.get_currencies(['R01235'])  # USD

        # Проверяем, что результат - это корректный JSON
        self.assertIsInstance(result, str, "Результат должен быть строкой.")

        json_data = None

        # Пробуем загрузить результат как JSON
        try:
            json_data = json.loads(result)
        except json.JSONDecodeError:
            self.fail("Результат не является корректным JSON.")

        # Проверяем, что JSON содержит хотя бы один элемент
        self.assertTrue(len(json_data) > 0, "JSON должен содержать хотя бы одну валюту.")

        # Проверяем, что в JSON есть ожидаемые поля для первой валюты
        first_currency = json_data[0]
        self.assertIn('USD', first_currency, "Первый элемент JSON должен содержать 'USD'.")
        self.assertIn('Доллар США', first_currency['USD'],
                      "Первый элемент JSON должен содержать имя валюты")
        # Дополнительно проверяем, что значения не пустые
        self.assertIsNotNone(list(first_currency.keys())[0], "Код валюты не должен быть None.")


if __name__ == '__main__':
    unittest.main()
