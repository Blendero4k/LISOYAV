import pyodbc
import json
import os
from datetime import datetime

# 1. Настройки подключения
config = {
    'server': 'BASESRV\SQLEXPRESS',
    'database': 'basa40',
    'username': 'basa40',
    'password': 'basa40',
    'json_file': 'products.json',
    'table_name': 'Products'
}

# 2. Подключение к SQL Server
def connect_to_sql():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']}"
        )
        return conn
    except pyodbc.Error as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

# 3. Создание таблицы
def create_table(cursor):
    try:
        cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{config['table_name']}')
        CREATE TABLE {config['table_name']} (
            id INT PRIMARY KEY,
            article INT NOT NULL,
            nmID INT NOT NULL,
            name NVARCHAR(MAX) NOT NULL,
            brand NVARCHAR(MAX) NOT NULL,
            price INT NOT NULL,
            rating INT NOT NULL,
            feedback_count INT NOT NULL,
            feedbacks INT NOT NULL,
            created_at DATETIME DEFAULT GETDATE()
        )
        """)
        cursor.connection.commit()
        print(f"🔹 Таблица '{config['table_name']}' готова")
        return True
    except pyodbc.Error as e:
        print(f"❌ Ошибка создания таблицы: {e}")
        return False

# 4. Загрузка данных из JSON
def import_from_json(cursor):
    try:
        # Проверка существования файла
        if not os.path.exists(config['json_file']):
            raise FileNotFoundError(f"Файл {config['json_file']} не найден")
        
        # Чтение JSON
        with open(config['json_file'], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Вставка данных
        for item in data:
            cursor.execute(f"""
                INSERT INTO {config['table_name']} (
                    id, article, nmID, name, brand, 
                    price, rating, feedback_count, feedbacks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            item['id'],
            item['article'],
            item['nmID'],
            item['name'],
            item['brand'],
            item['price'],
            item['rating'],
            item['feedback_count'],
            item['feedback_count'])
        
        cursor.connection.commit()
        print(f"✅ Успешно загружено {len(data)} записей")
        return True
    
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка формата JSON: {e}")
    except KeyError as e:
        print(f"❌ Отсутствует обязательное поле: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    return False

# 5. Главная функция
def main():
    conn = connect_to_sql()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        if not create_table(cursor):
            return
        
        if import_from_json(cursor):
            print("🎉 Все операции завершены успешно!")
        
    finally:
        conn.close()
        print("🔹 Соединение закрыто")

if __name__ == "__main__":
    main()