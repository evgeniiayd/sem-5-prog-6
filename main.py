import requests
import json
import csv
from xml.etree import ElementTree as ET
from typing import List, Dict, Any


# Base class
class CurrenciesList:
    def __init__(self):
        self.cur_lst: dict = {}
        self._ids_lst: list = []

    def set_ids(self, ids_lst: List[str]):
        self._ids_lst = ids_lst

    def get_currencies(self) -> List[Dict[str, Any]]:
        """Fetches currency data from the Central Bank of Russia."""
        cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        result = []

        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall("Valute")
        double_of_ids = self._ids_lst.copy()

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


# Decorator for JSON output
class ConcreteDecoratorJSON:
    def __init__(self, currencies_list: CurrenciesList):
        self._currencies_list = currencies_list

    def get_currencies(self) -> str:
        """Returns currency data in JSON format."""
        data = self._currencies_list.get_currencies()
        return json.dumps(data, ensure_ascii=False, indent=4)


# Decorator for CSV output
class ConcreteDecoratorCSV:
    def __init__(self, currencies_list: CurrenciesList):
        self._currencies_list = currencies_list

    def get_currencies(self) -> None:
        """Writes currency data to a CSV file."""
        data = self._currencies_list.get_currencies()
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
    currencies_list = CurrenciesList()
    currencies_list.set_ids(['R01010', 'R01239'])  # USD and EUR

    # Using base class
    print("Base Currencies List:")
    print(currencies_list.get_currencies())

    # Using JSON decorator
    json_decorator = ConcreteDecoratorJSON(currencies_list)
    print("\nCurrencies in JSON format:")
    print(json_decorator.get_currencies())

    # Using CSV decorator
    csv_decorator = ConcreteDecoratorCSV(currencies_list)
    csv_decorator.get_currencies()
    print("\nCurrency data has been written to currencies.csv.")
