# Tolk PWA - Фронтенд

Современное Progressive Web App для поиска и управления скидками.

## 🚀 Технологии

- **React 18** - UI библиотека
- **Vite** - Сборщик и dev-сервер
- **Tailwind CSS** - Стилизация
- **Framer Motion** - Анимации
- **Zustand** - Управление состоянием
- **React Router v6** - Роутинг
- **Vite PWA Plugin** - PWA функционал

## ✨ Особенности

### PWA Возможности
- 📱 Установка на устройства (iOS/Android)
- 💾 Офлайн работа с кэшированием
- 🔔 Push уведомления
- ⚡ Быстрая загрузка
- 🎯 Адаптивный дизайн

### Функционал
- 🏠 Главная страница со статистикой и предложениями
- 🔍 Каталог скидок с фильтрацией
- ❤️ Избранное
- 👨‍👩‍👧‍👦 Семейная карта
- 📚 Подборки предложений
- 👤 Профиль пользователя с подпиской

## 🛠️ Установка

```bash
# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev

# Сборка для production
npm run build

# Preview production сборки
npm run preview
```

## 📁 Структура проекта

```
frontend/
├── public/              # Статические файлы
│   ├── favicon.svg
│   └── ...
├── src/
│   ├── components/      # Переиспользуемые компоненты
│   │   ├── DiscountCard.jsx
│   │   ├── SearchFilter.jsx
│   │   └── Navigation.jsx
│   ├── pages/          # Страницы приложения
│   │   └── HomePage.jsx
│   ├── hooks/          # Custom hooks и stores
│   │   └── stores.js
│   ├── utils/          # Утилиты и API
│   │   └── api.js
│   ├── styles/         # Глобальные стили
│   │   └── index.css
│   ├── App.jsx         # Главный компонент
│   └── main.jsx        # Точка входа
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## 🎨 Дизайн-система

### Цвета
- **Primary**: `#10B981` (изумрудный) - основные действия
- **Accent**: `#EF4444` (красный) - акценты и скидки
- **Discount**: `#F59E0B` (янтарный) - специальные предложения

### Компоненты
- `btn-primary` - Основная кнопка
- `btn-secondary` - Вторичная кнопка
- `btn-accent` - Акцентная кнопка
- `card` - Карточка контента
- `badge` - Бейдж/тег

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🔌 API Integration

Все API запросы настроены через `src/utils/api.js`. 
Базовый URL берётся из переменной окружения `VITE_API_URL`.

## 🚀 Production

### Docker
```bash
docker build -t discount-pwa .
docker run -p 80:80 discount-pwa
```

### Хостинг
Поддерживает любой статический хостинг:
- Vercel
- Netlify
- GitHub Pages
- Cloudflare Pages

## 📝 Лицензия

MIT
