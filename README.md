# Product Catalog Service

Сервис каталога товаров с конфигурируемыми характеристиками, построенный на Clean Architecture.

## Особенности

- 🏗️ **Clean Architecture** - четкое разделение слоев
- 🚀 **FastAPI** - современный, быстрый веб-фреймворк
- 🗄️ **PostgreSQL** - надежная реляционная база данных
- ⚡ **Redis** - кеширование для высокой производительности
- 🐳 **Docker** - простое развертывание
- 📊 **Иерархические категории** - поддержка LTREE
- 🔧 **Конфигурируемые характеристики** - гибкая система атрибутов
- 🔍 **Полнотекстовый поиск** - быстрый поиск товаров
- 📝 **Автоматическая документация** - OpenAPI/Swagger

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для разработки)

### Запуск с Docker

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd product-catalog
```

2. Запустите сервисы:
```bash
docker-compose up -d
```

3. Проверьте работу:
```bash
curl http://localhost:12000/health
```

4. Откройте документацию API:
- Swagger UI: http://localhost:12000/api/v1/docs
- ReDoc: http://localhost:12000/api/v1/redoc

### Разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите базу данных и Redis:
```bash
docker-compose up -d postgres redis
```

3. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл
```

4. Запустите приложение:
```bash
python -m src.main
```

## Архитектура

Проект следует принципам Clean Architecture:

```
src/
├── domain/              # Бизнес-логика
│   ├── entities/        # Сущности
│   ├── value_objects/   # Объекты-значения
│   ├── repositories/    # Интерфейсы репозиториев
│   └── services/        # Доменные сервисы
├── application/         # Слой приложения
│   ├── use_cases/       # Варианты использования
│   ├── dto/             # Объекты передачи данных
│   └── interfaces/      # Интерфейсы
├── infrastructure/      # Инфраструктура
│   ├── database/        # Реализация БД
│   ├── cache/           # Кеширование
│   ├── external/        # Внешние сервисы
│   └── config/          # Конфигурация
└── presentation/        # Слой представления
    ├── api/             # API endpoints
    ├── schemas/         # Pydantic схемы
    └── dependencies/    # FastAPI зависимости
```

## API Endpoints

### Категории
- `GET /api/v1/categories` - Список категорий
- `GET /api/v1/categories/tree` - Дерево категорий
- `GET /api/v1/categories/{id}` - Детали категории
- `POST /api/v1/categories` - Создание категории
- `PUT /api/v1/categories/{id}` - Обновление категории
- `DELETE /api/v1/categories/{id}` - Удаление категории

### Товары
- `GET /api/v1/products` - Список товаров с фильтрацией
- `GET /api/v1/products/search` - Поиск товаров
- `GET /api/v1/products/{id}` - Детали товара
- `POST /api/v1/products` - Создание товара
- `PUT /api/v1/products/{id}` - Обновление товара
- `DELETE /api/v1/products/{id}` - Удаление товара

### Характеристики
- `GET /api/v1/attributes` - Список характеристик
- `POST /api/v1/attributes` - Создание характеристики
- `GET /api/v1/categories/{id}/attributes` - Характеристики категории

## Конфигурация

Основные настройки через переменные окружения:

```env
# База данных
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/catalog

# Redis
REDIS_URL=redis://localhost:6379

# Безопасность
SECRET_KEY=your-secret-key
AUTH_ENABLED=true

# Кеширование
CACHE_TTL_CATEGORIES=3600
CACHE_TTL_PRODUCTS=900
```

## Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src --cov-report=html

# Запуск конкретного типа тестов
pytest -m unit
pytest -m integration
```

## Разработка

### Форматирование кода
```bash
black src/
isort src/
flake8 src/
```

### Проверка типов
```bash
mypy src/
```

### Pre-commit hooks
```bash
pre-commit install
pre-commit run --all-files
```

## Мониторинг

- Health check: `GET /health`
- Metrics: `GET /metrics` (если включен Prometheus)
- Logs: структурированные JSON логи

## Производительность

- Кеширование результатов в Redis
- Индексы БД для быстрого поиска
- Пагинация для больших списков
- Асинхронная обработка запросов

## Безопасность

- JWT аутентификация
- Валидация входных данных
- SQL injection защита
- Rate limiting
- CORS настройки

## Лицензия

MIT License

## Поддержка

Для вопросов и предложений создавайте issues в репозитории.