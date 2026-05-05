# План развития продукта Tolk Discount v3.0

## Обзор задач

Данный документ описывает план развития платформы скидок Tolk до версии 3.0 с добавлением:
1. Нативного мобильного приложения (iOS + Android)
2. PWA (Progressive Web App)
3. Веб-версии с полным функционалом
4. Личного кабинета пользователя

---

## 1. Нативное мобильное приложение (iOS + Android)

### Требования
- **Кроссплатформенная разработка**: Flutter или React Native
- **Легкость и скорость**: 
  - Размер APK/IPA < 50MB
  - Время запуска < 2 секунд
  - Плавная анимация 60 FPS
- **Liquid Glass дизайн**: 
  - Прозрачные элементы с размытием фона
  - Градиентные overlays
  - Glassmorphism эффекты
- **Единый код для iOS и Android**

### Рекомендуемый стек: **Flutter**

#### Преимущества Flutter:
- Единая кодовая база для iOS и Android
- Высокая производительность (компиляция в нативный код)
- Богатые возможности для кастомного дизайна
- Поддержка Material Design 3 и Cupertino (iOS стиль)
- Hot reload для быстрой разработки
- Малый размер приложения при правильной оптимизации

#### Альтернатива: React Native
- Если команда уже знает React
- Возможность переиспользовать логику из веб-версии
- Но сложнее достичь одинакового вида на iOS и Android

### Архитектура мобильного приложения

```
lib/
├── main.dart
├── app/
│   ├── app.dart              # Настройка приложения
│   ├── routes.dart           # Маршрутизация
│   └── theme.dart            # Тема с Liquid Glass
├── core/
│   ├── constants/            # Константы
│   ├── errors/               # Обработка ошибок
│   ├── network/              # API клиент
│   ├── storage/              # Локальное хранилище
│   └── utils/                # Утилиты
├── features/
│   ├── auth/                 # Авторизация и регистрация
│   ├── discounts/            # Скидки
│   ├── profile/              # Личный кабинет
│   ├── collections/          # Подборки
│   ├── family/               # Семейные карты
│   └── settings/             # Настройки
├── shared/
│   ├── widgets/              # Переиспользуемые виджеты
│   │   ├── glass_card.dart   # Liquid Glass карточка
│   │   ├── glass_button.dart
│   │   └── ...
│   └── models/               # Общие модели
└── data/
    ├── repositories/         # Репозитории
    ├── datasources/          # Источники данных
    └── models/               # DTO модели
```

### Liquid Glass дизайн компоненты

#### Основные принципы:
1. **Прозрачность**: background-opacity 10-30%
2. **Размытие**: backdrop-filter blur(10-30px)
3. **Границы**: тонкие белые/прозрачные borders
4. **Тени**: мягкие рассеянные тени
5. **Градиенты**: subtle gradient overlays

#### Flutter реализация:
```dart
class GlassCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.white.withOpacity(0.3),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 20,
                spreadRadius: 5,
              ),
            ],
          ),
          // content
        ),
      ),
    );
  }
}
```

### Функционал мобильного приложения

#### MVP (Минимально жизнеспособный продукт):
- [ ] Регистрация/авторизация (телефон + email)
- [ ] Просмотр лентой скидок
- [ ] Поиск и фильтрация
- [ ] Избранное
- [ ] Личный кабинет
- [ ] Push-уведомления
- [ ] Офлайн режим (кэширование)

#### Версия 1.0:
- [ ] Персональные рекомендации
- [ ] Семейные карты
- [ ] Подборки скидок
- [ ] QR-коды для скидок
- [ ] Геолокация (скидки рядом)
- [ ] Социальный шеринг
- [ ] Аналитика использования

#### Версия 1.1:
- [ ] Биометрическая авторизация (Face ID, Touch ID)
- [ ] Виджеты на главный экран
- [ ] Apple Wallet / Google Pay интеграция
- [ ] Dark mode
- [ ] Мультиязычность

### Технические требования

#### Производительность:
- Cold start < 2s
- Time to interactive < 3s
- 60 FPS анимации
- Memory footprint < 100MB

#### Безопасность:
- HTTPS только
- JWT токены с refresh
- Biometric authentication
- Encrypted local storage
- Certificate pinning

#### Размер приложения:
- APK < 50MB (Android)
- IPA < 50MB (iOS)
- Использование split APKs
- Lazy loading ресурсов

---

## 2. PWA (Progressive Web App)

### Требования
- Аналогичный дизайн с мобильным приложением (Liquid Glass)
- Офлайн работа
- Push-уведомления
- Установка на домашний экран
- Быстрая загрузка

### Техническая реализация

#### Next.js PWA конфигурация:

```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\./i,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 300,
        },
      },
    },
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/i,
      handler: 'CacheFirst',
      options: {
        cacheName: 'images-cache',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 86400,
        },
      },
    },
  ],
});

module.exports = withPWA(nextConfig);
```

#### Manifest.json:
```json
{
  "name": "Tolk Discount",
  "short_name": "Tolk",
  "description": "Платформа скидок и специальных предложений",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "/icons/maskable-icon.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "categories": ["shopping", "finance"],
  "screenshots": [
    {
      "src": "/screenshots/home.png",
      "sizes": "1080x1920",
      "type": "image/png"
    }
  ]
}
```

### PWA функции

#### Офлайн режим:
- Кэширование статических ресурсов
- Offline страница
- Синхронизация при появлении сети
- Background sync

#### Push уведомления:
- Service Worker для push
- VAPID keys
- Токены устройств
- Персонализированные уведомления

#### Установка:
- Add to home screen prompt
- Custom install UI
- Detect install capability

### Оптимизация PWA

#### Performance:
- Lighthouse score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3.5s
- Cumulative Layout Shift < 0.1

#### Core Web Vitals:
- LCP (Largest Contentful Paint) < 2.5s
- FID (First Input Delay) < 100ms
- CLS (Cumulative Layout Shift) < 0.1

---

## 3. Веб-версия с полным функционалом

### Текущее состояние
Уже есть Next.js 14 фронтенд, но нужно расширить функционал.

### Необходимые страницы

#### Публичные страницы:
- [ ] Главная (лендинг)
- [ ] Каталог скидок
- [ ] Страница скидки
- [ ] Категории
- [ ] Магазины
- [ ] О проекте
- [ ] Помощь/FAQ
- [ ] Контакты

#### Защищенные страницы (требуется авторизация):
- [ ] Личный кабинет
- [ ] Профиль пользователя
- [ ] Избранное
- [ ] История просмотров
- [ ] Подборки
- [ ] Семейные карты
- [ ] Подписка
- [ ] Настройки
- [ ] Уведомления

#### Админ панель:
- [ ] Дашборд
- [ ] Управление скидками
- [ ] Управление пользователями
- [ ] Управление магазинами
- [ ] Аналитика
- [ ] Модерация

### Компоненты для веба

#### Liquid Glass дизайн система:
```css
/* globals.css */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
}

.glass-dark {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

#### React компоненты:
```tsx
// components/ui/GlassCard.tsx
export function GlassCard({ children, className }) {
  return (
    <div className={`glass rounded-2xl p-6 ${className}`}>
      {children}
    </div>
  );
}

// components/ui/GlassButton.tsx
export function GlassButton({ children, variant = 'primary' }) {
  const baseClasses = "glass px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:scale-105";
  const variants = {
    primary: "bg-blue-500/20 hover:bg-blue-500/30",
    secondary: "bg-gray-500/20 hover:bg-gray-500/30",
  };
  
  return (
    <button className={`${baseClasses} ${variants[variant]}`}>
      {children}
    </button>
  );
}
```

---

## 4. Личный кабинет пользователя

### Сценарий регистрации

#### Методы регистрации:
1. **По номеру телефона** (основной)
   - Ввод номера
   - SMS код подтверждения
   - Создание пароля (опционально)
   
2. **По email** (альтернативный)
   - Ввод email
   - Письмо с ссылкой подтверждения
   - Создание пароля
   
3. **Социальные сети** (опционально)
   - Google
   - Apple
   - VK
   - Яндекс

#### Форма регистрации:

```typescript
interface RegistrationData {
  // Обязательно
  phone?: string;        // +7 XXX XXX-XX-XX
  email?: string;        // user@example.com
  
  // Опционально при регистрации
  password?: string;     // Минимум 8 символов
  fullName?: string;     // Иван Иванов
  
  // Верификация
  smsCode?: string;      // Код из SMS
  emailToken?: string;   // Токен из письма
  
  // Согласия
  agreeToTerms: boolean;
  agreeToPrivacy: boolean;
  marketingOptIn?: boolean;
}
```

### Функционал личного кабинета

#### Профиль пользователя:
- [ ] Avatar (загрузка/удаление)
- [ ] Имя и фамилия
- [ ] Email (с верификацией)
- [ ] Телефон (с верификацией)
- [ ] Дата рождения (для персональных предложений)
- [ ] Город/регион

#### Статистика использования:
- [ ] Количество сэкономленных рублей
- [ ] Количество использованных скидок
- [ ] Любимые категории
- [ ] Любимые магазины
- [ ] Активность по месяцам (график)
- [ ] Достигнутые уровни/ачивки

#### Персональные предложения:
- [ ] Рекомендации на основе истории
- [ ] Эксклюзивные скидки
- [ ] Ранний доступ к акциям
- [ ] Персональные промокоды

#### Избранное и сохранения:
- [ ] Избранные скидки
- [ ] Сохраненные подборки
- [ ] История просмотров
- [ ] Отложенные покупки

#### Семейные карты:
- [ ] Создание семейной карты
- [ ] Приглашение членов семьи
- [ ] Управление участниками
- [ ] Общая статистика экономии
- [ ] Совместные подборки

#### Подписка:
- [ ] Текущий тариф (Free/Premium/Family)
- [ ] История платежей
- [ ] Смена тарифа
- [ ] Отмена подписки
- [ ] Преимущества каждого тарифа

#### Настройки:
- [ ] Уведомления (push, email, sms)
- [ ] Конфиденциальность
- [ ] Язык интерфейса
- [ ] Тема (светлая/темная/авто)
- [ ] Привязанные устройства
- [ ] Безопасность (пароль, 2FA)

#### Делиться:
- [ ] Поделиться скидкой (соцсети, мессенджеры)
- [ ] Поделиться подборкой
- [ ] Реферальная программа
- [ ] Пригласить друга (бонусы)

### Backend API для личного кабинета

#### Endpoints:

```go
// Auth
POST   /api/v1/auth/register          // Регистрация
POST   /api/v1/auth/login             // Вход
POST   /api/v1/auth/logout            // Выход
POST   /api/v1/auth/refresh           // Refresh token
POST   /api/v1/auth/verify-sms        // Подтверждение SMS
POST   /api/v1/auth/verify-email      // Подтверждение email
POST   /api/v1/auth/forgot-password   // Запрос сброса пароля
POST   /api/v1/auth/reset-password    // Сброс пароля

// Profile
GET    /api/v1/profile                // Получить профиль
PUT    /api/v1/profile                // Обновить профиль
DELETE /api/v1/profile                // Удалить аккаунт
POST   /api/v1/profile/avatar        // Загрузить аватар
DELETE /api/v1/profile/avatar        // Удалить аватар

// Statistics
GET    /api/v1/statistics/summary     // Общая статистика
GET    /api/v1/statistics/savings     // Экономия по периодам
GET    /api/v1/statistics/categories  // Статистика по категориям
GET    /api/v1/statistics/shops       // Статистика по магазинам

// Favorites
GET    /api/v1/favorites              // Список избранного
POST   /api/v1/favorites/{id}         // Добавить в избранное
DELETE /api/v1/favorites/{id}         // Удалить из избранного

// History
GET    /api/v1/history/views         // История просмотров
GET    /api/v1/history/used          // Использованные скидки

// Personal offers
GET    /api/v1/offers/personal       // Персональные предложения
GET    /api/v1/offers/exclusive      // Эксклюзивные предложения

// Family cards
GET    /api/v1/family-cards          // Мои семейные карты
POST   /api/v1/family-cards          // Создать карту
PUT    /api/v1/family-cards/{id}     // Обновить карту
DELETE /api/v1/family-cards/{id}     // Удалить карту
POST   /api/v1/family-cards/{id}/invite  // Пригласить участника
DELETE /api/v1/family-cards/{id}/members/{memberId}  // Удалить участника

// Subscription
GET    /api/v1/subscription/current  // Текущая подписка
GET    /api/v1/subscription/plans    // Доступные тарифы
POST   /api/v1/subscription/subscribe // Оформить подписку
POST   /api/v1/subscription/cancel   // Отменить подписку
GET    /api/v1/subscription/payments // История платежей

// Settings
GET    /api/v1/settings              // Получить настройки
PUT    /api/v1/settings              // Обновить настройки
PUT    /api/v1/settings/notifications // Настройки уведомлений
PUT    /api/v1/settings/privacy      // Настройки приватности

// Sharing
POST   /api/v1/share/discount/{id}   // Поделиться скидкой
POST   /api/v1/share/collection/{id} // Поделиться подборкой
GET    /api/v1/referrals             // Реферальная статистика
POST   /api/v1/referrals/invite      // Пригласить друга
```

### Модели данных

#### User (расширенная):
```go
type User struct {
    ID                int64          `json:"id"`
    Email             string         `json:"email"`
    EmailVerified     bool           `json:"email_verified"`
    Phone             string         `json:"phone"`
    PhoneVerified     bool           `json:"phone_verified"`
    PasswordHash      string         `json:"-"`
    FullName          string         `json:"full_name"`
    AvatarURL         string         `json:"avatar_url"`
    DateOfBirth       *time.Time     `json:"date_of_birth"`
    City              string         `json:"city"`
    
    SubscriptionTier  SubscriptionTier `json:"subscription_tier"`
    SubscriptionStart *time.Time     `json:"subscription_start"`
    SubscriptionEnd   *time.Time     `json:"subscription_end"`
    
    Settings          UserSettings   `json:"settings"`
    
    TotalSavings      float64        `json:"total_savings"`
    DiscountsUsed     int64          `json:"discounts_used"`
    Level             int            `json:"level"`
    Points            int64          `json:"points"`
    
    IsActive          bool           `json:"is_active"`
    IsDeleted         bool           `json:"is_deleted"`
    LastLoginAt       *time.Time     `json:"last_login_at"`
    CreatedAt         time.Time      `json:"created_at"`
    UpdatedAt         *time.Time     `json:"updated_at"`
}

type UserSettings struct {
    Notifications     NotificationSettings `json:"notifications"`
    Privacy           PrivacySettings      `json:"privacy"`
    Language          string               `json:"language"`
    Theme             string               `json:"theme"`
    Timezone          string               `json:"timezone"`
}

type NotificationSettings struct {
    PushEnabled       bool `json:"push_enabled"`
    EmailEnabled      bool `json:"email_enabled"`
    SMSEnabled        bool `json:"sms_enabled"`
    NewDiscounts      bool `json:"new_discounts"`
    PriceDrops        bool `json:"price_drops"`
    PersonalOffers    bool `json:"personal_offers"`
    FamilyActivity    bool `json:"family_activity"`
    Marketing         bool `json:"marketing"`
}

type PrivacySettings struct {
    ProfileVisibility   string `json:"profile_visibility"` // public, friends, private
    ShowSavings         bool   `json:"show_savings"`
    ShowActivity        bool   `json:"show_activity"`
    AllowPersonalization bool  `json:"allow_personalization"`
}
```

#### SMS Verification:
```go
type SMSVerification struct {
    ID          int64     `json:"id"`
    Phone       string    `json:"phone"`
    Code        string    `json:"-"`  // Hashed
    ExpiresAt   time.Time `json:"expires_at"`
    IsUsed      bool      `json:"is_used"`
    Attempts    int       `json:"attempts"`
    CreatedAt   time.Time `json:"created_at"`
}
```

#### UserStatistics:
```go
type UserStatistics struct {
    UserID          int64              `json:"user_id"`
    TotalSavings    float64            `json:"total_savings"`
    DiscountsUsed   int64              `json:"discounts_used"`
    FavoritesCount  int64              `json:"favorites_count"`
    CollectionsCount int64             `json:"collections_count"`
    
    ByCategory      []CategoryStat     `json:"by_category"`
    ByMonth         []MonthlyStat      `json:"by_month"`
    ByShop          []ShopStat         `json:"by_shop"`
    
    Level           int                `json:"level"`
    Points          int64              `json:"points"`
    Achievements    []Achievement      `json:"achievements"`
    
    UpdatedAt       time.Time          `json:"updated_at"`
}

type CategoryStat struct {
    CategoryID    int64   `json:"category_id"`
    CategoryName  string  `json:"category_name"`
    DiscountsUsed int64   `json:"discounts_used"`
    Savings       float64 `json:"savings"`
}

type MonthlyStat struct {
    Month         string  `json:"month"`  // YYYY-MM
    DiscountsUsed int64   `json:"discounts_used"`
    Savings       float64 `json:"savings"`
}
```

---

## Roadmap реализации

### Этап 1: Подготовка (2 недели)
- [ ] Дизайн-система Liquid Glass
- [ ] Настройка репозитория мобильного приложения
- [ ] Настройка CI/CD для мобильных приложений
- [ ] Расширение backend API для личного кабинета

### Этап 2: Личный кабинет (3 недели)
- [ ] Регистрация по телефону (SMS)
- [ ] Регистрация по email
- [ ] Профиль пользователя
- [ ] Базовая статистика
- [ ] Настройки

### Этап 3: PWA (2 недели)
- [ ] Service Worker
- [ ] Manifest
- [ ] Offline режим
- [ ] Push уведомления
- [ ] Оптимизация производительности

### Этап 4: Мобильное приложение MVP (6 недель)
- [ ] Базовая навигация
- [ ] Авторизация/Регистрация
- [ ] Лента скидок
- [ ] Поиск
- [ ] Избранное
- [ ] Профиль

### Этап 5: Полный функционал (4 недели)
- [ ] Персональные рекомендации
- [ ] Семейные карты
- [ ] Подборки
- [ ] Социальный шеринг
- [ ] Аналитика

### Этап 6: Полировка и релиз (2 недели)
- [ ] Тестирование
- [ ] Оптимизация производительности
- [ ] Баг фиксы
- [ ] Публикация в App Store и Google Play
- [ ] Маркетинг

**Итого: ~19 недель (~4.5 месяца)**

---

## Команда и ресурсы

### Необходимые роли:
- 1-2 Flutter разработчика
- 1 Frontend разработчик (Next.js)
- 1 Backend разработчик (Go)
- 1 UI/UX дизайнер
- 1 QA инженер
- 1 DevOps (частичная занятость)

### Инструменты:
- **Мобильная разработка**: Flutter, Android Studio, Xcode
- **Веб**: Next.js, TypeScript, TailwindCSS
- **Backend**: Go, PostgreSQL, Redis
- **Дизайн**: Figma
- **CI/CD**: GitHub Actions, Fastlane
- **Мониторинг**: Firebase Crashlytics, Sentry
- **Аналитика**: Firebase Analytics, Amplitude

---

## Метрики успеха

### Технические метрики:
- App size < 50MB
- Cold start < 2s
- Lighthouse score > 90
- API latency p99 < 100ms
- Uptime > 99.9%

### Бизнес метрики:
- Количество установок
- DAU/MAU (Daily/Monthly Active Users)
- Retention rate (Day 1, Day 7, Day 30)
- Conversion to registration
- Average session duration
- Number of discounts used per user

---

## Риски и митигация

| Риск | Вероятность | Влияние | Митигация |
|------|------------|---------|-----------|
| Сложности с Liquid Glass на разных устройствах | Средняя | Средняя | Тестирование на множестве устройств, fallback стили |
| Проблемы с производительностью Flutter | Низкая | Средняя | Профилирование, оптимизация, использование native modules |
| Задержки с публикацией в App Store | Средняя | Высокая | Начать процесс ревью заранее, иметь beta канал |
| SMS шлюз ненадежен | Средняя | Высокая | Несколько провайдеров, fallback на email |
| Масштабирование backend | Низкая | Высокая | Load testing, auto-scaling, caching |

---

## Заключение

Данный план описывает комплексное развитие платформы Tolk Discount до версии 3.0 с фокусом на:
1. **Мобильность** - нативное приложение для максимального UX
2. **Доступность** - PWA для пользователей без установки
3. **Персонализация** - личный кабинет с полной статистикой
4. **Дизайн** - современный Liquid Glass стиль на всех платформах

Реализация плана займет approximately 4-5 месяцев с командой из 5-7 человек.
