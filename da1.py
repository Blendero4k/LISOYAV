import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import time
import json
from urllib.parse import urljoin


class WildberriesParser:
    def __init__(self):
        self.base_url = "https://www.wildberries.ru"
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_page(self, url, params=None):
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_search_results(self, query, pages=1):
        products = []

        for page in range(1, pages + 1):
            print(f"Parsing page {page} of search results for '{query}'")

            params = {
                'search': query,
                'page': page
            }

            url = urljoin(self.base_url, '/catalog/0/search.aspx')
            html = self.get_page(url, params=params)

            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            product_cards = soup.find_all('div', class_='product-card')

            for card in product_cards:
                product = {}

                # Extract basic info
                product['name'] = card.get('data-nm-id', '')
                product['brand'] = card.find('strong', class_='brand-name').get_text(strip=True) if card.find('strong',
                                                                                                              class_='brand-name') else ''
                product['name'] = card.find('span', class_='goods-name').get_text(strip=True) if card.find('span',
                                                                                                           class_='goods-name') else ''

                # Price information
                price_block = card.find('div', class_='price-block')
                if price_block:
                    product['price'] = price_block.find('span', class_='price').get_text(strip=True).replace('₽',
                                                                                                             '').replace(
                        ' ', '') if price_block.find('span', class_='price') else ''
                    product['old_price'] = price_block.find('del', class_='price-old').get_text(strip=True).replace('₽',
                                                                                                                    '').replace(
                        ' ', '') if price_block.find('del', class_='price-old') else ''

                # Rating and reviews
                product['rating'] = card.find('span', class_='rating').get_text(strip=True) if card.find('span',
                                                                                                         class_='rating') else ''
                product['reviews'] = card.find('span', class_='review-count').get_text(strip=True) if card.find('span',
                                                                                                                class_='review-count') else ''

                # URL
                product['url'] = urljoin(self.base_url,
                                         card.find('a', class_='product-card__link').get('href')) if card.find('a',
                                                                                                               class_='product-card__link') else ''

                products.append(product)

            time.sleep(1)  # Delay to avoid being blocked

        return products

    def parse_product_page(self, product_url):
        html = self.get_page(product_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        product_data = {}

        # Main product info
        product_data['title'] = soup.find('h1', class_='name').get_text(strip=True) if soup.find('h1',
                                                                                                 class_='name') else ''
        product_data['brand'] = soup.find('span', class_='brand').get_text(strip=True) if soup.find('span',
                                                                                                    class_='brand') else ''

        # Price block
        price_block = soup.find('div', class_='price-block')
        if price_block:
            product_data['current_price'] = price_block.find('span', class_='final-price').get_text(strip=True).replace(
                '₽', '').replace(' ', '') if price_block.find('span', class_='final-price') else ''
            product_data['original_price'] = price_block.find('del', class_='old-price').get_text(strip=True).replace(
                '₽', '').replace(' ', '') if price_block.find('del', class_='old-price') else ''

        # Rating and reviews
        rating_block = soup.find('div', class_='rating-and-reviews')
        if rating_block:
            product_data['rating'] = rating_block.find('span', class_='rating').get_text(
                strip=True) if rating_block.find('span', class_='rating') else ''
            product_data['reviews_count'] = rating_block.find('a', class_='review-count').get_text(
                strip=True) if rating_block.find('a', class_='review-count') else ''

        # Additional info
        details_block = soup.find('div', class_='product-details')
        if details_block:
            details = {}
            for row in details_block.find_all('div', class_='detail-row'):
                key = row.find('span', class_='detail-name').get_text(strip=True) if row.find('span',
                                                                                              class_='detail-name') else ''
                value = row.find('span', class_='detail-value').get_text(strip=True) if row.find('span',
                                                                                                 class_='detail-value') else ''
                if key and value:
                    details[key] = value
            product_data['details'] = details

        # Description
        description_block = soup.find('div', class_='collapsable-content')
        if description_block:
            product_data['description'] = description_block.get_text(strip=True, separator='\n')

        return product_data

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Data saved to {filename}")

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")


def main():
    parser = WildberriesParser()

    print("Wildberries Parser Application")
    print("1. Parse search results")
    print("2. Parse specific product page")
    choice = input("Select option (1/2): ")

    if choice == '1':
        query = input("Enter search query: ")
        pages = int(input("Enter number of pages to parse: "))
        results = parser.parse_search_results(query, pages)

        if results:
            filename = f"wildberries_search_{query}.csv"
            parser.save_to_csv(results, filename)
            print(f"Found {len(results)} products")
        else:
            print("No results found")

    elif choice == '2':
        url = input("Enter product URL: ")
        product_data = parser.parse_product_page(url)

        if product_data:
            filename = "wildberries_product.json"
            parser.save_to_json(product_data, filename)
            print("Product data extracted successfully")
        else:
            print("Failed to extract product data")

    else:
        print("Invalid option selected")


if __name__ == "__main__":
    main()