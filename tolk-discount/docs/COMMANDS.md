# Команды для разработки

Справочник всех команд для разработки, тестирования и деплоя Tolk Discount.

## Содержание

- [Backend команды (Go)](#backend-команды-go)
- [Frontend команды (Next.js)](#frontend-команды-nextjs)
- [Docker команды](#docker-команды)
- [Утилиты и инструменты](#утилиты-и-инструменты)
- [Makefile команды](#makefile-команды)

---

## Backend команды (Go)

### Установка зависимостей

```bash
cd backend

# Скачать все зависимости
go mod download

# Обновить зависимости
go get -u ./...

# Очистить неиспользуемые зависимости
go mod tidy

# Проверить зависимости на уязвимости
go list -m -versions all
```

### Запуск приложения

```bash
cd backend

# Запуск в режиме разработки
go run cmd/main.go

# Запуск с флагами
go run cmd/main.go -config=config.yaml -port=8080

# Запуск конкретного сервиса
go run cmd/services/discount/main.go

# С горячим перезапуском (требуется air)
air

# Запуск в фоне
nohup go run cmd/main.go > app.log 2>&1 &
```

### Сборка

```bash
cd backend

# Сборка бинарного файла
go build -o bin/server cmd/main.go

# Сборка с оптимизацией
go build -ldflags="-s -w" -o bin/server cmd/main.go

# Кросс-компиляция для Linux
GOOS=linux GOARCH=amd64 go build -o bin/server-linux cmd/main.go

# Кросс-компиляция для macOS (ARM)
GOOS=darwin GOARCH=arm64 go build -o bin/server-darwin-arm cmd/main.go

# Кросс-компиляция для Windows
GOOS=windows GOARCH=amd64 go build -o bin/server.exe cmd/main.go

# Сборка всех сервисов
go build -o bin/ ./cmd/...
```

### Тестирование

```bash
cd backend

# Запуск всех тестов
go test ./...

# Запуск тестов с выводом
go test ./... -v

# Запуск тестов с покрытием
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out
go tool cover -func=coverage.out

# Запуск тестов конкретного пакета
go test ./internal/discount/... -v

# Запуск тестов по шаблону
go test ./... -run TestDiscount

# Бенчмарки
go test ./... -bench=. -benchmem

# Бенчмарки с CPU профилем
go test ./... -bench=. -cpuprofile=cpu.prof

# Race detector
go test ./... -race

# Parallel tests
go test ./... -parallel 4
```

### Форматирование и линтинг

```bash
cd backend

# Форматирование кода
go fmt ./...

# Веттинг кода (поиск проблем)
go vet ./...

# Запуск golangci-lint
golangci-lint run

# Запуск с авто-исправлением
golangci-lint run --fix

# Проверка на unused code
staticcheck ./...

# Проверка безопасности
gosec ./...
```

### Профилирование

```bash
cd backend

# CPU Profile
go tool pprof http://localhost:8080/debug/pprof/profile

# Memory Profile
go tool pprof http://localhost:8080/debug/pprof/heap

# Block Profile
go tool pprof http://localhost:8080/debug/pprof/block

# Mutex Profile
go tool pprof http://localhost:8080/debug/pprof/mutex

# Trace
go tool trace http://localhost:8080/debug/trace

# goroutine profile
go tool pprof http://localhost:8080/debug/pprof/goroutine
```

### Миграции БД

```bash
cd backend

# Применить миграции
go run cmd/migrate/main.go up

# Откатить миграцию
go run cmd/migrate/main.go down

# Создать новую миграцию
go run cmd/migrate/main.go create add_user_table

# Статус миграций
go run cmd/migrate/main.go status

# Force версию
go run cmd/migrate/main.go force 5
```

### Генерация кода

```bash
cd backend

# Генерация mock'ов
mockgen -source=internal/discount/repository.go -destination=mocks/discount_repository.go

# Генерация gRPC кода
protoc --go_out=. --go_opt=paths=source_relative \
       --go-grpc_out=. --go-grpc_opt=paths=source_relative \
       proto/*.proto

# Генерация swagger документации
swag init -g cmd/main.go

# Генерация deep copy функций
deepcopy-gen --input-dirs ./api/v1
```

---

## Frontend команды (Next.js)

### Установка зависимостей

```bash
cd frontend

# Установка зависимостей
npm install

# Установка с кэшем
npm ci

# Обновление зависимостей
npm update

# Установка конкретной версии
npm install package@version

# Dev зависимости
npm install --save-dev package
```

### Запуск приложения

```bash
cd frontend

# Запуск dev сервера
npm run dev

# Запуск на конкретном порту
npm run dev -- -p 3001

# Запуск с инспектором
NODE_OPTIONS='--inspect' npm run dev

# Запуск с открытием браузера
npm run dev -- --open

# HTTPS режим
npm run dev -- --experimental-https
```

### Сборка

```bash
cd frontend

# Production сборка
npm run build

# Сборка с анализом бандла
npm run build -- --analyze

# Standalone сборка
npm run build -- --standalone

# Запуск production сервера
npm run start

# Запуск на конкретном порту
npm run start -- -p 3001
```

### Тестирование

```bash
cd frontend

# Запуск тестов
npm run test

# Запуск тестов в watch режиме
npm run test -- --watch

# Запуск тестов с покрытием
npm run test -- --coverage

# Запуск конкретных тестов
npm run test -- --testNamePattern="component name"

# E2E тесты
npm run test:e2e

# Cypress тесты
npm run cypress:open

# Playwright тесты
npm run playwright:test
```

### Линтинг и форматирование

```bash
cd frontend

# ESLint
npm run lint

# ESLint с авто-исправлением
npm run lint -- --fix

# Prettier форматирование
npx prettier --write .

# Prettier проверка
npx prettier --check .

# Проверка типов TypeScript
npx tsc --noEmit

# Проверка типов в watch режиме
npx tsc --noEmit --watch
```

### Утилиты

```bash
cd frontend

# Очистка кэша
rm -rf .next node_modules/.cache

# Анализ зависимостей
npm list --depth=0

# Поиск устаревших пакетов
npm outdated

# Аудит безопасности
npm audit

# Авто-исправление уязвимостей
npm audit fix

# Генерация sitemap
npm run generate-sitemap

# Оптимизация изображений
npm run optimize-images
```

---

## Docker команды

### Основные команды

```bash
# Запуск всех сервисов
docker compose up -d

# Запуск с пересборкой
docker compose up -d --build

# Запуск в foreground режиме
docker compose up

# Остановка сервисов
docker compose down

# Остановка с удалением томов
docker compose down -v

# Остановка с удалением образов
docker compose down --rmi all

# Перезапуск сервисов
docker compose restart

# Перезапуск конкретного сервиса
docker compose restart backend
```

### Логи

```bash
# Просмотр всех логов
docker compose logs

# Логи в реальном времени
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f backend

# Последние N строк
docker compose logs --tail=100 backend

# Логи с timestamp
docker compose logs -ft
```

### Выполнение команд

```bash
# Подключение к shell
docker compose exec backend sh
docker compose exec frontend sh

# Выполнение команды
docker compose exec backend go version
docker compose exec frontend node --version

# Доступ к БД
docker compose exec postgres psql -U postgres tolk_discount

# Доступ к Redis CLI
docker compose exec redis redis-cli

# Запуск тестов в контейнере
docker compose exec backend go test ./...
```

### Управление образами

```bash
# Построить образ
docker compose build

# Построить без кэша
docker compose build --no-cache

# Построить конкретный сервис
docker compose build backend

# Pull образов
docker compose pull

# Push образов
docker compose push
```

### Масштабирование

```bash
# Запуск нескольких экземпляров
docker compose up -d --scale backend=3

# Проверка запущенных контейнеров
docker compose ps

# Детальная информация
docker compose ps -a

# Статистика ресурсов
docker stats
```

### Очистка

```bash
# Удаление остановленных контейнеров
docker container prune

# Удаление unused образов
docker image prune

# Удаление всех unused образов
docker image prune -a

# Удаление volumes
docker volume prune

# Полная очистка системы
docker system prune

# Полная очистка с volumes
docker system prune -a --volumes
```

### Экспорт/Импорт

```bash
# Экспорт образа
docker save -o backend.tar backend:latest

# Импорт образа
docker load -i backend.tar

# Экспорт контейнера
docker export -o backend-container.tar container_id

# Импорт контейнера
docker import backend-container.tar
```

---

## Утилиты и инструменты

### Git команды

```bash
# Создание новой ветки
git checkout -b feature/new-feature

# Коммит изменений
git commit -m "feat: add new feature"

# Push ветки
git push origin feature/new-feature

# Rebase на main
git rebase main

# Squash коммитов
git rebase -i HEAD~3

# Cherry-pick
git cherry-pick commit_hash

# Stash изменений
git stash
git stash pop

# Показать историю
git log --oneline --graph --all
```

### Makefile команды

```bash
#查看所有目标
make help

# Запуск backend
make run

# Запуск frontend
make run-frontend

# Запуск всех сервисов
make up

# Остановка сервисов
make down

# Сборка backend
make build

# Сборка frontend
make build-frontend

# Запуск тестов backend
make test

# Запуск тестов frontend
make test-frontend

# Линтинг backend
make lint

# Линтинг frontend
make lint-frontend

# Форматирование кода
make fmt

# Применение миграций
make migrate

# Создание миграции
make migration NAME=add_user_table

# Очистка кэша
make clean

# Reset базы данных
make db-reset

# Backup базы данных
make db-backup

# Restore базы данных
make db-restore BACKUP_FILE=backup.sql
```

### Kubernetes команды (если используется)

```bash
# Применить манифесты
kubectl apply -f k8s/

# Проверка подов
kubectl get pods

# Проверка сервисов
kubectl get svc

# Логи пода
kubectl logs -f pod-name

# Exec в под
kubectl exec -it pod-name -- sh

# Масштабирование
kubectl scale deployment backend --replicas=3

# Rollout статуса
kubectl rollout status deployment/backend

# Rollback
kubectl rollout undo deployment/backend

# Port forwarding
kubectl port-forward svc/backend 8080:8080
```

---

## Quick Reference

### Быстрый старт разработки

```bash
# Backend
cd backend && go mod download && make run

# Frontend
cd frontend && npm install && npm run dev

# Все сервисы через Docker
docker compose up -d
```

### Тестирование

```bash
# Backend тесты
cd backend && go test ./... -v

# Frontend тесты
cd frontend && npm run test

# E2E тесты
npm run test:e2e
```

### Деплой

```bash
# Build
make build-all

# Docker images
docker compose build

# Push images
docker push registry/tolk-backend:latest
docker push registry/tolk-frontend:latest

# Deploy to K8s
kubectl apply -f k8s/
```

---

**Последнее обновление**: Май 2026  
**Версия**: 2.0.0
