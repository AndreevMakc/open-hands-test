# Stage 3 Implementation Plan: Products, Attributes & Caching

## 🎯 **Цели Stage 3**

Реализовать полнофункциональную систему управления товарами с характеристиками, кешированием и расширенным поиском.

## 📋 **Задачи для реализации**

### 1. **Product API Endpoints** (Приоритет: Высокий)
- [ ] `POST /api/v1/products/` - Создание товара
- [ ] `GET /api/v1/products/` - Список товаров с фильтрацией
- [ ] `GET /api/v1/products/{id}` - Получение товара по ID
- [ ] `PUT /api/v1/products/{id}` - Обновление товара
- [ ] `DELETE /api/v1/products/{id}` - Удаление товара
- [ ] `GET /api/v1/products/search` - Расширенный поиск

### 2. **Attribute Management** (Приоритет: Высокий)
- [ ] `POST /api/v1/attributes/` - Создание характеристики
- [ ] `GET /api/v1/attributes/` - Список характеристик
- [ ] `GET /api/v1/attributes/{id}` - Получение характеристики
- [ ] `PUT /api/v1/attributes/{id}` - Обновление характеристики
- [ ] `DELETE /api/v1/attributes/{id}` - Удаление характеристики
- [ ] `POST /api/v1/categories/{id}/attributes` - Привязка к категории

### 3. **Product-Attribute Values** (Приоритет: Высокий)
- [ ] `POST /api/v1/products/{id}/attributes` - Установка значений
- [ ] `GET /api/v1/products/{id}/attributes` - Получение значений
- [ ] `PUT /api/v1/products/{id}/attributes/{attr_id}` - Обновление значения
- [ ] `DELETE /api/v1/products/{id}/attributes/{attr_id}` - Удаление значения

### 4. **Redis Caching Layer** (Приоритет: Средний)
- [ ] Настройка Redis подключения
- [ ] Кеширование категорий
- [ ] Кеширование товаров
- [ ] Кеширование результатов поиска
- [ ] Инвалидация кеша при изменениях

### 5. **Advanced Search & Filtering** (Приоритет: Средний)
- [ ] Поиск по названию и описанию
- [ ] Фильтрация по категориям
- [ ] Фильтрация по характеристикам
- [ ] Фильтрация по цене
- [ ] Сортировка результатов
- [ ] Пагинация с курсорами

### 6. **Enhanced Use Cases** (Приоритет: Средний)
- [ ] ProductUseCases с бизнес-логикой
- [ ] AttributeUseCases для управления характеристиками
- [ ] SearchUseCases для поиска и фильтрации
- [ ] CacheUseCases для управления кешем

### 7. **Data Validation & Business Rules** (Приоритет: Низкий)
- [ ] Валидация значений характеристик по типам
- [ ] Проверка обязательных характеристик
- [ ] Валидация единиц измерения
- [ ] Бизнес-правила для товаров

## 🏗️ **Архитектурные компоненты**

### **Application Layer**
```
src/application/
├── use_cases/
│   ├── product_use_cases.py
│   ├── attribute_use_cases.py
│   ├── search_use_cases.py
│   └── cache_use_cases.py
├── dtos/
│   ├── product_dto.py
│   ├── attribute_dto.py
│   └── search_dto.py
└── services/
    ├── search_service.py
    └── cache_service.py
```

### **Infrastructure Layer**
```
src/infrastructure/
├── cache/
│   ├── redis_client.py
│   └── cache_repository.py
├── repositories/
│   ├── attribute_repository.py
│   └── product_attribute_repository.py
└── services/
    └── search_service_impl.py
```

### **Presentation Layer**
```
src/presentation/api/v1/
├── products.py
├── attributes.py
└── search.py
```

## 🔧 **Технические детали**

### **Новые зависимости**
```
redis==5.0.1
redis-py-cluster==2.1.3
elasticsearch==8.11.1  # опционально для расширенного поиска
```

### **Redis Schema**
```
categories:{id} -> CategoryData
products:{id} -> ProductData
search:{query_hash} -> SearchResults
category_products:{category_id} -> List[ProductId]
```

### **Search Capabilities**
- Full-text search по названию и описанию
- Фильтрация по множественным критериям
- Агрегация по характеристикам
- Автокомплит для поиска

## 📊 **Метрики успеха**

- [ ] Все API endpoints работают корректно
- [ ] Время ответа API < 200ms (с кешем)
- [ ] Поиск работает по всем типам характеристик
- [ ] Кеш инвалидируется корректно
- [ ] 100% покрытие тестами новой функциональности

## 🚀 **План выполнения**

### **Week 1: Core Product API**
1. Product DTOs и Use Cases
2. Product API endpoints
3. Product-Attribute relationships

### **Week 2: Attributes & Search**
1. Attribute management API
2. Advanced search implementation
3. Redis caching layer

### **Week 3: Integration & Testing**
1. Integration testing
2. Performance optimization
3. Documentation updates

## 🔗 **Связь с предыдущими этапами**

- **Stage 1**: Использует доменные модели и архитектуру
- **Stage 2**: Расширяет существующие репозитории и API
- **Stage 3**: Добавляет продукты, характеристики и кеширование