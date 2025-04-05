import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

# Функция для получения HTML страницы
def get_html(url):
    response = requests.get(url)
    return response.text

# Функция для извлечения отзывов
def parse_reviews(html):
    soup = BeautifulSoup(html, 'html.parser')
    reviews = []
    
    for review in soup.find_all('div', class_='review'):
        text = review.find('p').text.strip()
        author = review.find('span', class_='author').text.strip()
        rating = review.find('span', class_='rating').text.strip()
        date = review.find('time')['datetime']
        
        reviews.append({
            'text': text,
            'author': author,
            'rating': rating,
            'date': date
        })
    
    return reviews

# Основная функция для парсинга и сохранения данных
def main():
    url_list = ['https://www.ozon.ru/product/otzyvy/?productId=1234567']  # Список URL с отзывами
    all_reviews = []
    
    for url in url_list:
        html = get_html(url)
        reviews = parse_reviews(html)
        all_reviews.extend(reviews)
    
    with open('reviews.json', 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()