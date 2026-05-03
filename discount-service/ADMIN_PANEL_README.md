# Админ-панель для управления демоном сбора скидок

## Обзор

Админ-панель предоставляет интерфейс для управления системой сбора скидок из Telegram каналов и веб-сайтов. Доступна только авторизованным пользователям с правами администратора.

## Функционал

### 1. Панель управления (Dashboard)
- **Статистика системы**:
  - Общее количество скидок
  - Активные скидки
  - Проверенные скидки
  - Количество источников данных
  
- **Управление демоном**:
  - Просмотр статуса демона (запущен/остановлен)
  - Запуск демона
  - Остановка демона
  - Принудительный запуск скрапинга
  
- **Быстрые действия**:
  - Переход к управлению скидками
  - Управление источниками данных
  - Управление магазинами

### 2. Управление скидками
- **Просмотр всех скидок** с пагинацией
- **Фильтрация**:
  - По статусу активности
  - По статусу проверки
  - По поисковому запросу
  
- **Редактирование**:
  - Изменение названия и описания
  - Обновление размера скидки
  - Изменение статуса активности
  - Отметка о проверке
  
- **Удаление**:
  - Удаление отдельных скидок
  - Массовое удаление
  
- **Массовые операции**:
  - Массовая проверка скидок
  - Снятие проверки

### 3. Источники данных
- **Просмотр всех источников**:
  - Telegram каналы
  - Веб-сайты
  - RSS ленты
  - API endpoints
  
- **Управление**:
  - Добавление новых источников
  - Редактирование существующих
  - Включение/отключение источников
  - Настройка частоты скрапинга

### 4. Статистика
- Распределение скидок по типам
- Топ магазинов по количеству скидок
- Последние добавленные скидки

## Доступ

### Права администратора
По умолчанию доступ к админ-панели имеют пользователи со следующими email:
- `admin@tolk.ru`
- `admin@example.com`

Для изменения списка администраторов отредактируйте файл `/backend/app/api/routes/admin.py`:

```python
def check_admin_access(current_user: User):
    admin_emails = ["admin@tolk.ru", "admin@example.com", "your@email.com"]
    if current_user.email not in admin_emails and not current_user.is_verified:
        raise ForbiddenException("Admin access required")
    return True
```

### Вход в админ-панель

1. Авторизуйтесь под учетной записью администратора
2. В левом меню появится пункт "Админ-панель" (виден только админам)
3. Нажмите на пункт меню для перехода

## API Endpoints

Все endpoints админ-панели требуют JWT токен авторизации.

### Discounts
- `GET /api/admin/discounts` - Список всех скидок
- `GET /api/admin/discounts/{id}` - Получить скидку по ID
- `POST /api/admin/discounts` - Создать новую скидку
- `PUT /api/admin/discounts/{id}` - Обновить скидку
- `DELETE /api/admin/discounts/{id}` - Удалить скидку
- `POST /api/admin/discounts/bulk-delete` - Массовое удаление
- `POST /api/admin/discounts/bulk-verify` - Массовая проверка

### Daemon Control
- `GET /api/admin/daemon/status` - Статус демона
- `POST /api/admin/daemon/start` - Запустить демон
- `POST /api/admin/daemon/stop` - Остановить демон
- `POST /api/admin/daemon/run-now` - Запустить скрапинг сейчас

### Sources
- `GET /api/admin/daemon/sources` - Список источников
- `POST /api/admin/daemon/sources` - Добавить источник
- `PUT /api/admin/daemon/sources/{id}` - Обновить источник
- `DELETE /api/admin/daemon/sources/{id}` - Удалить источник

### Statistics
- `GET /api/admin/statistics/overview` - Общая статистика

## Безопасность

### Требования
- Обязательная авторизация через JWT токен
- Проверка прав администратора для каждого запроса
- Валидация входных данных

### Рекомендации для production
1. Используйте роль пользователя в БД вместо проверки email
2. Добавьте двухфакторную аутентификацию для админов
3. Ведите лог всех действий администраторов
4. Ограничьте доступ по IP адресам
5. Используйте HTTPS для всех соединений

## Запуск

### Локальная разработка

1. Запустите backend:
```bash
cd discount-service/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Запустите frontend:
```bash
cd discount-service/frontend
npm install
npm run dev
```

3. Откройте браузер:
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### Docker Compose

```bash
cd discount-service
docker-compose up -d
```

Сервисы будут доступны:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin Panel: http://localhost:3000 (кнопка в меню)

## Создание первого администратора

Для создания пользователя с правами администратора:

1. Зарегистрируйтесь через форму регистрации
2. В базе данных обновите поле `is_verified` для вашего пользователя:
```sql
UPDATE users SET is_verified = TRUE WHERE email = 'your@email.com';
```

Или используйте email из списка администраторов по умолчанию.

## Структура файлов

```
discount-service/
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       └── admin.py          # Admin API endpoints
│       └── main.py                    # Main app with admin router
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── AdminPanel.jsx         # Admin panel UI
│       ├── components/
│       │   └── Navigation.jsx         # Nav with admin link
│       └── utils/
│           └── api.js                 # Admin API client
```

## Расширение функционала

### Добавление новых разделов

1. Создайте новый endpoint в `admin.py`
2. Добавьте соответствующий UI компонент
3. Обновите навигацию

### Пример добавления новой метрики

```python
@router.get("/statistics/new-metric", response_model=APIResponse)
async def get_new_metric(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_admin_access(current_user)
    
    # Ваша логика
    metric_value = calculate_metric(db)
    
    return {
        "success": True,
        "data": {"value": metric_value}
    }
```

## Troubleshooting

### Проблема: Не видно кнопку "Админ-панель"
**Решение**: Убедитесь, что:
- Вы авторизованы
- Email пользователя есть в списке администраторов
- Компонент Navigation правильно импортирован

### Проблема: API возвращает 403
**Решение**: Проверьте:
- Наличие JWT токена в заголовках
- Срок действия токена
- Права доступа пользователя

### Проблема: Демон не запускается
**Решение**: 
- Проверьте логи демона
- Убедитесь, что все зависимости установлены
- Проверьте подключение к базе данных

## Поддержка

При возникновении проблем обратитесь к документации проекта или создайте issue в репозитории.
