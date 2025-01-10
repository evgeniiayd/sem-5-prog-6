import requests
import json
import csv
from xml.etree import ElementTree as ET
from typing import List, Dict, Any


# Base class
class CurrenciesList:
    def __init__(self):
        self.cur_lst: dict = {}

    def get_currencies(self, ids_lst) -> List[Dict[str, Any]]:
        """Берет курсы валют с сайта Банка России."""
        cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        result = []

        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall("Valute")
        double_of_ids = ids_lst.copy()

        for _v in valutes:
            valute_id = _v.get('ID')
            valute = {}
            if str(valute_id) in double_of_ids:
                valute_cur_name = _v.find('Name').text
                valute_cur_val = _v.find('Value').text.replace(',', '.')
                valute_nominal = int(_v.find('Nominal').text)
                valute_charcode = _v.find('CharCode').text

                if valute_nominal != 1:
                    valute[valute_charcode] = (valute_cur_name, valute_cur_val, valute_nominal)
                else:
                    valute[valute_charcode] = (valute_cur_name, valute_cur_val)

                result.append(valute)
                self.cur_lst[valute_cur_name] = valute_cur_val
                double_of_ids.remove(str(valute_id))

        for id in double_of_ids:
            invalid_id = {f'{id}': None}
            result.append(invalid_id)

        return result


# Декоратор для JSON-формата
class ConcreteDecoratorJSON(CurrenciesList):
    def get_currencies(self, _ids_lst) -> str:
        """Возвращает валюты в JSON-формате."""
        data = super().get_currencies(_ids_lst)
        return json.dumps(data, ensure_ascii=False, indent=4)


# Decorator for CSV output
class ConcreteDecoratorCSV(CurrenciesList):
    def get_currencies(self, _ids_lst) -> None:
        """Writes currency data to a CSV file."""
        data = super().get_currencies(_ids_lst)
        with open('currencies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Currency Code", "Currency Name", "Value", "Nominal"])
            for item in data:
                for key, value in item.items():
                    if isinstance(value, tuple):
                        writer.writerow([key, value[0], value[1], value[2] if len(value) > 2 else 1])
                    else:
                        writer.writerow([key, None, None, None])


# Example usage
if __name__ == '__main__':
    currencies_list = CurrenciesList() # евро и доллары
    entry_lst = ['R01010', 'R01239']

    # Базовый класс
    print("Результат из Базового класса:")
    print(currencies_list.get_currencies(entry_lst))

    # JSON-декоратор
    json_decorator = ConcreteDecoratorJSON()
    print("\nРезультат в формате JSON:")
    print(json_decorator.get_currencies(entry_lst))

    # CSV-декоратор
    csv_decorator = ConcreteDecoratorCSV()
    csv_decorator.get_currencies(entry_lst)
    print("\nВалюты были записаны в файл currencies.csv.")
