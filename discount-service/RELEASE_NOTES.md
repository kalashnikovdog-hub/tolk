# Tolk Discount Service - Release Notes v1.0.0

**Дата релиза:** Декабрь 2024  
**Версия:** 1.0.0  
**Статус:** Production Ready

---

## 🎉 Обзор релиза

Tolk Discount Service v1.0.0 - это полноценная платформа для управления и распространения скидок от различных ритейлеров. Платформа включает в себя REST API бэкенд на FastAPI, автоматический скрапинг акций из магазинов, систему аутентификации пользователей и кэширование для высокой производительности.

### Ключевые возможности

- 🔐 **Безопасная аутентификация** - JWT токены, хеширование паролей bcrypt
- 🛍️ **Каталог скидок** - Агрегация акций из Пятерочка, Перекресток, Магнит, Лента
- ⚡ **Высокая производительность** - Redis кэширование популярных запросов
- 🛡️ **Защита от атак** - Rate limiting для предотвращения brute-force
- 🔄 **Автоматический скрапинг** - Парсинг сайтов магазинов с retry logic и proxy rotation
- 📊 **База данных** - PostgreSQL с оптимизированными индексами
- 🧪 **Тестирование** - Интеграционные тесты для API endpoints

---

## ✨ Новые функции

### Backend (FastAPI)

#### Authentication & Authorization
- Регистрация новых пользователей с валидацией email
- Login с выдачей JWT access токенов
- Защита эндпоинтов через зависимости FastAPI
- Хеширование паролей алгоритмом bcrypt

#### Discounts Management
- CRUD операции для скидок
- Фильтрация по категориям, магазинам, типу скидки
- Пагинация результатов (page/page_size)
- Сортировка по различным полям
- Подсчет просмотров и кликов

#### Stores & Categories
- Каталог магазинов с типами (grocery, electronics, etc.)
- Иерархия категорий с поддержкой подкатегорий
- Связь магазинов с категориями

#### User Features
- Пользовательские подборки скидок (collections)
- Семейные карты скидок (family cards)
- Предпочтения пользователей для рекомендаций

### Caching System

#### Redis Integration
- Async Redis клиент для неблокирующих операций
- CacheManager с методами для различных сущностей
- Автоматическое кэширование списков скидок
- Инвалидация кэша при обновлении данных
- TTL настройка для разных типов данных

#### Cache Strategies
- Cache-aside pattern для популярных запросов
- Кэширование по ключам с префиксами
- Массовая инвалидация по паттернам

### Security

#### Rate Limiting
- Middleware для всех входящих запросов
- Разные лимиты для auth endpoints (10/мин) и обычных (100/мин)
- Скользящее окно (sliding window) для точного подсчета
- HTTP заголовки X-RateLimit-* для клиентов
- Блокировка по IP или user ID

#### Input Validation
- Pydantic модели для всех request/response
- Валидация email через email-validator
- Проверка сложности пароля (минимум 8 символов)
- Sanitization входных данных

### Web Scraping

#### Improved Spider Architecture
- BaseSpider с общими утилитами парсинга
- ImprovedGrocerySpider с расширенными возможностями
- Поддержка 4 крупных ритейлеров РФ

#### Retry Logic
- Tenacity библиотека для автоматических retries
- Экспоненциальная задержка между попытками (2-10 сек)
- Retry при HTTP ошибках 500, 502, 503, 504, 408, 429
- Обработка IgnoreRequest исключений

#### Proxy Rotation
- ProxyPool класс для управления пулом прокси
- Ротация прокси при блокировках
- Детектирование captcha и блоков
- Проверка валидности ответа

#### Data Extraction
- Парсинг названий, цен, процентов скидок
- Извлечение изображений товаров
- Определение дат начала/окончания акций
- Нормализация данных к единому формату

### Database

#### Schema Design
- 12 таблиц с отношениями один-ко-многим и многие-ко-многим
- Enum типы для статусов и категорий
- Audit поля (created_at, updated_at)

#### Indexes
- Индексы на primary keys (автоматически)
- Уникальные индексы на email, slug, card_number
- Составные индексы для частых запросов
- Индекс на external_id для скрапированных данных

#### Migrations
- Alembic для версионирования схемы БД
- Initial migration с полной схемой
- Поддержка asyncpg driver

### Testing

#### Integration Tests
- pytest + httpx AsyncClient для тестирования API
- In-memory SQLite база для изоляции тестов
- Фикстуры для тестовых данных (user, store, discount)
- Тесты health checks, auth, discounts, stores, categories
- Валидация error responses (422, 404, 409, 401)

#### Test Coverage
- Auth endpoints (register, login, duplicate email)
- Discount CRUD и фильтрация
- Store и Category listing
- Input validation (invalid email, short password, pagination)

---

## 🔧 Технические улучшения

### Производительность
- Async/await throughout the codebase
- Connection pooling для PostgreSQL
- Redis connection reuse
- Оптимизированные SQL запросы с joinedload

### Надежность
- Graceful shutdown при остановке приложения
- Обработка ошибок Redis (fallback без кэша)
- Логирование всех критических событий
- Tracking failed URLs в скрапере

### DevOps
- Docker контейнеры для backend и scraper
- Docker Compose для локальной разработки
- Environment variables конфигурация
- Health check endpoints

---

## 📦 Зависимости

### Backend
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
psycopg2-binary>=2.9.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.1.0
email-validator>=2.1.0
redis>=5.0.0
alembic>=1.13.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
```

### Scraper
```
scrapy>=2.11.0
tenacity>=8.2.0
```

---

## 🚀 Как запустить

### Backend
```bash
cd discount-service/backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Scraper
```bash
cd discount-service/scraper
pip install -r requirements.txt
scrapy crawl improved_grocery_spider
```

### Docker Compose
```bash
cd discount-service
docker-compose up -d
```

---

## 📝 API Documentation

После запуска сервера документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 🔗 Endpoints Overview

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/health/` | Проверка здоровья сервиса |
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Аутентификация |
| GET | `/api/discounts/` | Список скидок с фильтрами |
| GET | `/api/discounts/{id}` | Детали скидки |
| POST | `/api/discounts/{id}/view` | Increment view count |
| GET | `/api/stores/` | Список магазинов |
| GET | `/api/categories/` | Список категорий |
| GET | `/api/collections/` | Пользовательские подборки |

---

## 🐛 Известные ограничения

1. **In-memory rate limiter** - При рестарте сервера счетчики сбрасываются. Для production рекомендуется использовать Redis-based rate limiting.

2. **SQLite для тестов** - Интеграционные тесты используют SQLite, что может отличаться от поведения PostgreSQL.

3. **Прокси для скрапера** - В коде есть заглушки для прокси. Для production необходима интеграция с платным proxy сервисом.

4. **Отсутствие refresh tokens** - Реализованы только access токены. Рекомендуется добавить refresh token rotation.

---

## 🔮 Планы на будущее

### v1.1.0
- [ ] Refresh token implementation
- [ ] Redis-based rate limiting
- [ ] Email verification flow
- [ ] Password reset functionality

### v1.2.0
- [ ] WebSocket для real-time уведомлений
- [ ] GraphQL API опционально
- [ ] Admin панель для модерации
- [ ] Analytics dashboard

### v2.0.0 (Go/Next.js)
- [ ] Микросервисная архитектура
- [ ] Frontend на Next.js
- [ ] gRPC коммуникация между сервисами
- [ ] Kubernetes deployment

---

## 👥 Авторы

- Backend Team
- Data Scraping Team
- QA Team

## 📄 Лицензия

Proprietary - Tolk Platform
