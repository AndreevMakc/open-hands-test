#!/usr/bin/env python3
"""
Функциональный Hello World на Python
Демонстрация функционального программирования
"""

from functools import reduce, partial
from itertools import chain, cycle, islice
from typing import Callable, List, Iterator, Any

# Чистые функции
def greet(name: str) -> str:
    """Чистая функция приветствия"""
    return f"Привет, {name}!"

def add_exclamation(text: str) -> str:
    """Добавить восклицательный знак"""
    return f"{text}!"

def make_uppercase(text: str) -> str:
    """Сделать заглавными буквами"""
    return text.upper()

def add_emoji(emoji: str) -> Callable[[str], str]:
    """Функция высшего порядка для добавления эмодзи"""
    def inner(text: str) -> str:
        return f"{emoji} {text} {emoji}"
    return inner

# Композиция функций
def compose(*functions):
    """Композиция функций"""
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

# Каррирование
def curry_greet(greeting: str) -> Callable[[str], str]:
    """Каррированная функция приветствия"""
    return lambda name: f"{greeting}, {name}!"

# Генераторы
def greeting_generator(names: List[str]) -> Iterator[str]:
    """Генератор приветствий"""
    for name in names:
        yield greet(name)

def infinite_hello() -> Iterator[str]:
    """Бесконечный генератор Hello"""
    greetings = ["Hello", "Привет", "Hola", "Bonjour", "Guten Tag"]
    return cycle(greetings)

# Функции высшего порядка
def apply_to_all(func: Callable[[str], str], items: List[str]) -> List[str]:
    """Применить функцию ко всем элементам"""
    return list(map(func, items))

def filter_long_names(names: List[str], min_length: int = 5) -> List[str]:
    """Отфильтровать длинные имена"""
    return list(filter(lambda name: len(name) >= min_length, names))

# Рекурсия
def factorial(n: int) -> int:
    """Рекурсивное вычисление факториала"""
    return 1 if n <= 1 else n * factorial(n - 1)

def fibonacci_sequence(n: int) -> List[int]:
    """Последовательность Фибоначчи через рекурсию"""
    def fib(x: int) -> int:
        return x if x <= 1 else fib(x - 1) + fib(x - 2)
    
    return [fib(i) for i in range(n)]

# Монады (упрощенная версия)
class Maybe:
    """Упрощенная монада Maybe"""
    
    def __init__(self, value: Any):
        self.value = value
    
    def bind(self, func: Callable) -> 'Maybe':
        """Монадическая операция bind"""
        if self.value is None:
            return Maybe(None)
        try:
            return Maybe(func(self.value))
        except:
            return Maybe(None)
    
    def __repr__(self) -> str:
        return f"Maybe({self.value})"

def safe_divide(x: float, y: float) -> float:
    """Безопасное деление"""
    if y == 0:
        raise ValueError("Division by zero")
    return x / y

def main():
    """Главная функция демонстрации"""
    print("🐍 Функциональный Python Hello World! 🐍")
    print("=" * 60)
    
    # Базовые функции
    names = ["Анна", "Боб", "Виктория", "Григорий", "Дарья"]
    print("👥 Имена:", names)
    
    # Простые приветствия
    print("\n🎯 Простые приветствия:")
    greetings = list(map(greet, names))
    for greeting in greetings:
        print(f"   {greeting}")
    
    # Композиция функций
    print("\n🔧 Композиция функций:")
    enhanced_greet = compose(
        add_emoji("🎉"),
        add_exclamation,
        greet
    )
    
    for name in names[:3]:
        result = enhanced_greet(name)
        print(f"   {result}")
    
    # Каррирование
    print("\n🍛 Каррированные функции:")
    morning_greet = curry_greet("Доброе утро")
    evening_greet = curry_greet("Добрый вечер")
    
    print(f"   {morning_greet('Мир')}")
    print(f"   {evening_greet('Python')}")
    
    # Функции высшего порядка
    print("\n⚡ Функции высшего порядка:")
    add_wave = add_emoji("👋")
    waving_greetings = apply_to_all(add_wave, greetings[:3])
    
    for greeting in waving_greetings:
        print(f"   {greeting}")
    
    # Фильтрация
    print("\n🔍 Фильтрация длинных имен:")
    long_names = filter_long_names(names)
    print(f"   Длинные имена: {long_names}")
    
    # Генераторы
    print("\n🔄 Генераторы:")
    greeting_gen = greeting_generator(names[:3])
    print("   Генератор приветствий:")
    for greeting in greeting_gen:
        print(f"     {greeting}")
    
    # Бесконечный генератор (ограниченный)
    print("\n♾️  Бесконечный генератор (первые 8):")
    infinite_gen = infinite_hello()
    limited_greetings = list(islice(infinite_gen, 8))
    print(f"   {limited_greetings}")
    
    # Рекурсия
    print("\n🔁 Рекурсивные функции:")
    print(f"   Факториал 5: {factorial(5)}")
    fib_seq = fibonacci_sequence(8)
    print(f"   Фибоначчи (8): {fib_seq}")
    
    # Монады
    print("\n🎭 Монады (Maybe):")
    maybe_value = Maybe(10)
    result = (maybe_value
              .bind(lambda x: x * 2)
              .bind(lambda x: x + 5)
              .bind(lambda x: safe_divide(x, 5)))
    print(f"   Maybe(10) -> *2 -> +5 -> /5 = {result}")
    
    # Безопасное деление на ноль
    maybe_zero = Maybe(10)
    result_zero = (maybe_zero
                   .bind(lambda x: safe_divide(x, 0))
                   .bind(lambda x: x + 100))
    print(f"   Maybe(10) -> /0 -> +100 = {result_zero}")
    
    # Функциональные операции со списками
    print("\n📊 Функциональные операции:")
    numbers = [1, 2, 3, 4, 5]
    
    # Map, filter, reduce
    squared = list(map(lambda x: x**2, numbers))
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    sum_all = reduce(lambda x, y: x + y, numbers)
    
    print(f"   Числа: {numbers}")
    print(f"   Квадраты: {squared}")
    print(f"   Четные: {evens}")
    print(f"   Сумма: {sum_all}")
    
    # Частичное применение
    print("\n🧩 Частичное применение:")
    multiply = lambda x, y: x * y
    double = partial(multiply, 2)
    triple = partial(multiply, 3)
    
    print(f"   double(5) = {double(5)}")
    print(f"   triple(4) = {triple(4)}")
    
    print("\n🎉 Функциональное программирование завершено!")
    print("Продемонстрированные концепции:")
    print("  • Чистые функции")
    print("  • Функции высшего порядка")
    print("  • Композиция функций")
    print("  • Каррирование")
    print("  • Генераторы")
    print("  • Рекурсия")
    print("  • Монады")
    print("  • Map, Filter, Reduce")
    print("  • Частичное применение")

if __name__ == "__main__":
    main()