from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def parse_wildberries_reviews(article_number, output_file='reviews.txt'):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(executable_path='chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        url = f"https://www.wildberries.ru/catalog/{article_number}/detail.aspx"
        driver.get(url)
        time.sleep(3)
        try:
            reviews_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-link='html{product^reviews}']"))
            )
            reviews_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Не удалось найти кнопку отзывов: {e}")
            return
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)
        reviews = []
        review_elements = driver.find_elements(By.CSS_SELECTOR, "div.feedback__item")[:10]
        for i, review in enumerate(review_elements, 1):
            try:
                author = review.find_element(By.CSS_SELECTOR, "span.feedback__name").text.strip()
                date = review.find_element(By.CSS_SELECTOR, "span.feedback__date").text.strip()
                text_element = review.find_element(By.CSS_SELECTOR, "p.feedback__text")
                text = text_element.text.strip()
                rating = len(review.find_elements(By.CSS_SELECTOR, "span.feedback__star.feedback__star--active"))
                reviews.append(f"Отзыв {i}:\nАвтор: {author}\nДата: {date}\nРейтинг: {rating}/5\nТекст: {text}\n")
            except Exception as e:
                print(f"Ошибка при парсинге отзыва {i}: {e}")
                continue
        with open(output_file, 'w', encoding='utf-8') as f:
            if reviews:
                f.write(f"Отзывы на товар с артикулом {article_number}:\n\n")
                f.write("\n".join(reviews))
                print(f"Успешно сохранено {len(reviews)} отзывов в файл {output_file}")
            else:
                f.write("Не удалось найти отзывы для данного товара.")
                print("Не удалось найти отзывы для данного товара.")
                
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    article = input("Введите артикул товара с Wildberries: ")
    parse_wildberries_reviews(article)
