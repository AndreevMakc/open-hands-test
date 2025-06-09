#!/usr/bin/env python3
"""
Hello World на Python

Этот файл демонстрирует базовые возможности Python и интеграцию с Product Catalog Service.
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any


def hello_world():
    """Простая функция Hello World"""
    print("Привет, мир! 🌍")
    print("Hello, World! 🐍")
    print(f"Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def demonstrate_python_features():
    """Демонстрация возможностей Python"""
    print("\n=== Демонстрация возможностей Python ===")
    
    # Работа со строками
    name = "Python"
    version = sys.version_info
    print(f"Язык: {name}")
    print(f"Версия: {version.major}.{version.minor}.{version.micro}")
    
    # Работа со списками и словарями
    languages = ["Python", "JavaScript", "Go", "Rust"]
    print(f"Популярные языки: {', '.join(languages)}")
    
    # Словарь с информацией о проекте
    project_info = {
        "name": "Product Catalog Service",
        "architecture": "Clean Architecture",
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "cache": "Redis",
        "features": [
            "Hierarchical categories",
            "Configurable attributes", 
            "Full CRUD operations",
            "Search and filtering",
            "RESTful API"
        ]
    }
    
    print(f"\nИнформация о проекте:")
    for key, value in project_info.items():
        if isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")


def fibonacci(n: int) -> List[int]:
    """Генерация последовательности Фибоначчи"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib


def demonstrate_algorithms():
    """Демонстрация алгоритмов"""
    print("\n=== Демонстрация алгоритмов ===")
    
    # Последовательность Фибоначчи
    fib_sequence = fibonacci(10)
    print(f"Первые 10 чисел Фибоначчи: {fib_sequence}")
    
    # Сортировка списка
    numbers = [64, 34, 25, 12, 22, 11, 90]
    print(f"Исходный список: {numbers}")
    sorted_numbers = sorted(numbers)
    print(f"Отсортированный список: {sorted_numbers}")
    
    # Работа с множествами
    set1 = {1, 2, 3, 4, 5}
    set2 = {4, 5, 6, 7, 8}
    print(f"Множество 1: {set1}")
    print(f"Множество 2: {set2}")
    print(f"Пересечение: {set1 & set2}")
    print(f"Объединение: {set1 | set2}")


class ProductCatalogDemo:
    """Демонстрационный класс для работы с каталогом товаров"""
    
    def __init__(self):
        self.categories = []
        self.products = []
    
    def add_category(self, name: str, slug: str, description: str = None):
        """Добавить категорию"""
        category = {
            "id": len(self.categories) + 1,
            "name": name,
            "slug": slug,
            "description": description,
            "created_at": datetime.now()
        }
        self.categories.append(category)
        return category
    
    def add_product(self, name: str, price: float, category_id: int):
        """Добавить товар"""
        product = {
            "id": len(self.products) + 1,
            "name": name,
            "price": price,
            "category_id": category_id,
            "created_at": datetime.now()
        }
        self.products.append(product)
        return product
    
    def get_products_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Получить товары по категории"""
        return [p for p in self.products if p["category_id"] == category_id]
    
    def display_catalog(self):
        """Отобразить каталог"""
        print("\n=== Демонстрационный каталог товаров ===")
        
        for category in self.categories:
            print(f"\nКатегория: {category['name']} ({category['slug']})")
            if category['description']:
                print(f"  Описание: {category['description']}")
            
            products = self.get_products_by_category(category['id'])
            if products:
                print("  Товары:")
                for product in products:
                    print(f"    - {product['name']}: {product['price']} руб.")
            else:
                print("  Товары отсутствуют")


async def async_demo():
    """Демонстрация асинхронного программирования"""
    print("\n=== Демонстрация асинхронного программирования ===")
    
    async def fetch_data(name: str, delay: float) -> str:
        """Имитация асинхронного запроса данных"""
        print(f"Начинаем загрузку {name}...")
        await asyncio.sleep(delay)
        print(f"Загрузка {name} завершена!")
        return f"Данные {name}"
    
    # Параллельное выполнение задач
    tasks = [
        fetch_data("категорий", 1.0),
        fetch_data("товаров", 1.5),
        fetch_data("атрибутов", 0.8)
    ]
    
    results = await asyncio.gather(*tasks)
    print(f"Результаты: {results}")


def main():
    """Главная функция"""
    print("🐍 Python Hello World Demo 🐍")
    print("=" * 50)
    
    # Базовый Hello World
    hello_world()
    
    # Демонстрация возможностей Python
    demonstrate_python_features()
    
    # Демонстрация алгоритмов
    demonstrate_algorithms()
    
    # Демонстрация ООП
    catalog = ProductCatalogDemo()
    
    # Добавляем категории
    electronics = catalog.add_category("Электроника", "electronics", "Электронные устройства")
    books = catalog.add_category("Книги", "books", "Печатные и электронные книги")
    
    # Добавляем товары
    catalog.add_product("Смартфон iPhone", 99999.99, electronics["id"])
    catalog.add_product("Ноутбук MacBook", 199999.99, electronics["id"])
    catalog.add_product("Python для начинающих", 1500.00, books["id"])
    catalog.add_product("Clean Architecture", 2500.00, books["id"])
    
    # Отображаем каталог
    catalog.display_catalog()
    
    # Асинхронная демонстрация
    print("\nЗапуск асинхронной демонстрации...")
    asyncio.run(async_demo())
    
    print("\n" + "=" * 50)
    print("🎉 Демонстрация завершена! 🎉")
    print("\nДля запуска Product Catalog Service используйте:")
    print("  python -m uvicorn src.main:app --reload")
    print("\nДокументация API будет доступна по адресу:")
    print("  http://localhost:8000/api/v1/docs")


if __name__ == "__main__":
    main()