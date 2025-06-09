#!/usr/bin/env python3
"""
Асинхронный Hello World на Python
Демонстрация asyncio и асинхронного программирования
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import random

async def simple_greeting(name: str, delay: float = 1.0) -> str:
    """Простое асинхронное приветствие с задержкой"""
    print(f"🔄 Начинаем приветствие для {name}...")
    await asyncio.sleep(delay)
    greeting = f"Привет, {name}! 👋"
    print(f"✅ Завершено приветствие для {name}")
    return greeting

async def fetch_greeting_from_api(name: str) -> str:
    """Имитация получения приветствия из API"""
    # Имитируем API запрос
    await asyncio.sleep(random.uniform(0.5, 2.0))
    greetings = [
        f"Hello, {name}! 🌍",
        f"Bonjour, {name}! 🇫🇷", 
        f"Hola, {name}! 🇪🇸",
        f"Guten Tag, {name}! 🇩🇪",
        f"Konnichiwa, {name}! 🇯🇵"
    ]
    return random.choice(greetings)

async def process_user_data(user_id: int) -> Dict[str, Any]:
    """Асинхронная обработка данных пользователя"""
    print(f"📊 Обрабатываем данные пользователя {user_id}...")
    
    # Имитируем различные асинхронные операции
    tasks = [
        fetch_user_profile(user_id),
        fetch_user_preferences(user_id),
        fetch_user_activity(user_id)
    ]
    
    profile, preferences, activity = await asyncio.gather(*tasks)
    
    result = {
        "user_id": user_id,
        "profile": profile,
        "preferences": preferences,
        "activity": activity,
        "processed_at": time.time()
    }
    
    print(f"✅ Данные пользователя {user_id} обработаны")
    return result

async def fetch_user_profile(user_id: int) -> Dict[str, str]:
    """Получить профиль пользователя"""
    await asyncio.sleep(0.5)
    return {
        "name": f"User_{user_id}",
        "email": f"user{user_id}@example.com",
        "status": "active"
    }

async def fetch_user_preferences(user_id: int) -> Dict[str, Any]:
    """Получить предпочтения пользователя"""
    await asyncio.sleep(0.3)
    return {
        "language": random.choice(["ru", "en", "fr", "es"]),
        "theme": random.choice(["light", "dark"]),
        "notifications": random.choice([True, False])
    }

async def fetch_user_activity(user_id: int) -> Dict[str, int]:
    """Получить активность пользователя"""
    await asyncio.sleep(0.7)
    return {
        "login_count": random.randint(1, 100),
        "messages_sent": random.randint(0, 50),
        "last_seen_days_ago": random.randint(0, 30)
    }

async def greeting_producer(queue: asyncio.Queue, names: List[str]):
    """Производитель приветствий"""
    print("🏭 Запускаем производителя приветствий...")
    
    for name in names:
        greeting = await fetch_greeting_from_api(name)
        await queue.put(greeting)
        print(f"📤 Добавлено в очередь: {greeting}")
        await asyncio.sleep(0.1)
    
    # Сигнал завершения
    await queue.put(None)
    print("🏁 Производитель завершил работу")

async def greeting_consumer(queue: asyncio.Queue, consumer_id: int):
    """Потребитель приветствий"""
    print(f"🛒 Запускаем потребителя {consumer_id}...")
    processed = 0
    
    while True:
        greeting = await queue.get()
        
        if greeting is None:
            # Возвращаем сигнал завершения в очередь для других потребителей
            await queue.put(None)
            break
        
        # Обрабатываем приветствие
        await asyncio.sleep(0.2)
        print(f"🔄 Потребитель {consumer_id} обработал: {greeting}")
        processed += 1
        
        queue.task_done()
    
    print(f"✅ Потребитель {consumer_id} завершил работу. Обработано: {processed}")

def cpu_intensive_task(n: int) -> int:
    """CPU-интенсивная задача для демонстрации ThreadPoolExecutor"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

async def run_cpu_tasks_async(numbers: List[int]) -> List[int]:
    """Запуск CPU-интенсивных задач асинхронно"""
    print("🖥️  Запускаем CPU-интенсивные задачи...")
    
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        tasks = [
            loop.run_in_executor(executor, cpu_intensive_task, n)
            for n in numbers
        ]
        
        results = await asyncio.gather(*tasks)
    
    print("✅ CPU-интенсивные задачи завершены")
    return results

class AsyncGreetingService:
    """Асинхронный сервис приветствий"""
    
    def __init__(self):
        self.greeting_cache = {}
        self.request_count = 0
    
    async def get_greeting(self, name: str, language: str = "ru") -> str:
        """Получить приветствие с кэшированием"""
        self.request_count += 1
        cache_key = f"{name}_{language}"
        
        if cache_key in self.greeting_cache:
            print(f"💾 Кэш попадание для {cache_key}")
            return self.greeting_cache[cache_key]
        
        print(f"🌐 Генерируем новое приветствие для {cache_key}")
        
        # Имитируем асинхронную генерацию приветствия
        await asyncio.sleep(0.5)
        
        greetings = {
            "ru": f"Привет, {name}! 🇷🇺",
            "en": f"Hello, {name}! 🇺🇸",
            "fr": f"Bonjour, {name}! 🇫🇷",
            "es": f"Hola, {name}! 🇪🇸"
        }
        
        greeting = greetings.get(language, greetings["en"])
        self.greeting_cache[cache_key] = greeting
        
        return greeting
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику сервиса"""
        return {
            "total_requests": self.request_count,
            "cache_size": len(self.greeting_cache),
            "cached_greetings": list(self.greeting_cache.keys())
        }

async def main():
    """Главная асинхронная функция"""
    print("🐍 Асинхронный Python Hello World! 🐍")
    print("=" * 60)
    
    # 1. Простые асинхронные приветствия
    print("\n1️⃣ Простые асинхронные приветствия:")
    names = ["Анна", "Боб", "Виктория"]
    
    start_time = time.time()
    
    # Последовательное выполнение
    print("   📝 Последовательное выполнение:")
    for name in names:
        greeting = await simple_greeting(name, 0.5)
        print(f"     {greeting}")
    
    sequential_time = time.time() - start_time
    
    # Параллельное выполнение
    print("\n   ⚡ Параллельное выполнение:")
    start_time = time.time()
    
    tasks = [simple_greeting(name, 0.5) for name in names]
    greetings = await asyncio.gather(*tasks)
    
    for greeting in greetings:
        print(f"     {greeting}")
    
    parallel_time = time.time() - start_time
    
    print(f"\n   ⏱️  Время последовательно: {sequential_time:.2f}с")
    print(f"   ⏱️  Время параллельно: {parallel_time:.2f}с")
    print(f"   🚀 Ускорение: {sequential_time/parallel_time:.2f}x")
    
    # 2. Обработка данных пользователей
    print("\n2️⃣ Асинхронная обработка данных пользователей:")
    user_ids = [1, 2, 3, 4, 5]
    
    start_time = time.time()
    user_data_tasks = [process_user_data(uid) for uid in user_ids]
    user_data_results = await asyncio.gather(*user_data_tasks)
    processing_time = time.time() - start_time
    
    print(f"   ✅ Обработано {len(user_data_results)} пользователей за {processing_time:.2f}с")
    
    # 3. Producer-Consumer паттерн
    print("\n3️⃣ Producer-Consumer с очередью:")
    queue = asyncio.Queue(maxsize=5)
    producer_names = ["Alice", "Bob", "Charlie", "Diana"]
    
    # Запускаем производителя и потребителей
    producer_task = asyncio.create_task(
        greeting_producer(queue, producer_names)
    )
    
    consumer_tasks = [
        asyncio.create_task(greeting_consumer(queue, i))
        for i in range(2)
    ]
    
    # Ждем завершения всех задач
    await producer_task
    await asyncio.gather(*consumer_tasks)
    
    # 4. CPU-интенсивные задачи
    print("\n4️⃣ CPU-интенсивные задачи с ThreadPoolExecutor:")
    numbers = [100000, 200000, 150000, 300000]
    
    start_time = time.time()
    results = await run_cpu_tasks_async(numbers)
    cpu_time = time.time() - start_time
    
    print(f"   📊 Результаты: {results}")
    print(f"   ⏱️  Время выполнения: {cpu_time:.2f}с")
    
    # 5. Асинхронный сервис
    print("\n5️⃣ Асинхронный сервис приветствий:")
    service = AsyncGreetingService()
    
    # Тестируем сервис
    test_requests = [
        ("Анна", "ru"),
        ("John", "en"),
        ("Marie", "fr"),
        ("Анна", "ru"),  # Повторный запрос для демонстрации кэша
        ("Carlos", "es")
    ]
    
    for name, lang in test_requests:
        greeting = await service.get_greeting(name, lang)
        print(f"   {greeting}")
    
    # Статистика сервиса
    stats = await service.get_stats()
    print(f"\n   📈 Статистика сервиса:")
    print(f"     Всего запросов: {stats['total_requests']}")
    print(f"     Размер кэша: {stats['cache_size']}")
    print(f"     Кэшированные приветствия: {stats['cached_greetings']}")
    
    print("\n🎉 Асинхронная демонстрация завершена!")
    print("Продемонстрированные концепции:")
    print("  • async/await синтаксис")
    print("  • asyncio.gather() для параллельного выполнения")
    print("  • asyncio.Queue для Producer-Consumer")
    print("  • ThreadPoolExecutor для CPU-интенсивных задач")
    print("  • Асинхронные классы и методы")
    print("  • Кэширование в асинхронном контексте")

if __name__ == "__main__":
    asyncio.run(main())