import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

class OzonParser:
    def __init__(self):
        self.base_url = "https://www.ozon.ru"
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
        }
        
    def get_product_by_article(self, article):
        search_url = f"{self.base_url}/search/?text={article}&from_global=true"
        
        try:
            # Получаем страницу поиска
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Находим первый товар в результатах поиска
            product_link = soup.find('a', {'class': 'tile-hover-target'})
            if not product_link:
                return {"error": "Товар не найден"}
                
            product_url = self.base_url + product_link.get('href')
            
            # Получаем страницу товара
            product_response = requests.get(product_url, headers=self.headers)
            product_response.raise_for_status()
            
            product_soup = BeautifulSoup(product_response.text, 'html.parser')
            
            # Парсим информацию о товаре
            product_data = {
                "article": article,
                "url": product_url,
                "title": self._get_title(product_soup),
                "price": self._get_price(product_soup),
                "rating": self._get_rating(product_soup),
                "reviews_count": self._get_reviews_count(product_soup),
                "seller": self._get_seller(product_soup),
                "characteristics": self._get_characteristics(product_soup)
            }
            
            return product_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_title(self, soup):
        title_tag = soup.find('h1')
        return title_tag.text.strip() if title_tag else "Не удалось получить название"
    
    def _get_price(self, soup):
        price_tag = soup.find('span', {'class': 'c308-a'})
        return price_tag.text.strip() if price_tag else "Не удалось получить цену"
    
    def _get_rating(self, soup):
        rating_tag = soup.find('div', {'class': 'c306-a'})
        return rating_tag.text.strip() if rating_tag else "Не удалось получить рейтинг"
    
    def _get_reviews_count(self, soup):
        reviews_tag = soup.find('a', {'class': 'c306-b'})
        return reviews_tag.text.strip() if reviews_tag else "Не удалось получить количество отзывов"
    
    def _get_seller(self, soup):
        seller_tag = soup.find('a', {'class': 'c307-b'})
        return seller_tag.text.strip() if seller_tag else "Не удалось получить продавца"
    
    def _get_characteristics(self, soup):
        characteristics = {}
        chars_section = soup.find('div', {'class': 'c308-b'})
        if chars_section:
            for row in chars_section.find_all('dl'):
                key = row.find('dt').text.strip() if row.find('dt') else None
                value = row.find('dd').text.strip() if row.find('dd') else None
                if key and value:
                    characteristics[key] = value
        return characteristics

if __name__ == "__main__":
    parser = OzonParser()
    
    print("Ozon Parser - поиск товара по артикулу")
    article = input("Введите артикул товара: ")
    
    result = parser.get_product_by_article(article)
    print("\nРезультат:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
