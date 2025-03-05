#!/usr/bin/env python3
"""
Пример использования RagDict для хранения и поиска цен на автомобили.
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from ragdict import RagDict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def main():
    # Проверяем наличие API ключа OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Пожалуйста, установите переменную окружения OPENAI_API_KEY")
        print("Пример: export OPENAI_API_KEY='your-api-key'")
        return

    # Создаем словарь с ценами на автомобили
    print("Создание словаря с ценами на автомобили...")
    car_prices = RagDict(
        {
            "Toyota Camry": 25000,
            "Honda Accord": 27000,
            "Tesla Model 3": 40000,
            "Ford Mustang": 35000,
            "Chevrolet Corvette": 60000,
            "BMW X5": 65000,
            "Mercedes-Benz C-Class": 45000,
            "Audi A4": 42000,
            "Volkswagen Golf": 28000,
            "Hyundai Sonata": 24000
        },
        embedding_model="text-embedding-3-small",
        llm_model="gpt-3.5-turbo",
        similarity_threshold=0.65,
        top_k=3
    )
    
    print(f"Словарь создан с {len(car_prices)} моделями автомобилей")
    
    # Демонстрация точного поиска
    print("\n--- Точный поиск ---")
    exact_key = "Toyota Camry"
    try:
        price = car_prices[exact_key]
        print(f"Цена {exact_key}: ${price}")
    except KeyError:
        print(f"Ключ '{exact_key}' не найден")
    
    # Демонстрация нечеткого поиска
    print("\n--- Нечеткий поиск ---")
    fuzzy_examples = [
        "Toyot Camri",
        "Tesla Model Three",
        "Chevy Corvette",
        "Mercedes C Class",
        "BMW X-5",
        "VW Golf",
        "Hyundai Sonat"
    ]
    
    for query in fuzzy_examples:
        try:
            price = car_prices[query]
            print(f"Запрос: '{query}' -> Цена: ${price}")
        except KeyError:
            print(f"Ключ '{query}' не найден даже с нечетким поиском")
    
    # Демонстрация добавления нового ключа
    print("\n--- Добавление нового ключа ---")
    car_prices["Lexus RX"] = 55000
    print(f"Добавлен новый автомобиль: Lexus RX - ${car_prices['Lexus RX']}")
    
    # Проверка нечеткого поиска для нового ключа
    try:
        price = car_prices["Lexus R-X"]
        print(f"Запрос: 'Lexus R-X' -> Цена: ${price}")
    except KeyError:
        print(f"Ключ 'Lexus R-X' не найден даже с нечетким поиском")

if __name__ == "__main__":
    main() 