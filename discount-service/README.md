# DiscountHub - Сервис скидок и промо-акций

Полноценная платформа для поиска, сбора и управления скидками с монетизацией через подписку.

## 📋 Оглавление

- [Возможности](#возможности)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [API Документация](#api-документация)
- [PWA Фронтенд](#pwa-фронтенд)
- [Монетизация](#монетизация)

## ✨ Возможности

### Для пользователей
- 🔍 **Поиск и фильтрация** скидок по категориям, магазинам, размеру скидки
- 🎯 **Персональные скидки** на основе предпочтений и истории
- 👨‍👩‍👧‍👦 **Семейная карта** - объединение до 5 участников
- 🏪 **Магазины**: Пятёрочка, Перекрёсток, Магнит, Лента и др.
- 💳 **Банковские предложения** - специальные категории каждый месяц
- 📚 **Цифровые каталоги** - копии бумажных каталогов магазинов
- 📝 **Подборки** - создание и публикация коллекций скидок
- 💰 **Базовая скидка 2-3%** на все товары без акций

### PWA Приложения
- 📱 Установка на iOS и Android
- 💾 Офлайн работа
- 🔔 Push уведомления о новых скидках
- ⚡ Быстрая загрузка

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                      Nginx (Reverse Proxy)                   │
│                         Port 80/443                          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌───────────────┐
│   Frontend    │   │     Backend     │   │   Scraper     │
│  (React PWA)  │   │   (FastAPI)     │   │   (Scrapy)    │
│   Port 3000   │   │    Port 8000    │   │   Scheduled   │
└───────────────┘   └─────────────────┘   └───────────────┘
        │                     │                     │
        │              ┌──────┴──────┐              │
        │              │             │              │
        ▼              ▼             ▼              ▼
               ┌──────────┐  ┌──────────┐   ┌──────────┐
               │PostgreSQL│  │  Redis   │   │  Celery  │
               │  :5432   │  │  :6379   │   │  Worker  │
               └──────────┘  └──────────┘   └──────────┘
```

## 🚀 Быстрый старт

### Требования
- Docker & Docker Compose
- Node.js 18+ (для локальной разработки фронтенда)
- Python 3.10+ (для локальной разработки бэкенда)

### Запуск через Docker Compose

```bash
cd discount-service

# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

Сервисы будут доступны:
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **Swagger Docs**: http://localhost/api/docs

### Локальная разработка

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Scraper
```bash
cd scraper
pip install -r requirements.txt
scrapy crawl grocery_spider
```

## 📡 API Документация

### Основные эндпоинты

#### Аутентификация
```
POST   /api/auth/register      Регистрация
POST   /api/auth/login         Вход
POST   /api/auth/logout        Выход
GET    /api/auth/me            Текущий пользователь
```

#### Скидки
```
GET    /api/discounts          Список скидок
GET    /api/discounts/{id}     Детали скидки
GET    /api/discounts/personal Персональные скидки
GET    /api/discounts/bank-offers Банковские предложения
POST   /api/discounts/{id}/favorite Добавить в избранное
```

#### Магазины и категории
```
GET    /api/stores             Список магазинов
GET    /api/categories         Список категорий
```

#### Подборки
```
GET    /api/collections        Мои подборки
POST   /api/collections        Создать подборку
GET    /api/collections/{id}   Детали подборки
PUT    /api/collections/{id}   Обновить подборку
DELETE /api/collections/{id}   Удалить подборку
POST   /api/collections/{id}/share Поделиться
```

#### Семейная карта
```
GET    /api/family-card        Информация о карте
POST   /api/family-card        Создать карту
POST   /api/family-card/members Добавить участника
DELETE /api/family-card/members/{id} Удалить участника
```

#### Подписки
```
GET    /api/subscriptions/plans    Тарифные планы
GET    /api/subscriptions/current  Текущая подписка
POST   /api/subscriptions/subscribe Оформить подписку
POST   /api/subscriptions/cancel   Отменить подписку
```

## 📱 PWA Фронтенд

### Структура страниц

| Страница | Описание |
|----------|----------|
| `/` (Home) | Главная со статистикой и предложениями |
| `/catalog` | Каталог скидок с фильтрами |
| `/favorites` | Избранные скидки |
| `/family` | Семейная карта |
| `/collections` | Подборки предложений |
| `/profile` | Профиль и подписка |

### Установка зависимостей
```bash
cd frontend
npm install
```

### Команды
```bash
npm run dev      # Dev сервер
npm run build    # Production сборка
npm run preview  # Preview сборки
npm run lint     # Линтинг
```

## 💰 Монетизация

### Тарифные планы

#### Free (Бесплатно)
- Базовый доступ к скидкам
- Базовая скидка 2%
- До 3 избранных
- Ограниченный доступ к каталогам

#### Premium (299₽/мес)
- Все скидки без ограничений
- Персональные скидки до 50%
- Базовая скидка 3%
- Безлимитное избранное
- Доступ ко всем каталогам
- Приоритетная поддержка

#### Family (499₽/мес)
- Всё из Premium
- До 5 участников семьи
- Общие накопления
- Индивидуальные предложения
- Выгода до 60% vs индивидуальной

## 🕷️ Scraper (Парсер)

Автоматический сбор скидок из источников:

### Поддерживаемые магазины
- Пятёрочка
- Перекрёсток
- Магнит
- Лента
- Дикси
- Ашан

### Планировщик
- Запуск каждые 6 часов
- Автоматическое обновление базы
- Обработка цифровых каталогов

```bash
# Ручной запуск парсера
cd scraper
scrapy crawl grocery_spider

# С планировщиком
python -m schedulers.main
```

## 📊 База данных

### Основные модели
- **User** - Пользователи
- **Store** - Магазины
- **Category** - Категории товаров
- **Discount** - Скидки и акции
- **Collection** - Подборки пользователей
- **FamilyCard** - Семейные карты
- **UserPreference** - Предпочтения пользователей
- **BankOffer** - Банковские предложения
- **Subscription** - Подписки
- **Catalog** - Цифровые каталоги

## 🔧 Конфигурация

### Переменные окружения

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@db:5432/discounts
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

## 📝 Лицензия

MIT License

---

**DiscountHub** © 2024 - Экономьте с умом!
