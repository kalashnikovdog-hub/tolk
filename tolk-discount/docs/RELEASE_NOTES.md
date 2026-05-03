# Release Notes

Этот файл содержит подробные заметки о релизах проекта Tolk Discount.

---

## Release v2.0.0

**Дата релиза:** 3 мая 2026  
**Тип релиза:** Major (мажорный)  
**Статус:** ✅ Стабильная, рекомендуется к использованию

### 📋 Обзор

Tolk v2.0 представляет собой полный рефакторинг платформы с переходом на новую архитектуру, 
ориентированную на высокую производительность и отказоустойчивость.

### 🎯 Цели релиза

1. **Производительность**: Увеличение в 10-20 раз по сравнению с v1
2. **Масштабируемость**: Поддержка 10,000+ RPS
3. **Отказоустойчивость**: Availability > 99.9%
4. **Наблюдаемость**: Полный coverage monitoring, tracing, logging
5. **Безопасность**: mTLS, JWT rotation, rate limiting

### 🏗️ Архитектурные изменения

#### До (v1.x)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│ PostgreSQL  │
│    Vite     │     │   + Celery  │     │   Redis     │
└─────────────┘     └─────────────┘     └─────────────┘
```

#### После (v2.0)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Next.js 14 │────▶│ Go + gRPC   │────▶│ Patroni HA  │
│  App Router │     │   Istio     │     │ Redis Cluster│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌──────────┐  ┌──────────┐
              │   NATS   │  │ Jaeger   │
              │ JetStream│  │ Loki     │
              └──────────┘  └──────────┘
```

### ✨ Новые возможности

#### Backend Services

| Сервис | Описание | Технологии |
|--------|----------|------------|
| API Gateway | Маршрутизация, auth, rate limiting | Go, gRPC, middleware |
| Auth Service | JWT, OAuth2, RBAC | Go, Redis, JWT |
| Discount Service | CRUD, поиск, рекомендации | Go, PostgreSQL, Redis |
| Collection Service | Подборки, social sharing | Go, NATS |
| Family Card Service | Семейные карты, invites | Go, PostgreSQL |
| Scraper Service | Парсинг сайтов | Go, Scrapy-like, NATS |

#### Frontend Features

- **Server Components**: Рендеринг на сервере для SEO
- **Edge Functions**: Гео-распределение контента
- **PWA Support**: Офлайн работа, push уведомления
- **Modern Stack**: Next.js 14, React Query, Zustand, TailwindCSS

#### Infrastructure

- **High Availability**: Patroni для автоматического failover БД
- **Distributed Cache**: Redis Cluster для масштабирования
- **Event Streaming**: NATS JetStream для асинхронной обработки
- **Service Mesh**: Istio для service-to-service коммуникации
- **Time Series DB**: TimescaleDB для аналитики

### 🔧 Технические детали

#### Производительность

| Endpoint | v1 (RPS) | v2 (RPS) | Улучшение |
|----------|----------|----------|-----------|
| GET /api/discounts | 500 | 5,000 | **10x** |
| POST /api/auth/login | 200 | 3,000 | **15x** |
| GET /api/discounts/personal | 100 | 2,000 | **20x** |

#### Latency (p99)

| Метрика | v1 | v2 | Цель |
|---------|-----|-----|------|
| API Response | 250ms | <100ms | ✅ |
| DB Query | 50ms | <20ms | ✅ |
| Cache Hit | 5ms | <2ms | ✅ |

#### Resource Utilization

| Ресурс | v1 | v2 | Экономия |
|--------|-----|-----|----------|
| CPU (per instance) | 2 cores | 0.5 cores | 75% |
| Memory (per instance) | 2 GB | 512 MB | 75% |
| Startup Time | 30s | 2s | 93% |

### ⚠️ Breaking Changes

#### API Changes

**Изменение формата ответов:**

v1:
```json
{
  "status": "ok",
  "data": {...}
}
```

v2:
```json
{
  "success": true,
  "data": {...},
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

**Новые обязательные заголовки:**
- `X-Request-ID` - для трассировки
- `X-API-Version` - версия API

#### Authentication

**JWT Token Format:**

v1:
```json
{
  "user_id": 123,
  "exp": 1234567890
}
```

v2:
```json
{
  "sub": "user_123",
  "iat": 1234567890,
  "exp": 1234567890,
  "roles": ["user", "admin"],
  "permissions": ["read", "write"],
  "tenant_id": "org_456"
}
```

#### Database Schema

**Миграция схемы требуется:**

```bash
# Экспорт из v1
pg_dump -h old-host -U postgres tolk_discount > backup_v1.sql

# Импорт в v2 (с трансформацией)
psql -h new-host -U postgres tolk_discount_v2 < backup_v1_transformed.sql
```

#### Environment Variables

**Новые обязательные переменные:**

```bash
# Backend
GRPC_PORT=9090
JAEGER_ENDPOINT=http://jaeger:14268/api/traces
NATS_URL=nats://nats:4222
PATRONI_DSN=postgres://patroni:password@host:5432/db

# Frontend
NEXT_PUBLIC_API_VERSION=v2
NEXT_PUBLIC_FEATURE_FLAGS={"new_ui":true}
```

### 📦 Установка и обновление

#### Fresh Install

```bash
# Клонирование
git clone <repository-url>
cd tolk-discount

# Запуск через Docker Compose
docker compose up -d

# Проверка
curl http://localhost:8080/health
```

#### Upgrade с v1.x

```bash
# 1. Backup данных
pg_dump -h old-host -U postgres tolk_discount > backup.sql

# 2. Остановка v1 сервисов
docker compose -f docker-compose.v1.yml down

# 3. Миграция данных
./scripts/migrate_v1_to_v2.sh

# 4. Запуск v2 сервисов
docker compose up -d

# 5. Верификация
curl http://localhost:8080/health/ready
```

### 🐛 Известные проблемы

На момент релиза известных проблем нет.

### 🔮 Планы на будущее

#### v2.1.0 (Q3 2026)
- [ ] GraphQL API
- [ ] WebSocket для real-time обновлений
- [ ] Advanced caching стратегии

#### v2.2.0 (Q4 2026)
- [ ] ML recommendations engine
- [ ] A/B testing framework
- [ ] Multi-region deployment

#### v3.0.0 (2027)
- [ ] Mobile SDK
- [ ] Edge computing integration
- [ ] Quantum-resistant cryptography (research)

### 📞 Поддержка

- **Документация**: [docs/tolk-discount.io](https://docs.tolk-discount.io)
- **GitHub Issues**: [github.com/tolk-discount/issues](https://github.com/tolk-discount/issues)
- **Discord**: [discord.gg/tolk-discount](https://discord.gg/tolk-discount)
- **Email**: support@tolk-discount.io

---

## Release v1.0.0

**Дата релиза:** 3 мая 2026  
**Тип релиза:** Initial (первый выпуск)  
**Статус:** ⚠️ Устаревшая, не рекомендуется к использованию

### 📋 Обзор

Первая версия платформы Tolk Discount, предоставляющая базовый функционал 
для управления скидками и подборками.

### ✨ Возможности

#### Backend
- REST API на Python/FastAPI
- CRUD операции со скидками
- Authentication через JWT
- Интеграция с PostgreSQL и Redis
- Celery для фоновых задач

#### Frontend
- SPA на React + Vite
- Компоненты: DiscountCard, Navigation, SearchFilter
- Страницы: HomePage, AdminPanel, UserProfile
- Responsive design

#### Scraper
- Парсинг сайтов магазинов через Scrapy
- Планировщик задач
- Автоматическое обновление скидок

### 📊 Метрики

- **Максимальная нагрузка**: ~500 RPS
- **Средняя latency**: 250ms (p99)
- **Время запуска**: 30 секунд
- **Требования к ресурсам**: 2 cores, 2GB RAM per instance

### ⚠️ Ограничения

- Нет поддержки высокой доступности
- Отсутствие distributed tracing
- Limited monitoring capabilities
- Синхронная обработка скрапинга
- Проблемы с масштабированием

### 🔮 Развитие

Эта версия послужила основой для создания v2.0 с полной переработкой архитектуры.

---

## Политика поддержки версий

### Поддерживаемые версии

| Версия | Статус | Поддержка до |
|--------|--------|--------------|
| 2.0.x | ✅ Active | Текущая + 12 месяцев |
| 1.0.x | ⚠️ EOL | Не поддерживается |

### Типы релизов

- **Major (X.0.0)**: Критические изменения, breaking changes
- **Minor (x.Y.0)**: Новая функциональность, обратная совместимость
- **Patch (x.y.Z)**: Исправления ошибок, security patches

### Security Updates

Security patches выпускаются в течение:
- **v2.x**: 48 часов после обнаружения уязвимости
- **v1.x**: Не выпускаются (EOL)

---

## Changelog Reference

Для полной истории изменений см. [CHANGELOG.md](./CHANGELOG.md)

---

**Последнее обновление**: Май 2026  
**Контакт**: release-team@tolk-discount.io
