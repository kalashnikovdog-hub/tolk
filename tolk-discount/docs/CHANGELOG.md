# Changelog

Все значимые изменения в проекте Tolk Discount будут задокументированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/), 
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

---

## [2.0.0] - 2026-05-03

### 🎉 Добавлено

#### Backend (Go)
- **API Gateway** на Go с поддержкой middleware
  - Маршрутизация запросов
  - Rate limiting (token bucket algorithm)
  - Authentication/Authorization через JWT
  - Request validation
  - Circuit breaker pattern для отказоустойчивости
  
- **Auth Service**
  - JWT token management с refresh token rotation
  - OAuth2 providers (Google, GitHub, Apple)
  - Session management с Redis
  - RBAC (Role-Based Access Control)
  
- **Discount Service**
  - CRUD операции со скидками
  - Поиск и фильтрация по множеству параметров
  - Персональные рекомендации на основе истории
  - Кэширование hot data в Redis Cluster
  - Поддержка категорий и тегов
  
- **Collection Service**
  - Управление подборками скидок
  - Social sharing функциональность
  - Analytics по популярности подборок
  
- **Family Card Service**
  - Управление семейными картами
  - Invitation system для членов семьи
  - Shared benefits между участниками
  
- **Scraper Service**
  - Парсинг сайтов магазинов на Go
  - Интеграция с NATS JetStream для асинхронной обработки
  - Автоматическое обновление скидок
  
#### Frontend (Next.js 14)
- **App Router** - серверные компоненты React
- **React Query** - кэширование на клиенте
- **Zustand** - глобальное состояние приложения
- **TailwindCSS** - утилитарная стилизация
- **PWA** - поддержка офлайн работы
- **Edge Functions** - гео-распределение
- **Server-Side Rendering (SSR)** для SEO
- **Incremental Static Regeneration (ISR)**

#### Инфраструктура
- **PostgreSQL + Patroni** для высокой доступности БД
  - Автоматический failover
  - Синхронная репликация
  - Point-in-time recovery
  
- **Redis Cluster** для распределенного кэширования
  - Сессионное хранилище
  - Rate limiting counters
  - Distributed locks
  
- **TimescaleDB** для аналитики
  - Хранение временных рядов
  - Агрегация метрик пользователей
  - Быстрые запросы по времени
  
- **NATS JetStream** для message queue
  - Асинхронная обработка событий
  - Event sourcing паттерн
  - Retry logic с exponential backoff
  - Dead letter queue для ошибочных сообщений
  
- **Istio Service Mesh**
  - Circuit breaker между сервисами
  - Automatic retry с jitter
  - mTLS для безопасности
  - Traffic splitting для canary deployments

#### Мониторинг и Observability
- **Prometheus** для сбора метрик
  - Request rate
  - Error rate
  - Latency percentiles (p50, p95, p99)
  - Resource utilization
  
- **Grafana** для визуализации
  - Дашборды по каждому сервису
  - Business metrics
  - Alert rules
  
- **Jaeger/OpenTelemetry** для distributed tracing
  - End-to-end tracing запросов
  - Service dependency mapping
  - Bottleneck identification
  
- **Loki** для агрегации логов
  - Structured logging
  - Log aggregation со всех сервисов
  - Full-text search

### 🔧 Изменено

- Миграция backend с Python/FastAPI на Go 1.21+
- Обновление протокола коммуникации с REST на gRPC
- Изменение схемы базы данных для поддержки новой архитектуры
- Обновление формата JWT токенов с расширенными claims
- Рефакторинг frontend с React/Vite на Next.js 14 App Router
- Изменение структуры проекта для монорепозитория

### 🗑️ Удалено

- Старый discount-service на Python/FastAPI
- Celery очереди задач
- Docker Compose-only архитектура (добавлена поддержка Kubernetes)
- Прямые SQL запросы без использования query builder
- Синхронная обработка скрапинга

### 🐛 Исправлено

- Утечки памяти при длительной работе сервиса
- Race conditions в многопоточной обработке
- Проблемы с подключением к БД при высоких нагрузках
- Ошибки кэширования stale data
- Неправильная обработка таймаутов внешних API

### ⚠️ Breaking Changes

- Изменение формата API ответов
- Обновленная структура JWT токенов
- Новые обязательные переменные окружения
- Измененные эндпоинты миграции
- Несовместимость схем БД с v1.x

---

## [1.0.0] - 2026-05-03

### 🎉 Добавлено

#### Backend (Python/FastAPI)
- **REST API** для управления скидками
  - CRUD операции
  - Поиск и фильтрация
  - Пагинация результатов
  
- **Authentication/Authorization**
  - JWT tokens
  - Basic auth
  - API keys для сервисов
  
- **Интеграция с базами данных**
  - PostgreSQL для основного хранения
  - Redis для кэширования и сессий
  
- **Celery** для фоновых задач
  - Периодический скрапинг
  - Отправка уведомлений
  - Обработка изображений

#### Frontend (React + Vite)
- **SPA приложение** с маршрутизацией
- **Компоненты**:
  - DiscountCard - отображение скидки
  - Navigation - навигация по приложению
  - SearchFilter - поиск и фильтрация
  - Pagination - пагинация списков
  
- **Страницы**:
  - HomePage - главная страница со списком скидок
  - AdminPanel - панель администратора
  - DiscountDetail - детальная информация о скидке
  - UserProfile - профиль пользователя

#### Scraper (Python/Scrapy)
- **Парсинг сайтов магазинов**
  - Автоматическое извлечение скидок
  - Обработка разных форматов сайтов
  - Сохранение в базу данных
  
- **Планировщик задач**
  - Периодический запуск парсеров
  - Обработка ошибок и retry

#### Daemon Services
- **Фоновые задачи**
  - Периодическая проверка актуальности скидок
  - Отправка email уведомлений
  - Генерация отчетов

### 🔧 Изменено

- Начальная структура проекта
- Базовая схема базы данных
- Конфигурация Docker Compose

### 📝 Документация

- README с инструкцией по запуску
- API документация через Swagger/OpenAPI
- Примеры использования

---

## [Unreleased]

### В планах

- [ ] GraphQL API для гибких запросов
- [ ] Machine Learning для персональных рекомендаций
- [ ] WebSocket для real-time обновлений
- [ ] Mobile приложения (iOS/Android)
- [ ] Интеграция с социальными сетями
- [ ] Система купонов и промокодов
- [ ] Геолокация для поиска ближайших магазинов
- [ ] Push уведомления
- [ ] A/B тестирование функциональности
- [ ] Мультиязычность интерфейса

---

## Версии

| Версия | Дата релиза | Тип | Статус |
|--------|-------------|-----|--------|
| 2.0.0 | 2026-05-03 | Major | ✅ Стабильная |
| 1.0.0 | 2026-05-03 | Initial | ⚠️ Устаревшая |

---

## Примечания к релизам

### Release 2.0.0 - Мажорный релиз

**Цели релиза:**
- Увеличение производительности в 10-20 раз
- Повышение отказоустойчивости системы
- Масштабирование до 10,000+ RPS
- Улучшение наблюдаемости (monitoring, tracing, logging)

**Критические изменения:**
- Изменение языка backend с Python на Go
- Изменение протокола коммуникации с REST на gRPC
- Миграция схемы базы данных
- Изменение формата JWT токенов

**Миграция с v1 на v2:**

```bash
# Экспорт данных из старой БД
pg_dump -h old-host -U postgres tolk_discount > backup.sql

# Импорт в новую БД
psql -h new-host -U postgres tolk_discount_v2 < backup.sql

# Обновление конфигов
# Обновить переменные окружения согласно новому формату
```

**Известные проблемы:**
- Нет известных проблем на момент релиза

---

### Release 1.0.0 - Initial Release

**Цели релиза:**
- Создание MVP платформы скидок
- Базовый функционал CRUD
- Интеграция с источниками данных

**Функционал:**
- Просмотр списка скидок
- Поиск и фильтрация
- Админ-панель для управления
- Семейные карты
- Подборки скидок

---

## Как читать changelog

### Типы изменений

- **Added** - новые функции
- **Changed** - изменения в существующем функционале
- **Deprecated** - скоро будет удалено
- **Removed** - удаленный функционал
- **Fixed** - исправления ошибок
- **Security** - исправления уязвимостей

### Формат версий

Проект использует [Semantic Versioning](https://semver.org/lang/ru/):

- **MAJOR** - несовместимые изменения API
- **MINOR** - новая функциональность, обратная совместимость
- **PATCH** - исправления ошибок, обратная совместимость

---

**Последнее обновление**: Май 2026  
**Поддерживаемые версии**: 2.0.x
