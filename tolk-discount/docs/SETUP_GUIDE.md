# Детальная инструкция по запуску на локальном сервере

Это руководство содержит пошаговые инструкции для запуска Tolk Discount платформы на локальном сервере.

## Содержание

- [Требования](#требования)
- [Шаг 1: Подготовка окружения](#шаг-1-подготовка-окружения)
- [Шаг 2: Клонирование репозитория](#шаг-2-клонирование-репозитория)
- [Шаг 3: Запуск Backend (Go)](#шаг-3-запуск-backend-go)
- [Шаг 4: Запуск Frontend (Next.js)](#шаг-4-запуск-frontend-nextjs)
- [Шаг 5: Запуск через Docker Compose](#шаг-5-запуск-через-docker-compose)
- [Шаг 6: Проверка работоспособности](#шаг-6-проверка-работоспособности)
- [Шаг 7: Мониторинг и отладка](#шаг-7-мониторинг-и-отладка)

---

## Требования

### Минимальные системные требования

- **Оперативная память**: 8 GB RAM (рекомендуется 16 GB)
- **Процессор**: 4 ядра (рекомендуется 8 ядер)
- **Дисковое пространство**: 10 GB свободного места
- **ОС**: macOS 12+, Linux Ubuntu 20.04+, Windows 10+ (с WSL2)

### Необходимое ПО

| Программное обеспечение | Версия | Ссылка для скачивания |
|------------------------|--------|----------------------|
| Go | 1.21+ | [go.dev](https://go.dev/dl/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| Docker | 24+ | [docker.com](https://docker.com) |
| Git | 2.40+ | [git-scm.com](https://git-scm.com) |

---

## Шаг 1: Подготовка окружения

### 1.1 Установка Go

#### macOS
```bash
brew install go@1.21

# Проверка версии
go version
```

#### Linux (Ubuntu/Debian)
```bash
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -xvf go1.21.0.linux-amd64.tar.gz -C /usr/local
export PATH=$PATH:/usr/local/go/bin

# Добавьте в ~/.bashrc или ~/.zshrc для постоянного применения
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# Проверка версии
go version
```

#### Windows (WSL2)
```bash
# Внутри WSL2 выполните команды для Linux
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -xvf go1.21.0.linux-amd64.tar.gz -C /usr/local
```

### 1.2 Установка Node.js

#### macOS
```bash
brew install node@20

# Проверка версии
node --version
npm --version
```

#### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Проверка версии
node --version
npm --version
```

#### Windows
Скачайте установщик с [nodejs.org](https://nodejs.org/) и следуйте инструкциям мастера установки.

### 1.3 Установка Docker

#### macOS/Windows
1. Скачайте Docker Desktop с [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Установите и запустите приложение
3. Проверьте установку:
```bash
docker --version
docker compose version
```

#### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Перелогиньтесь или выполните:
newgrp docker

# Проверка
docker --version
docker compose version
```

### 1.4 Дополнительные инструменты (опционально)

#### Make
```bash
# macOS
brew install make

# Linux
sudo apt-get install make
```

#### kubectl (для Kubernetes)
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

---

## Шаг 2: Клонирование репозитория

```bash
# Клонирование репозитория
git clone <repository-url>
cd tolk-discount

# Проверка структуры проекта
ls -la
```

Ожидаемая структура:
```
tolk-discount/
├── backend/          # Go backend сервисы
├── frontend/         # Next.js frontend приложение
├── docs/             # Документация
├── README.md         # Главная документация
└── docker-compose.yml
```

---

## Шаг 3: Запуск Backend (Go)

### 3.1 Установка зависимостей

```bash
cd backend
go mod download

# Проверка установленных зависимостей
go list -m all
```

### 3.2 Настройка переменных окружения

Создайте файл `.env` в папке `backend`:

```bash
cd backend
cat > .env << EOF
# Server
PORT=8080
ENV=development

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tolk_discount
DB_USER=postgres
DB_PASSWORD=postgres
DB_SSLMODE=disable

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# NATS
NATS_URL=nats://localhost:4222

# JWT
JWT_SECRET=your-secret-key-here-change-in-production
JWT_EXPIRY=24h

# Logging
LOG_LEVEL=debug
LOG_FORMAT=json

# Tracing
JAEGER_ENDPOINT=http://localhost:14268/api/traces
TRACE_SAMPLE_RATE=1.0
EOF
```

### 3.3 Запуск базы данных и зависимостей

#### Вариант A: Использование Docker Compose только для зависимостей

```bash
# Запуск PostgreSQL, Redis и NATS
docker compose up -d postgres redis nats

# Проверка статуса
docker compose ps
```

#### Вариант B: Локальная установка (не рекомендуется)

Если вы предпочитаете запускать БД локально без Docker:

**PostgreSQL:**
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Создание базы данных
createdb tolk_discount
```

**Redis:**
```bash
# macOS
brew install redis
brew services start redis
```

**NATS:**
```bash
# macOS
brew install nats-server
brew services start nats-server
```

### 3.4 Запуск миграций БД

```bash
cd backend

# Через Makefile
make migrate

# Или напрямую (если используется golang-migrate)
go run cmd/migrate/main.go up
```

### 3.5 Запуск сервера разработки

```bash
cd backend

# Через Makefile (рекомендуется)
make run

# Или напрямую
go run cmd/main.go

# С горячим перезапуском (требуется air)
air
```

Backend будет доступен по адресу: `http://localhost:8080`

Проверка работоспособности:
```bash
curl http://localhost:8080/health
```

### 3.6 Запуск тестов

```bash
cd backend

# Все тесты
make test

# Тесты с покрытием
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out

# Тесты конкретного пакета
go test ./internal/discount/... -v

# Бенчмарки
go test ./... -bench=. -benchmem
```

### 3.7 Сборка бинарного файла

```bash
cd backend

# Через Makefile
make build

# Или напрямую
go build -o bin/server cmd/main.go

# Кросс-компиляция для Linux
GOOS=linux GOARCH=amd64 go build -o bin/server-linux cmd/main.go
```

---

## Шаг 4: Запуск Frontend (Next.js)

### 4.1 Установка зависимостей

```bash
cd frontend
npm install

# Если возникают проблемы с зависимостями
npm install --legacy-peer-deps

# Проверка установленных пакетов
npm list --depth=0
```

### 4.2 Настройка переменных окружения

Создайте файл `.env.local` в папке `frontend`:

```bash
cd frontend
cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_API_VERSION=v1

# Application
NEXT_PUBLIC_APP_NAME=Tolk Discount
NEXT_PUBLIC_APP_VERSION=2.0.0

# Authentication
NEXT_PUBLIC_AUTH_ENABLED=true

# Features
NEXT_PUBLIC_FEATURE_NEW_UI=true
NEXT_PUBLIC_FEATURE_ANALYTICS=true

# Cache
NEXT_PUBLIC_REVALIDATE_INTERVAL=60
EOF
```

### 4.3 Запуск сервера разработки

```bash
cd frontend

# Запуск dev сервера
npm run dev

# Запуск на конкретном порту
npm run dev -- -p 3001

# Запуск с включенным debug режимом
NODE_OPTIONS='--inspect' npm run dev
```

Frontend будет доступен по адресу: `http://localhost:3000`

### 4.4 Сборка для продакшена

```bash
cd frontend

# Создание production билда
npm run build

# Анализ размера бандла
npm run build -- --analyze

# Запуск production сервера
npm run start

# Запуск на конкретном порту
npm run start -- -p 3001
```

### 4.5 Линтинг и форматирование

```bash
cd frontend

# ESLint
npm run lint

# ESLint с авто-исправлением
npm run lint -- --fix

# Prettier
npx prettier --write .

# Проверка типов TypeScript
npx tsc --noEmit
```

---

## Шаг 5: Запуск через Docker Compose

Этот способ рекомендуется для быстрого развертывания всего стека технологий.

### 5.1 Запуск всех сервисов

```bash
cd tolk-discount

# Запуск в фоновом режиме
docker compose up -d

# Запуск с пересборкой образов
docker compose up -d --build

# Запуск в режиме foreground (видны логи)
docker compose up
```

### 5.2 Просмотр логов

```bash
# Все логи
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f nats

# Последние 100 строк логов
docker compose logs --tail=100 backend
```

### 5.3 Остановка сервисов

```bash
# Остановка с сохранением данных
docker compose down

# Остановка с удалением томов (данные будут потеряны)
docker compose down -v

# Остановка с удалением образов
docker compose down --rmi all
```

### 5.4 Выполнение команд внутри контейнеров

```bash
# Подключение к shell контейнера
docker compose exec backend sh
docker compose exec frontend sh

# Выполнение команды
docker compose exec backend go version
docker compose exec frontend node --version

# Доступ к базе данных
docker compose exec postgres psql -U postgres tolk_discount
```

### 5.5 Масштабирование сервисов

```bash
# Запуск нескольких экземпляров backend
docker compose up -d --scale backend=3

# Проверка запущенных контейнеров
docker compose ps
```

### 5.6 Очистка кэша Docker

```bash
# Удаление неиспользуемых ресурсов
docker system prune

# Удаление всех остановленных контейнеров
docker container prune

# Удаление всех unused образов
docker image prune -a

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

---

## Шаг 6: Проверка работоспособности

### 6.1 Health Check эндпоинты

```bash
# Проверка backend
curl http://localhost:8080/health

# Подробная информация о здоровье
curl http://localhost:8080/health/ready
curl http://localhost:8080/health/live

# Проверка frontend
curl http://localhost:3000

# Проверка статус кода
curl -I http://localhost:8080/health
```

### 6.2 Тестовые API запросы

```bash
# Получение списка скидок
curl http://localhost:8080/api/v1/discounts

# Получение скидки по ID
curl http://localhost:8080/api/v1/discounts/1

# Поиск скидок
curl "http://localhost:8080/api/v1/discounts?search=laptop&limit=10"

# Авторизация
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Получение персональных рекомендаций (требуется токен)
TOKEN="your-jwt-token"
curl http://localhost:8080/api/v1/discounts/personal \
  -H "Authorization: Bearer $TOKEN"
```

### 6.3 Проверка WebSocket соединения

```bash
# Если поддерживаются WebSocket
wscat -c ws://localhost:8080/ws
```

### 6.4 Проверка метрик

```bash
# Prometheus метрики
curl http://localhost:8080/metrics

# Статистика по запросам
curl http://localhost:8080/api/v1/stats
```

---

## Шаг 7: Мониторинг и отладка

### 7.1 Prometheus Metrics

```bash
# Метрики backend
curl http://localhost:8080/metrics

# Откройте Prometheus UI
# http://localhost:9090
```

Примеры запросов PromQL:
```
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Latency p99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### 7.2 Jaeger Distributed Tracing

Откройте `http://localhost:16686` для просмотра трейсов.

Поиск трейсов:
1. Выберите сервис из dropdown
2. Укажите операцию (endpoint)
3. Нажмите "Find Traces"

### 7.3 Grafana Dashboard

Откройте `http://localhost:3001`

- **Логин**: admin
- **Пароль**: admin (измените при первом входе)

Импортированные дашборды:
- Backend Performance
- Database Metrics
- Business Metrics

### 7.4 Loki Log Aggregation

Откройте `http://localhost:3100` для доступа к логам.

Пример запроса LogQL:
```logql
{app="backend"} |= "error"
```

### 7.5 Отладка Go приложения

```bash
# Запуск с Delve debugger
dlv debug cmd/main.go

# Подключение к работающему процессу
dlv attach <pid>

# Remote debugging
dlv debug --headless --listen=:2345 --api-version=2 cmd/main.go
```

### 7.6 Отладка Next.js приложения

```bash
# Запуск с инспектором Node.js
NODE_OPTIONS='--inspect' npm run dev

# Откройте chrome://inspect в Chrome
```

### 7.7 Профилирование

#### Go Profiling
```bash
# CPU Profile
go tool pprof http://localhost:8080/debug/pprof/profile

# Memory Profile
go tool pprof http://localhost:8080/debug/pprof/heap

# Trace
go tool trace http://localhost:8080/debug/trace
```

#### React DevTools
Установите расширение React DevTools для браузера для отладки компонентов.

---

## Решение распространенных проблем

### Проблема: Port already in use

```bash
# Найти процесс на порту
lsof -i :8080
lsof -i :3000

# Убить процесс
kill -9 <PID>

# Или изменить порт в конфигурации
```

### Проблема: Database connection refused

```bash
# Проверить статус PostgreSQL
docker compose ps postgres

# Проверить логи
docker compose logs postgres

# Перезапустить БД
docker compose restart postgres
```

### Проблема: Module not found (Node.js)

```bash
# Очистить кэш npm
npm cache clean --force

# Удалить node_modules и package-lock.json
rm -rf node_modules package-lock.json

# Переустановить зависимости
npm install
```

### Проблема: Go module errors

```bash
# Очистить кэш модулей
go clean -modcache

# Обновить зависимости
go get -u ./...

# Тидиайз go.mod
go mod tidy
```

---

## Дополнительные ресурсы

- [Документация Go](https://golang.org/doc/)
- [Документация Next.js](https://nextjs.org/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)

---

**Последнее обновление**: Май 2026  
**Версия документации**: 2.0.0
