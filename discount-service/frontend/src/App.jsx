import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navigation from './components/Navigation'
import DiscountCard from './components/DiscountCard'
import SearchFilter from './components/SearchFilter'
import HomePage from './pages/HomePage'
import AdminPanel from './pages/AdminPanel'
import { useUIStore, useDiscountStore } from './hooks/stores'
import { discountAPI } from './utils/api'
import { Percent, BookOpen, Heart, Users, CreditCard } from 'lucide-react'

function App() {
  const { currentTab } = useUIStore()
  const { discounts, favorites, setDiscounts, addFavorite, removeFavorite, filters, setFilters, resetFilters } = useDiscountStore()
  const [categories, setCategories] = useState([])
  const [stores, setStores] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchValue, setSearchValue] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    loadDiscounts()
  }, [filters])

  const loadData = async () => {
    try {
      const [catsRes, storesRes] = await Promise.all([
        discountAPI.getCategories(),
        discountAPI.getStores()
      ])
      setCategories(catsRes.data)
      setStores(storesRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadDiscounts = async () => {
    try {
      const params = {}
      if (filters.category) params.category_id = filters.category
      if (filters.store) params.store_id = filters.store
      if (filters.minDiscount) params.min_discount = filters.minDiscount
      if (searchValue) params.search = searchValue

      const response = await discountAPI.getAll(params)
      setDiscounts(response.data)
    } catch (error) {
      console.error('Failed to load discounts:', error)
    }
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }

  const toggleFavorite = (id) => {
    if (favorites.includes(id)) {
      removeFavorite(id)
    } else {
      addFavorite(id)
    }
  }

  const renderContent = () => {
    // Admin panel is a separate full-page component
    if (currentTab === 'admin') {
      return <AdminPanel />
    }
    
    switch (currentTab) {
      case 'home':
        return <HomePage />
      
      case 'catalog':
        return (
          <div className="space-y-6 pb-20 md:pb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Каталог скидок</h2>
              <p className="text-gray-600">Найдите лучшие предложения для себя</p>
            </div>
            
            <SearchFilter
              searchValue={searchValue}
              onSearchChange={setSearchValue}
              categories={categories}
              stores={stores}
              filters={filters}
              onFilterChange={handleFilterChange}
              onReset={resetFilters}
            />
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
              </div>
            ) : (
              <div className="catalog-grid">
                {discounts.map((discount) => (
                  <DiscountCard
                    key={discount.id}
                    discount={discount}
                    isFavorite={favorites.includes(discount.id)}
                    onFavorite={toggleFavorite}
                  />
                ))}
              </div>
            )}
          </div>
        )
      
      case 'favorites':
        const favoriteDiscounts = discounts.filter(d => favorites.includes(d.id))
        return (
          <div className="space-y-6 pb-20 md:pb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Избранное</h2>
              <p className="text-gray-600">Ваши сохранённые скидки</p>
            </div>
            
            {favoriteDiscounts.length === 0 ? (
              <div className="card p-8 text-center">
                <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Пока нет избранных
                </h3>
                <p className="text-gray-600 mb-4">
                  Добавляйте скидки в избранное, чтобы не потерять их
                </p>
                <button 
                  onClick={() => useUIStore.getState().setTab('catalog')}
                  className="btn-primary"
                >
                  Перейти в каталог
                </button>
              </div>
            ) : (
              <div className="catalog-grid">
                {favoriteDiscounts.map((discount) => (
                  <DiscountCard
                    key={discount.id}
                    discount={discount}
                    isFavorite={true}
                    onFavorite={toggleFavorite}
                  />
                ))}
              </div>
            )}
          </div>
        )
      
      case 'family':
        return (
          <div className="space-y-6 pb-20 md:pb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Семейная карта</h2>
              <p className="text-gray-600">Объедините семью для общих скидок</p>
            </div>
            
            <div className="card p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-4 rounded-xl">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Family Premium</h3>
                  <p className="text-sm text-gray-600">До 5 участников семьи</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Вы (Организатор)</p>
                    <p className="text-sm text-gray-600">active</p>
                  </div>
                  <span className="badge badge-primary">Активен</span>
                </div>
                
                <button className="btn-secondary w-full py-3 border-dashed border-2">
                  + Пригласить участника
                </button>
              </div>
            </div>
            
            <div className="card p-6 bg-gradient-to-br from-accent-50 to-white">
              <h4 className="font-bold text-gray-900 mb-2">Преимущества семейной карты</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  Общие скидки для всех участников
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  Накопление баллов всей семьёй
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  Персональные предложения для каждого
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  Выгоднее индивидуальной подписки
                </li>
              </ul>
            </div>
          </div>
        )
      
      case 'collections':
        return (
          <div className="space-y-6 pb-20 md:pb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Мои подборки</h2>
              <p className="text-gray-600">Создавайте и делитесь коллекциями скидок</p>
            </div>
            
            <button className="btn-primary w-full flex items-center justify-center gap-2">
              <BookOpen className="w-5 h-5" />
              Создать новую подборку
            </button>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3].map((i) => (
                <motion.div
                  key={i}
                  whileHover={{ scale: 1.02 }}
                  className="card p-4 cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-900">Подборка #{i}</h4>
                      <p className="text-sm text-gray-600">5 товаров • Публичная</p>
                    </div>
                    <button className="p-2 hover:bg-gray-100 rounded-lg">
                      <Heart className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-16 h-16 bg-gray-100 rounded-lg"></div>
                    <div className="w-16 h-16 bg-gray-100 rounded-lg"></div>
                    <div className="w-16 h-16 bg-gray-100 rounded-lg"></div>
                    <div className="w-16 h-16 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600 font-medium">
                      +2
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )
      
      case 'profile':
        return (
          <div className="space-y-6 pb-20 md:pb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Профиль</h2>
              <p className="text-gray-600">Управление аккаунтом и подпиской</p>
            </div>
            
            {/* Profile Card */}
            <div className="card p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  A
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Александр Петров</h3>
                  <p className="text-sm text-gray-600">alex@example.com</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <button className="btn-secondary w-full justify-start">
                  Редактировать профиль
                </button>
                <button className="btn-secondary w-full justify-start">
                  Настройки уведомлений
                </button>
                <button className="btn-secondary w-full justify-start">
                  История покупок
                </button>
              </div>
            </div>
            
            {/* Subscription Status */}
            <div className="card p-6 bg-gradient-to-br from-primary-50 to-white border border-primary-100">
              <div className="flex items-center gap-3 mb-4">
                <CreditCard className="w-6 h-6 text-primary-600" />
                <h3 className="font-bold text-gray-900">Premium подписка</h3>
              </div>
              
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Действует до</span>
                  <span className="font-medium text-gray-900">15.02.2024</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>
              
              <button className="btn-primary w-full">
                Продлить подписку
              </button>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="card p-4 text-center">
                <div className="text-2xl font-bold text-primary-600">2,450 ₽</div>
                <div className="text-xs text-gray-600">Сэкономлено</div>
              </div>
              <div className="card p-4 text-center">
                <div className="text-2xl font-bold text-accent-600">47</div>
                <div className="text-xs text-gray-600">Использовано скидок</div>
              </div>
            </div>
            
            <button className="btn-secondary w-full text-accent-600">
              Выйти из аккаунта
            </button>
          </div>
        )
      
      default:
        return <HomePage />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="md:ml-64 pt-16 md:pt-0">
        <div className="max-w-7xl mx-auto px-4 py-6 md:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}

export default App
