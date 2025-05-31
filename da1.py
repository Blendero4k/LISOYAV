import requests
import json
import time
from urllib.parse import urlencode

def get_product_info(article):
    """Получаем информацию о товаре с обходом блокировок"""
    url = f"https://card.wb.ru/cards/detail?{urlencode({'nm': article, 'dest': -1257786})}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': f'https://www.wildberries.ru/catalog/{article}/detail.aspx'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('products'):
                return data['data']['products'][0]
        
        # Пробуем альтернативный API
        alt_url = f"https://wbx-content.wildberries.ru/v1/cards/detail?nm={article}"
        response = requests.get(alt_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('products'):
                return data['data']['products'][0]
                
    except Exception as e:
        print(f"Ошибка запроса: {str(e)}")
    
    return None

def get_feedbacks(product_id, limit=10):
    """Получаем отзывы с обходом блокировок"""
    vol = product_id // 100000
    part = product_id // 1000
    
    # Пробуем несколько серверов с отзывами
    feedback_servers = [
        f"https://feedbacks1.wb.ru/feedbacks/{vol}/{part}/{product_id}",
        f"https://feedbacks2.wb.ru/feedbacks/{vol}/{part}/{product_id}",
        f"https://feedbacks.wb.ru/feedbacks/{vol}/{part}/{product_id}"
    ]
    
    for server in feedback_servers:
        try:
            response = requests.get(server, timeout=10)
            if response.status_code == 200:
                feedbacks = response.json().get('feedbacks', [])[:limit]
                if feedbacks:
                    return feedbacks
        except:
            continue
    
    return []

def save_feedbacks(article, feedbacks):
    """Сохраняем отзывы в файл"""
    with open('reviews.txt', 'w', encoding='utf-8') as f:
        if not feedbacks:
            f.write(f"Для товара {article} не найдено отзывов\n")
            return
        
        f.write(f"Последние отзывы на товар {article}:\n\n")
        for i, fb in enumerate(feedbacks, 1):
            rating = int(fb.get('productValuation', 0))
            f.write(f"★ {'⭐' * rating}\n")  # Исправленная строка
            f.write(f"Дата: {fb.get('createdDate', 'не указана')}\n")
            f.write(f"Плюсы: {fb.get('pros', 'нет информации')}\n")
            f.write(f"Минусы: {fb.get('cons', 'нет информации')}\n")
            f.write(f"Отзыв: {fb.get('text', 'без комментария')}\n")
            f.write("-"*50 + "\n\n")

def main():
    article = input("Введите артикул товара с Wildberries: ")
    
    print("\n⌛ Получаем информацию о товаре...")
    
    # Добавляем задержку перед запросом
    time.sleep(1)
    
    product = get_product_info(article)
    if not product:
        print("\n❌ Товар не найден или доступ ограничен")
        print("Что можно сделать:")
        print("1. Проверьте артикул на сайте WB")
        print("2. Попробуйте другой артикул (например, 14976090)")
        print("3. Используйте VPN/прокси")
        with open('reviews.txt', 'w', encoding='utf-8') as f:
            f.write(f"Не удалось получить данные для артикула {article}\n")
        return
    
    print(f"✔ Найден товар: {product.get('name')}")
    print("⌛ Получаем отзывы...")
    
    feedbacks = get_feedbacks(product['id'])
    save_feedbacks(article, feedbacks)
    
    print(f"\n✅ Готово! Сохранено {len(feedbacks)} отзывов в файл 'reviews.txt'")
    print("Открываю файл с отзывами...")
    
    # Пытаемся открыть файл
    try:
        import os
        os.startfile('reviews.txt')
    except:
        print("Файл сохранен в текущей директории")

if __name__ == "__main__":
    main()
