#!/usr/bin/env python3
"""
Простой Hello World на Python
"""

def main():
    print("Привет, мир! 🌍")
    print("Hello, World! 🐍")
    
    # Демонстрация основных возможностей Python
    name = "Python"
    version = "3.12"
    
    print(f"Язык программирования: {name}")
    print(f"Версия: {version}")
    
    # Простые вычисления
    numbers = [1, 2, 3, 4, 5]
    sum_numbers = sum(numbers)
    print(f"Сумма чисел {numbers} = {sum_numbers}")
    
    # Работа со строками
    message = "Python - отличный язык программирования!"
    print(f"Сообщение: {message}")
    print(f"Длина сообщения: {len(message)} символов")
    
    # Простой цикл
    print("\nСчет от 1 до 5:")
    for i in range(1, 6):
        print(f"  {i}")
    
    # Словарь
    info = {
        "язык": "Python",
        "создатель": "Guido van Rossum",
        "год": 1991,
        "популярность": "очень высокая"
    }
    
    print("\nИнформация о Python:")
    for key, value in info.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()