import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import time
import json


class OzonParser:
    def __init__(self):
        self.base_url = "https://www.ozon.ru/"
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_page(self, url, params=None):
        """Получение содержимого страницы"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return None

    def parse_search_results(self, query, pages=1):
        """ Парсинг результатов поиска товаров по ключевому слову. :param query: Запрос для поиска товаров :param pages: Количество страниц для обработки :return: Список найденных товаров """
        products = []

        for page in range(1, pages + 1):
            print(f"Парсим страницу {page} результатов поиска по запросу '{query}'")
            
            params = {'text': query}
            if page > 1:
                params['page'] = str(page)
                
            url = self.base_url + "/category/?text=" + query
            html = self.get_page(url, params=params)

            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            product_cards = soup.select('.tile-hover-target')

            for card in product_cards:
                product = {}

                # Основная информация о товаре
                product['name'] = card.find('img').get('alt', '')
                product['brand'] = card.find('a', class_='b7j9ge-widget').get_text(strip=True) \
                    if card.find('a', class_='b7j9ge-widget') else ''

                # Цена товара
                price_block = card.find('span', class_='k7omze-widget')
                if price_block:
                    product['price'] = price_block.get_text(strip=True).replace('₽', '').strip()

                # Рейтинг и количество отзывов
                rating_block = card.find('div', class_='y3x1kw-widget')
                if rating_block:
                    product['rating'] = rating_block.find('span', class_='c2t2mf-widget').get_text(strip=True)\
                        .split()[0]
                    product['reviews'] = rating_block.find('span', class_='r9xv4s-widget').get_text(strip=True)\
                        .split()[0].replace(',', '.')

                # URL продукта
                href = card.find('a', class_='tsBodyL').get('href')
                product['url'] = self.base_url.rstrip('/') + href if href.startswith('/') else href

                products.append(product)

            time.sleep(1)  # Задержка перед следующим запросом

        return products

    def parse_product_page(self, product_url):
        """ Получение детальной информации о конкретном продукте. :param product_url: Полный URL страницы товара :return: Словарь с информацией о продукте """
        html = self.get_page(product_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        product_data = {}

        # Название товара
        title_element = soup.find('h1', class_='u3gy7v-widget')
        product_data['title'] = title_element.get_text(strip=True) if title_element else ''

        # Бренд товара
        brand_element = soup.find('a', class_='wldgt-widget')
        product_data['brand'] = brand_element.get_text(strip=True) if brand_element else ''

        # Текущая и старая цена
        current_price_element = soup.find('span', class_='u3gy7v-widget')
        original_price_element = soup.find('del', class_='frcxtz-widget')
        product_data['current_price'] = current_price_element.get_text(strip=True).replace('₽', '').strip()\
            if current_price_element else ''
        product_data['original_price'] = original_price_element.get_text(strip=True).replace('₽', '').strip()\
            if original_price_element else ''

        # Рейтинг и количество отзывов
        rating_block = soup.find('div', class_='rb7uwz-widget')
        if rating_block:
            product_data['rating'] = rating_block.find('span', class_='f8pqw5-widget').get_text(strip=True)\
                .split()[0]
            product_data['reviews_count'] = rating_block.find('span', class_='rgvvfb-widget').get_text(strip=True)\
                .split()[0].replace(',', '.')

        # Дополнительная информация о продукте
        details_block = soup.find('ul', class_='esdpgv-widget')
        if details_block:
            details = {}
            for detail_row in details_block.find_all('li'):
                parts = detail_row.get_text(strip=True).split(': ')
                if len(parts) >= 2:
                    key, value = parts[:2]
                    details[key.strip()] = value.strip()
            product_data['details'] = details

        # Описание товара
        description_block = soup.find('div', class_='eeopaw-widget')
        if description_block:
            product_data['description'] = description_block.get_text(strip=True, separator='\n')

        return product_data

    def save_to_csv(self, data, filename):
        """Сохранение списка товаров в CSV."""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Данные сохранены в {filename}")

    def save_to_json(self, data, filename):
        """Сохранение данных о продукте в JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в {filename}")


def main():
    parser = OzonParser()
    
    print("Парсер Ozon:")
    print("1. Парсинг результатов поиска")
    print("2. Детальная информация о товаре")
    choice = input("Выберите действие (1/2): ")

    if choice == '1':
        query = input("Введите поисковый запрос: ")
        pages = int(input("Количество страниц для парсинга: "))
        results = parser.parse_search_results(query, pages)

        if results:
            filename = f"ozon_search_{query}.csv"
            parser.save_to_csv(results, filename)
            print(f"Обнаружено {len(results)} товаров.")
        else:
            print("Нет результатов поиска.")

    elif choice == '2':
        url = input("Введите ссылку на товар: ")
        product_data = parser.parse_product_page(url)

        if product_data:
            filename = "ozon_product.json"
            parser.save_to_json(product_data, filename)
            print("Информация о продукте успешно извлечена.")
        else:
            print("Извлечь информацию о продукте не удалось.")

    else:
        print("Неверный выбор действия.")


if __name__ == "__main__":
    main()