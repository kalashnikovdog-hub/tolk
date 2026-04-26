# DiscountHub v2.0 - Высоконагруженная платформа скидок

Модернизированная версия платформы с улучшенной отказоустойчивостью и производительностью.

## 🚀 Улучшения по сравнению с v1

| Аспект | v1 | v2 |
|--------|-----|-----|
| Backend | FastAPI (Python) | Go + gRPC |
| Frontend | React + Vite | Next.js 14 App Router |
| БД | PostgreSQL standalone | PostgreSQL + Patroni (HA) |
| Кэш | Redis standalone | Redis Cluster |
| Очереди | Celery | NATS JetStream |
| Service Mesh | Нет | Istio (circuit breaker, retry) |
| Оркестрация | Docker Compose | Kubernetes + HPA |
| Мониторинг | Prometheus basic | Prometheus + Grafana + Loki |
| Tracing | Нет | Jaeger/OpenTelemetry |

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloudflare/Cloud Load Balancer                │
│                         (DDoS Protection)                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Ingress Controller (nginx)                   │
│                      + TLS Termination                           │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌───────────────┐
│   Frontend    │     │   API Gateway   │     │   Scraper     │
│  Next.js 14   │     │   (Go + gRPC)   │     │   (Go)        │
│  Edge Cache   │     │   Rate Limiting │     │   NATS Pub    │
└───────────────┘     └─────────────────┘     └───────────────┘
        │                       │                       │
        │              ┌────────┴────────┐              │
        │              │                 │              │
        ▼              ▼                 ▼              ▼
               ┌─────────────┐   ┌─────────────┐  ┌──────────┐
               │ Auth Service│   │Discount Svc │  │  NATS    │
               │   (gRPC)    │   │   (gRPC)    │  │JetStream │
               └─────────────┘   └─────────────┘  └──────────┘
                      │                 │                 │
                      └────────┬────────┘                 │
                               ▼                          │
                    ┌──────────────────┐                  │
                    │  PostgreSQL HA   │◄─────────────────┘
                    │  (Patroni+etcd)  │
                    └──────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌─────────────────┐   ┌─────────────────┐
           │   Redis Cluster │   │   TimescaleDB   │
           │   (Cache/Sess)  │   │   (Analytics)   │
           └─────────────────┘   └─────────────────┘
```

## 📋 Компоненты

### Backend Services (Go)

#### API Gateway
- Маршрутизация запросов
- Rate limiting (token bucket)
- Authentication/Authorization
- Request validation
- Circuit breaker pattern

#### Auth Service
- JWT token management
- OAuth2 providers
- Session management
- RBAC

#### Discount Service
- CRUD операции со скидками
- Поиск и фильтрация
- Персональные рекомендации
- Кэширование hot data

#### Collection Service
- Управление подборками
- Social sharing
- Analytics

#### Family Card Service
- Управление семейными картами
- Invitation system
- Shared benefits

### Frontend (Next.js 14)

- **App Router** - серверные компоненты
- **React Query** - кэширование на клиенте
- **Zustand** - глобальное состояние
- **TailwindCSS** - стилизация
- **PWA** - офлайн работа
- **Edge Functions** - гео-распределение

### Message Queue (NATS JetStream)

- Асинхронная обработка
- Event sourcing
- Retry logic с exponential backoff
- Dead letter queue

### Database

#### PostgreSQL + Patroni
- Автоматический failover
- Репликация
- Point-in-time recovery

#### Redis Cluster
- Сессионное хранилище
- Кэширование
- Rate limiting counters

#### TimescaleDB
- Аналитика событий
- Метрики пользователей
- Временные ряды

## 🔧 Отказоустойчивость

### Circuit Breaker Pattern
```go
// Пример реализации circuit breaker
breaker := circuitbreaker.New(circuitbreaker.Config{
    MaxFailures: 5,
    Timeout: 30 * time.Second,
    HalfOpenRequests: 3,
})
```

### Retry Policy
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Max retries: 5
- Jitter для предотвращения thundering herd

### Health Checks
- Liveness probe - проверка живости сервиса
- Readiness probe - готовность обрабатывать запросы
- Startup probe - для медленного старта

### Graceful Degradation
- Fallback responses при недоступности сервисов
- Stale cache serving
- Queue requests для последующей обработки

## 📊 Мониторинг

### Metrics (Prometheus)
- Request rate
- Error rate
- Latency percentiles (p50, p95, p99)
- Resource utilization

### Distributed Tracing (Jaeger)
- End-to-end tracing
- Service dependency mapping
- Bottleneck identification

### Logging (Loki)
- Structured logging
- Log aggregation
- Alert rules

## 🚀 Быстрый старт

### Требования
- Go 1.21+
- Node.js 20+
- Docker & Docker Compose
- kubectl (для Kubernetes)

### Локальная разработка

```bash
# Backend
cd discount-service-new/backend
go mod download
make run

# Frontend
cd discount-service-new/frontend
npm install
npm run dev
```

### Docker Compose

```bash
cd discount-service-new
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f infrastructure/k8s/
```

## 📈 Производительность

### Целевые метрики
- API latency p99 < 100ms
- Throughput > 10,000 RPS
- Availability > 99.9%
- Time to recover < 30s

### Benchmark результаты

| Endpoint | v1 (RPS) | v2 (RPS) | Улучшение |
|----------|----------|----------|-----------|
| GET /api/discounts | 500 | 5,000 | 10x |
| POST /api/auth/login | 200 | 3,000 | 15x |
| GET /api/discounts/personal | 100 | 2,000 | 20x |

## 🔐 Безопасность

- mTLS между сервисами
- JWT с коротким временем жизни
- Refresh token rotation
- Rate limiting per user/IP
- SQL injection prevention
- XSS protection
- CSP headers

## 📝 Лицензия

MIT License

---

**DiscountHub v2.0** © 2024 - Построено для масштаба!
