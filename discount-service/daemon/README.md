# Discount Daemon

Сервис для автоматического сбора скидок из Telegram каналов и веб-сайтов.

## Возможности

- **Автоматический сбор по расписанию**: Парсинг сайтов и Telegram каналов через заданные интервалы
- **Ручной запуск**: Возможность запуска сбора по команде
- **Telegram мониторинг**: Отслеживание скидок в указанных Telegram каналах
- **Веб-скрапинг**: Парсинг сайтов магазинов на наличие акций
- **Дедупликация**: Автоматическая проверка на дубликаты перед сохранением
- **Очистка старых данных**: Автоматическое архивирование устаревших скидок

## Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` или экспортируйте переменные:

```bash
# База данных
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/discounts

# Telegram API (получить на https://my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION=discount_daemon.session

# Каналы для мониторинга (через запятую)
TELEGRAM_CHANNELS=skidki_online,golddays,edadeal

# Интервал скрапинга в часах
SCRAPE_INTERVAL=6

# Сайты для парсинга (JSON)
TARGET_WEBSITES='[
    {"name": "Пятерочка", "url": "https://5ka.ru/promo", "type": "grocery"},
    {"name": "Перекресток", "url": "https://perekrestok.ru/catalog/promo", "type": "grocery"}
]'
```

## Использование

### Запуск в режиме демона (постоянная работа)

```bash
python discount_daemon.py --command run
```

Демон будет:
- Запускать полный цикл сбора каждые 6 часов (настраивается)
- Проверять Telegram каналы каждые 30 минут
- Очищать старые данные каждый день в 3:00

### Однократный запуск парсинга сайтов

```bash
python discount_daemon.py --command scrape
```

### Однократная проверка Telegram

```bash
python discount_daemon.py --command telegram
```

### Проверка статуса

```bash
python discount_daemon.py --command status
```

## Запуск в Docker

### Сборка образа

```bash
docker build -t discount-daemon .
```

### Запуск контейнера

```bash
docker run -d \
  --name discount-daemon \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/discounts \
  -e TELEGRAM_API_ID=your_api_id \
  -e TELEGRAM_API_HASH=your_api_hash \
  -e TELEGRAM_CHANNELS=skidki_online,golddays \
  discount-daemon
```

### Через docker-compose

Добавьте сервис в ваш `docker-compose.yml`:

```yaml
services:
  daemon:
    build:
      context: ./daemon
      dockerfile: Dockerfile
    container_name: discount_daemon
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/discounts
      TELEGRAM_API_ID: ${TELEGRAM_API_ID}
      TELEGRAM_API_HASH: ${TELEGRAM_API_HASH}
      TELEGRAM_CHANNELS: skidki_online,golddays,edadeal
      SCRAPE_INTERVAL: 6
    depends_on:
      - postgres
    restart: unless-stopped
    volumes:
      - ./logs:/var/log
```

## Расписание задач

| Задача | Частота | Описание |
|--------|---------|----------|
| Основной цикл сбора | Каждые 6 часов | Парсинг сайтов + Telegram |
| Проверка Telegram | Каждые 30 минут | Мониторинг новых сообщений |
| Очистка данных | Ежедневно в 3:00 | Архивация старых скидок |

## Логи

Логи сохраняются в:
- Консоль (stdout)
- Файл `/var/log/discount_daemon.log`

## Структура базы данных

Демон использует существующую базу данных со следующими таблицами:

- `discounts` - основные данные о скидках
- `stores` - магазины/источники скидок
- `categories` - категории товаров

## Добавление новых источников

### Telegram каналы

Добавьте названия каналов в переменную `TELEGRAM_CHANNELS`:

```bash
TELEGRAM_CHANNELS=channel1,channel2,channel3
```

### Веб-сайты

Добавьте сайты в `TARGET_WEBSITES`:

```json
[
  {"name": "Название", "url": "https://site.com", "type": "grocery"}
]
```

Типы сайтов: `grocery`, `electronics`, `clothing`, `services`, `restaurant`, `online`, `other`

## Требования к Telegram API

Для работы с Telegram каналами необходимо:

1. Зарегистрировать приложение на https://my.telegram.org
2. Получить `API_ID` и `API_HASH`
3. При первом запуске ввести номер телефона и код подтверждения

**Примечание**: Для доступа к закрытым каналам аккаунт должен быть их участником.

## Лицензия

MIT
