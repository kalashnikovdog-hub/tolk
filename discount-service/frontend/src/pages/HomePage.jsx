import { motion } from 'framer-motion'
import { Star, TrendingUp, Clock, Shield, Percent, Users, BookOpen } from 'lucide-react'

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
      color: 'from-yellow-400 to-orange-500' 
    },
    { 
      id: 2, 
      bank: 'Сбер', 
      category: 'АЗС', 
      discount: 20, 
      color: 'from-green-400 to-emerald-500' 
    },
    { 
      id: 3, 
      bank: 'Альфа', 
      category: 'Такси', 
      discount: 25, 
      color: 'from-red-400 to-rose-500' 
    },
  ]

  return (
    <div className="space-y-6 pb-20 md:pb-6">
      {/* Hero Section - Liquid Glass */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="hero-liquid text-gray-900"
      >
        <h2 className="text-2xl md:text-3xl font-bold mb-3 text-glow">
          Экономьте до 70% на покупках
        </h2>
        <p className="text-gray-700 mb-5 font-medium">
          Тысячи скидок, промокодов и кэшбэков в одном месте
        </p>
        <div className="flex flex-wrap gap-3 text-sm">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-2 glass-card-premium px-4 py-2.5 backdrop-blur-md"
          >
            <Star className="w-4 h-4 text-primary-600 fill-current" />
            <span className="font-semibold">10,000+ скидок</span>
          </motion.div>
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-2 glass-card-premium px-4 py-2.5 backdrop-blur-md"
          >
            <TrendingUp className="w-4 h-4 text-accent-600" />
            <span className="font-semibold">500+ магазинов</span>
          </motion.div>
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-2 glass-card-premium px-4 py-2.5 backdrop-blur-md"
          >
            <Shield className="w-4 h-4 text-emerald-600" />
            <span className="font-semibold">Гарантия лучшей цены</span>
          </motion.div>
        </div>
      </motion.div>

      {/* Quick Stats - Glass Cards */}
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
            whileHover={{ scale: 1.05, y: -4 }}
            className="stat-glass float-animation"
            style={{ animationDelay: `${index * 0.5}s` }}
          >
            <div className="text-3xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">{stat.value}</div>
            <div className="text-xs text-gray-600 font-medium">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Featured Categories - Liquid */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white/90 drop-shadow-lg">Категории</h3>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="glass-card-premium px-4 py-2 text-sm font-semibold text-primary-600 hover:text-primary-700"
          >
            Все категории
          </motion.button>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {featuredCategories.map((category) => (
            <motion.button
              key={category.id}
              whileHover={{ scale: 1.1, rotate: 3 }}
              whileTap={{ scale: 0.95 }}
              className={`category-liquid bg-gradient-to-br ${category.color} text-white shadow-lg`}
            >
              <div className="text-4xl mb-2 drop-shadow-lg">{category.icon}</div>
              <div className="text-sm font-bold drop-shadow-md">{category.name}</div>
            </motion.button>
          ))}
        </div>
      </section>

      {/* Top Stores - Glass */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white/90 drop-shadow-lg">Популярные магазины</h3>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="glass-card-premium px-4 py-2 text-sm font-semibold text-primary-600 hover:text-primary-700"
          >
            Все магазины
          </motion.button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {topStores.map((store) => (
            <motion.div
              key={store.id}
              whileHover={{ scale: 1.05, y: -4 }}
              className="glass-card-premium p-4 cursor-pointer"
            >
              <div className="text-4xl mb-3">{store.logo}</div>
              <h4 className="font-bold text-gray-900 mb-2">{store.name}</h4>
              <div className="flex items-center gap-2">
                <span className="badge-glass-primary font-semibold">{store.discounts} скидок</span>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Bank Offers of the Month - Gradient Glass */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold text-white/90 drop-shadow-lg">Банковские предложения</h3>
            <p className="text-sm text-white/70">Специальные категории этого месяца</p>
          </div>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            <Clock className="w-7 h-7 text-white/90 drop-shadow-lg" />
          </motion.div>
        </div>
        <div className="space-y-3">
          {bankOffers.map((offer, index) => (
            <motion.div
              key={offer.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02, x: 4 }}
              className={`bg-gradient-to-r ${offer.color} rounded-2xl p-5 text-white shadow-glass hover:shadow-glass-hover transition-all cursor-pointer overflow-hidden relative`}
            >
              {/* Shimmer overlay */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full hover:translate-x-full transition-transform duration-700" />
              
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <h4 className="font-bold text-xl drop-shadow-lg">{offer.bank}</h4>
                  <p className="text-white/90 font-medium">Категория: {offer.category}</p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-black drop-shadow-lg">-{offer.discount}%</div>
                  <div className="text-sm text-white/90 font-medium">кэшбэк</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Base Discount Banner - Liquid Glass */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass-card-premium p-6 border-2 border-discount/50"
      >
        <div className="flex items-center gap-5">
          <motion.div 
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="bg-gradient-to-br from-discount to-discount-dark text-white p-4 rounded-2xl shadow-lg"
          >
            <Percent className="w-9 h-9" />
          </motion.div>
          <div className="flex-1">
            <h4 className="font-bold text-gray-900 text-lg mb-1">
              Базовая скидка 2-3%
            </h4>
            <p className="text-sm text-gray-700 font-medium">
              На все товары даже без специальных предложений
            </p>
          </div>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-liquid-primary whitespace-nowrap"
          >
            Подробнее
          </motion.button>
        </div>
      </motion.div>

      {/* CTA for Premium - Dark Glass */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card-dark p-6 bg-gradient-to-br from-gray-900/90 to-gray-800/90 backdrop-blur-xl"
      >
        <h3 className="text-xl font-bold mb-4 text-white">Premium подписка</h3>
        <ul className="space-y-3 mb-5 text-sm text-white/90">
          <motion.li 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-3"
          >
            <div className="bg-yellow-400/20 p-1.5 rounded-lg">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
            </div>
            Персональные скидки до 50%
          </motion.li>
          <motion.li 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-3"
          >
            <div className="bg-primary-400/20 p-1.5 rounded-lg">
              <Users className="w-4 h-4 text-primary-400" />
            </div>
            Семейная карта до 5 участников
          </motion.li>
          <motion.li 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-3"
          >
            <div className="bg-accent-400/20 p-1.5 rounded-lg">
              <BookOpen className="w-4 h-4 text-accent-400" />
            </div>
            Доступ ко всем каталогам
          </motion.li>
        </ul>
        <motion.button 
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
          className="btn-accent w-full font-semibold"
        >
          Попробовать бесплатно 7 дней
        </motion.button>
      </motion.div>
    </div>
  )
}

export default HomePage
