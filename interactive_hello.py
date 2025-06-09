#!/usr/bin/env python3
"""
Интерактивный Hello World на Python
"""

import datetime
import random

def get_greeting_by_time():
    """Возвращает приветствие в зависимости от времени суток"""
    current_hour = datetime.datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 17:
        return "Добрый день"
    elif 17 <= current_hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def get_random_fact():
    """Возвращает случайный факт о Python"""
    facts = [
        "Python назван в честь британского комедийного шоу 'Monty Python's Flying Circus'",
        "Python был создан Гвидо ван Россумом в 1991 году",
        "Python используется в NASA, Google, Instagram, Spotify и многих других компаниях",
        "Zen of Python содержит 19 принципов дизайна языка",
        "Python поддерживает множественное наследование",
        "В Python все является объектом",
        "Python имеет автоматическое управление памятью",
        "Индентация в Python является частью синтаксиса"
    ]
    return random.choice(facts)

def calculate_age_in_days(birth_year):
    """Вычисляет возраст в днях"""
    current_year = datetime.datetime.now().year
    age_years = current_year - birth_year
    return age_years * 365  # Приблизительно

def main():
    print("🐍 Интерактивный Python Hello World! 🐍")
    print("=" * 50)
    
    # Приветствие по времени
    greeting = get_greeting_by_time()
    print(f"{greeting}!")
    
    # Запрос имени
    try:
        name = input("\nКак вас зовут? ").strip()
        if not name:
            name = "Друг"
        
        print(f"\nПривет, {name}! 👋")
        
        # Запрос года рождения
        birth_year_input = input("В каком году вы родились? (необязательно): ").strip()
        
        if birth_year_input.isdigit():
            birth_year = int(birth_year_input)
            current_year = datetime.datetime.now().year
            
            if 1900 <= birth_year <= current_year:
                age = current_year - birth_year
                days = calculate_age_in_days(birth_year)
                print(f"Вам примерно {age} лет ({days} дней)! 🎂")
            else:
                print("Интересный год рождения! 🤔")
        
        # Случайный факт о Python
        print(f"\n💡 Интересный факт о Python:")
        print(f"   {get_random_fact()}")
        
        # Простая математика
        print(f"\n🧮 Давайте посчитаем!")
        try:
            num1 = float(input("Введите первое число: "))
            num2 = float(input("Введите второе число: "))
            
            print(f"\nРезультаты:")
            print(f"  {num1} + {num2} = {num1 + num2}")
            print(f"  {num1} - {num2} = {num1 - num2}")
            print(f"  {num1} * {num2} = {num1 * num2}")
            
            if num2 != 0:
                print(f"  {num1} / {num2} = {num1 / num2:.2f}")
            else:
                print(f"  {num1} / {num2} = На ноль делить нельзя! 😅")
                
        except ValueError:
            print("Это не похоже на число, но ничего страшного! 😊")
        
        # Завершение
        print(f"\n🎉 Спасибо за общение, {name}!")
        print("Удачного дня и счастливого программирования на Python! 🚀")
        
    except KeyboardInterrupt:
        print("\n\n👋 До свидания! Увидимся в следующий раз!")
    except EOFError:
        print("\n\n👋 До свидания!")

if __name__ == "__main__":
    main()