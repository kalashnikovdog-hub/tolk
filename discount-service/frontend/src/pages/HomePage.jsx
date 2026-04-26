import { motion } from 'framer-motion'
import { Star, TrendingUp, Clock, Shield } from 'lucide-react'

const HomePage = () => {
  const featuredCategories = [
    { id: 1, name: 'Продукты', icon: '🛒', color: 'from-green-400 to-emerald-500' },
    { id: 2, name: 'Электроника', icon: '📱', color: 'from-blue-400 to-indigo-500' },
    { id: 3, name: 'Одежда', icon: '👕', color: 'from-purple-400 to-pink-500' },
    { id: 4, name: 'Дом', icon: '🏠', color: 'from-orange-400 to-red-500' },
    { id: 5, name: 'Красота', icon: '💄', color: 'from-pink-400 to-rose-500' },
    { id: 6, name: 'Спорт', icon: '⚽', color: 'from-teal-400 to-cyan-500' },
  ]

  const topStores = [
    { id: 1, name: 'Пятёрочка', discounts: 45, logo: '🟢' },
    { id: 2, name: 'Перекрёсток', discounts: 38, logo: '🔴' },
    { id: 3, name: 'Магнит', discounts: 32, logo: '🟣' },
    { id: 4, name: 'Лента', discounts: 28, logo: '🔵' },
  ]

  const bankOffers = [
    { 
      id: 1, 
      bank: 'Тинькофф', 
      category: 'Рестораны', 
      discount: 30, 
      color: 'bg-yellow-400' 
    },
    { 
      id: 2, 
      bank: 'Сбер', 
      category: 'АЗС', 
      discount: 20, 
      color: 'bg-green-400' 
    },
    { 
      id: 3, 
      bank: 'Альфа', 
      category: 'Такси', 
      discount: 25, 
      color: 'bg-red-400' 
    },
  ]

  return (
    <div className="space-y-6 pb-20 md:pb-6">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-primary-500 via-primary-600 to-accent-500 rounded-2xl p-6 text-white shadow-glow"
      >
        <h2 className="text-2xl md:text-3xl font-bold mb-2">
          Экономьте до 70% на покупках
        </h2>
        <p className="text-primary-100 mb-4">
          Тысячи скидок, промокодов и кэшбэков в одном месте
        </p>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2 bg-white/20 px-3 py-2 rounded-lg backdrop-blur-sm">
            <Star className="w-4 h-4" />
            <span>10,000+ скидок</span>
          </div>
          <div className="flex items-center gap-2 bg-white/20 px-3 py-2 rounded-lg backdrop-blur-sm">
            <TrendingUp className="w-4 h-4" />
            <span>500+ магазинов</span>
          </div>
          <div className="flex items-center gap-2 bg-white/20 px-3 py-2 rounded-lg backdrop-blur-sm">
            <Shield className="w-4 h-4" />
            <span>Гарантия лучшей цены</span>
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Активных скидок', value: '2,847', icon: '🏷️' },
          { label: 'Магазинов', value: '523', icon: '🏪' },
          { label: 'Пользователей', value: '45K', icon: '👥' },
          { label: 'Сэкономлено', value: '12M ₽', icon: '💰' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="card p-4 text-center"
          >
            <div className="text-2xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-xs text-gray-500">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Featured Categories */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">Категории</h3>
          <button className="text-primary-600 text-sm font-medium hover:underline">
            Все категории
          </button>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {featuredCategories.map((category) => (
            <motion.button
              key={category.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`bg-gradient-to-br ${category.color} p-4 rounded-xl text-white shadow-card hover:shadow-card-hover transition-all`}
            >
              <div className="text-3xl mb-2">{category.icon}</div>
              <div className="text-sm font-medium">{category.name}</div>
            </motion.button>
          ))}
        </div>
      </section>

      {/* Top Stores */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">Популярные магазины</h3>
          <button className="text-primary-600 text-sm font-medium hover:underline">
            Все магазины
          </button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {topStores.map((store) => (
            <motion.div
              key={store.id}
              whileHover={{ scale: 1.02 }}
              className="card p-4 cursor-pointer"
            >
              <div className="text-3xl mb-2">{store.logo}</div>
              <h4 className="font-semibold text-gray-900 mb-1">{store.name}</h4>
              <div className="flex items-center gap-2">
                <span className="badge badge-primary">{store.discounts} скидок</span>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Bank Offers of the Month */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-900">Банковские предложения</h3>
            <p className="text-sm text-gray-500">Специальные категории этого месяца</p>
          </div>
          <Clock className="w-6 h-6 text-accent-500" />
        </div>
        <div className="space-y-3">
          {bankOffers.map((offer, index) => (
            <motion.div
              key={offer.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`${offer.color} rounded-xl p-4 text-white shadow-card hover:shadow-card-hover transition-all cursor-pointer`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-lg">{offer.bank}</h4>
                  <p className="text-white/90">Категория: {offer.category}</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold">-{offer.discount}%</div>
                  <div className="text-sm text-white/90">кэшбэк</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Base Discount Banner */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-gradient-to-r from-discount-light to-yellow-50 border-2 border-discount rounded-xl p-6"
      >
        <div className="flex items-center gap-4">
          <div className="bg-discount text-white p-3 rounded-full">
            <Percent className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-gray-900 mb-1">
              Базовая скидка 2-3%
            </h4>
            <p className="text-sm text-gray-600">
              На все товары даже без специальных предложений
            </p>
          </div>
          <button className="btn-primary whitespace-nowrap">
            Подробнее
          </button>
        </div>
      </motion.div>

      {/* CTA for Premium */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 text-white"
      >
        <h3 className="text-xl font-bold mb-2">Premium подписка</h3>
        <ul className="space-y-2 mb-4 text-sm text-gray-300">
          <li className="flex items-center gap-2">
            <Star className="w-4 h-4 text-yellow-400" />
            Персональные скидки до 50%
          </li>
          <li className="flex items-center gap-2">
            <Users className="w-4 h-4 text-yellow-400" />
            Семейная карта до 5 участников
          </li>
          <li className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-yellow-400" />
            Доступ ко всем каталогам
          </li>
        </ul>
        <button className="btn-accent w-full">
          Попробовать бесплатно 7 дней
        </button>
      </motion.div>
    </div>
  )
}

export default HomePage
