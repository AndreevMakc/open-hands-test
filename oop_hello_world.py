#!/usr/bin/env python3
"""
Объектно-ориентированный Hello World на Python
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

class Greeter(ABC):
    """Абстрактный базовый класс для приветствий"""
    
    @abstractmethod
    def greet(self, name: str) -> str:
        """Абстрактный метод для приветствия"""
        pass

class SimpleGreeter(Greeter):
    """Простое приветствие"""
    
    def greet(self, name: str) -> str:
        return f"Привет, {name}!"

class FormalGreeter(Greeter):
    """Формальное приветствие"""
    
    def greet(self, name: str) -> str:
        return f"Здравствуйте, {name}!"

class TimeBasedGreeter(Greeter):
    """Приветствие в зависимости от времени"""
    
    def greet(self, name: str) -> str:
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_greeting = "Доброе утро"
        elif 12 <= hour < 17:
            time_greeting = "Добрый день"
        elif 17 <= hour < 22:
            time_greeting = "Добрый вечер"
        else:
            time_greeting = "Доброй ночи"
        
        return f"{time_greeting}, {name}!"

class Person:
    """Класс для представления человека"""
    
    def __init__(self, name: str, age: Optional[int] = None, language: str = "русский"):
        self.name = name
        self.age = age
        self.language = language
        self.greetings_received: List[str] = []
    
    def receive_greeting(self, greeting: str) -> None:
        """Получить приветствие"""
        self.greetings_received.append(greeting)
        print(f"👤 {self.name}: {greeting}")
    
    def introduce(self) -> str:
        """Представиться"""
        intro = f"Меня зовут {self.name}"
        if self.age:
            intro += f", мне {self.age} лет"
        intro += f", я говорю на {self.language} языке."
        return intro
    
    def get_greeting_count(self) -> int:
        """Получить количество полученных приветствий"""
        return len(self.greetings_received)

class HelloWorldApp:
    """Главное приложение Hello World"""
    
    def __init__(self):
        self.greeters = {
            "простое": SimpleGreeter(),
            "формальное": FormalGreeter(),
            "по времени": TimeBasedGreeter()
        }
        self.people: List[Person] = []
    
    def add_person(self, person: Person) -> None:
        """Добавить человека"""
        self.people.append(person)
        print(f"➕ Добавлен: {person.introduce()}")
    
    def greet_all(self, greeter_type: str = "простое") -> None:
        """Поприветствовать всех людей"""
        if greeter_type not in self.greeters:
            print(f"❌ Неизвестный тип приветствия: {greeter_type}")
            return
        
        greeter = self.greeters[greeter_type]
        print(f"\n🎯 Используем {greeter_type} приветствие:")
        
        for person in self.people:
            greeting = greeter.greet(person.name)
            person.receive_greeting(greeting)
    
    def show_statistics(self) -> None:
        """Показать статистику"""
        print(f"\n📊 Статистика:")
        print(f"   Всего людей: {len(self.people)}")
        
        for person in self.people:
            count = person.get_greeting_count()
            print(f"   {person.name}: получил {count} приветствий")
    
    def run_demo(self) -> None:
        """Запустить демонстрацию"""
        print("🐍 Объектно-ориентированный Hello World! 🐍")
        print("=" * 60)
        
        # Создаем людей
        people_data = [
            ("Анна", 25, "русский"),
            ("John", 30, "английский"),
            ("Marie", 28, "французский"),
            ("Python Developer", None, "Python")
        ]
        
        for name, age, language in people_data:
            person = Person(name, age, language)
            self.add_person(person)
        
        # Приветствуем разными способами
        for greeter_type in self.greeters.keys():
            self.greet_all(greeter_type)
        
        # Показываем статистику
        self.show_statistics()
        
        # Демонстрация полиморфизма
        print(f"\n🔄 Демонстрация полиморфизма:")
        test_name = "Мир"
        
        for name, greeter in self.greeters.items():
            greeting = greeter.greet(test_name)
            print(f"   {name.capitalize()}: {greeting}")

def main():
    """Главная функция"""
    app = HelloWorldApp()
    app.run_demo()
    
    print(f"\n🎉 Демонстрация завершена!")
    print("Это пример использования ООП в Python:")
    print("  • Абстрактные классы и наследование")
    print("  • Полиморфизм")
    print("  • Инкапсуляция")
    print("  • Композиция")
    print("  • Типизация (type hints)")

if __name__ == "__main__":
    main()