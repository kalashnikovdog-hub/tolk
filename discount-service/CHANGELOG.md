# Changelog

Все значимые изменения в проекте Tolk Discount Service будут задокументированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версионирование следует [Semantic Versioning](https://semver.org/lang/ru/).

---

## [1.0.0] - 2024-12-XX

### Добавлено

#### Backend (FastAPI)
- **Приложение FastAPI** (`app/main.py`)
  - Создание основного приложения с роутингом
  - Lifespan менеджер для инициализации/закрытия соединений
  - Подключение CORS middleware
  - Регистрация exception handlers
  
- **Аутентификация и авторизация**
  - JWT токен аутентификация
  - Хеширование паролей bcrypt
  - Endpoints: register, login, me
  - Зависимость `get_current_user` для защиты роутов

- **CRUD операции**
  - Discounts: list, get, create, update, delete
  - Stores: list, get
  - Categories: list, get
  - Collections: user favorites
  - Users: profile management

- **Фильтрация и пагинация**
  - Фильтры для скидок (category, store, type, price range)
  - Пагинация с page/page_size
  - Сортировка по различным полям

- **CORS конфигурация**
  - Настройка разрешенных origin
  - Поддержка credentials
  - Exposure rate limit headers

#### Database (PostgreSQL + Alembic)
- **Модели данных**
  - User, Store, Category, Discount
  - Collection, FamilyCard, UserPreference
  - BankOffer, ScrapedSource
  - Many-to-many relationships

- **Alembic миграции**
  - Initial migration (`001_initial.py`)
  - Полная схема БД с индексами
  - Поддержка asyncpg

- **Индексы базы данных**
  - Primary keys на всех таблицах
  - Unique index на `users.email`
  - Unique index на `categories.slug`
  - Unique index на `family_cards.card_number`
  - Index на `discounts.external_id`
  - Index на `discounts.store_id`, `discounts.category_id`

#### Caching (Redis)
- **CacheManager** (`app/core/cache.py`)
  - Async Redis клиент
  - TTL управление
  - Методы для discount, store, user entities
  - Pattern-based invalidation
  - Cache-or-get helper

- **Интеграция в endpoints**
  - Кэширование списков скидок
  - Кэширование отдельных сущностей
  - Автоматическая инвалидация при изменениях

#### Security
- **Rate Limiting** (`app/core/middleware.py`)
  - Sliding window algorithm
  - Разные лимиты для auth (10/min) и API (100/min)
  - Блокировка по IP или user ID
  - HTTP заголовки X-RateLimit-*
  - Response 429 при превышении

- **Input Validation**
  - Pydantic v2 модели
  - Email валидация
  - Password strength требования
  - Query parameter валидация

- **Exception Handling** (`app/core/exceptions.py`)
  - Custom AppException классы
  - NotFoundException, ForbiddenException
  - RateLimitExceededException
  -统一 error response format

#### Web Scraping
- **Улучшенные пауки** (`scraper/scraper/spiders/`)
  - `base_spider.py` - общая логика
  - `grocery_spider.py` - парсинг ритейлеров
  - ImprovedGrocerySpider с расширенными возможностями

- **Retry Logic**
  - Tenacity библиотека
  - Экспоненциальная задержка (2-10 сек)
  - Retry при HTTP 5xx, 408, 429
  - Максимум 3-5 попыток

- **Proxy Rotation**
  - ProxyPool класс
  - Ротация при блокировках
  - Detekтирование captcha/blocks
  - Проверка валидности ответа

- **Парсинг ритейлеров**
  - Пятерочка (5ka.ru)
  - Перекресток (perekrestok.ru)
  - Магнит (magnit.ru)
  - Лента (lenta.com)

#### Testing
- **Integration Tests** (`app/tests/test_integration.py`)
  - pytest + httpx AsyncClient
  - In-memory SQLite для изоляции
  - Фикстуры для тестовых данных
  - Тесты health endpoints
  - Тесты auth flows (register, login)
  - Тесты discount CRUD
  - Тесты validation errors

- **Unit Tests**
  - `test_auth_service.py` - auth logic
  - `test_discount_service.py` - business logic

#### Configuration
- **Settings Management** (`app/config/settings.py`)
  - Pydantic Settings
  - Environment variables
  - Development vs Production режимы

- **Database Setup** (`app/config/database.py`)
  - Async engine создание
  - Session factory
  - Init/close функции

### Изменено

- Обновлена структура проекта
- Улучшена обработка ошибок
- Оптимизированы SQL запросы (joinedload)
- Улучшено логирование

### Исправлено

- Обработка отсутствующего Redis (graceful degradation)
- Валидация входных данных во всех endpoints
- Корректный shutdown при остановке приложения

### Удалено

- Устаревшие endpoints (если были)

---

## [0.2.0] - 2024-11-XX

### Добавлено

- Начальная версия скрапера
- Базовая схема базы данных
- Docker контейнеры

---

## [0.1.0] - 2024-10-XX

### Добавлено

- Initial project setup
- Basic FastAPI application structure
- Database models

---

## Типы изменений

- **Added** - новые функции
- **Changed** - изменения в существующем функционале
- **Deprecated** - скоро будет удалено
- **Removed** - удалено из проекта
- **Fixed** - исправления багов
- **Security** - улучшения безопасности

---

## Версии

- **v1.0.0** - Production релиз с полным функционалом
- **v0.2.0** - Beta версия с базовым функционалом
- **v0.1.0** - Alpha версия, initial setup
