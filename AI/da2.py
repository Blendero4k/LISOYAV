import requests
import os
import time
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class YandexGPTSummarizer:
    def __init__(self, max_retries: int = 3):
        """Инициализация с автоматическими повторными попытками"""
        self.max_retries = max_retries
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self._validate_credentials()
        
        self.endpoint = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id
        }

    def _validate_credentials(self):
        """Проверка учетных данных"""
        if not self.api_key or not self.folder_id:
            raise ValueError("Требуются YANDEX_API_KEY и YANDEX_FOLDER_ID в .env")
        
        if len(self.folder_id) != 20 or not self.folder_id.startswith("b1g"):
            raise ValueError("Неверный формат folder_id. Должен начинаться с 'b1g' и содержать 20 символов")

    def _make_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Отправка запроса с повторными попытками"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                # Для отладки
                print(f"Попытка {attempt + 1}. Статус: {response.status_code}")
                
                if response.status_code == 500:
                    raise Exception("Сервер вернул 500 ошибку")
                
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                print(f"Ошибка запроса (попытка {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # Экспоненциальная задержка

    def create_summary(self, text: str) -> Optional[str]:
        """Создает краткую выжимку текста"""
        if not text.strip():
            return None

        payload = {
            "modelUri": "gpt://b1gs3e92fdalvnphqc47/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": 1000  # Уменьшенный лимит для стабильности
            },
            "messages": [
                {
                    "role": "system",
                    "text": (
                        "Ты - профессиональный редактор. Создай краткую выжимку текста.\n"
                        "Формат: один абзац (4-6 предложений).\n"
                        "Сохрани только ключевые мысли, избегай примеров."
                    )
                },
                {
                    "role": "user",
                    "text": f"Текст для обработки:\n\n{text[:5000]}"  # Ограничение длины
                }
            ]
        }

        result = self._make_request(payload)
        if result and 'result' in result:
            return result['result']['alternatives'][0]['message']['text'].strip()
        return None

    def process_file(self, file_path: str) -> str:
        """Обрабатывает файл и возвращает выжимку или сообщение об ошибке"""
        try:
            if not os.path.exists(file_path):
                return "Ошибка: файл не найден"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(5000).strip()  # Чтение первых 5000 символов
                
            if not content:
                return "Файл пуст"
                
            summary = self.create_summary(content)
            return summary if summary else "Не удалось создать выжимку (ошибка сервера)"
            
        except Exception as e:
            return f"Ошибка обработки: {str(e)}"


if __name__ == "__main__":
    try:
        summarizer = YandexGPTSummarizer(max_retries=5)
        
        # Конфигурация путей
        input_file = "reviews.txt"
        output_file = "summary.txt"
        
        print(f"Создание выжимки из файла {input_file}...")
        result = summarizer.process_file(input_file)
        
        print("\nРезультат:")
        print(result)
        
        if result and not result.startswith("Ошибка"):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\nСохранено в {output_file}")
            
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        print("\nРекомендации:")
        print("1. Проверьте баланс в Yandex Cloud Console")
        print("2. Убедитесь, что сервис YandexGPT активирован")
        print("3. Попробуйте другой folder_id или API-ключ")