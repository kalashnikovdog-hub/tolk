import { motion } from 'framer-motion'
import { Home, Search, Heart, Users, BookOpen, User, Menu, X } from 'lucide-react'
import { useUIStore, useAuthStore } from '../hooks/stores'

const navItems = [
  { id: 'home', label: 'Главная', icon: Home },
  { id: 'catalog', label: 'Каталог', icon: Search },
  { id: 'favorites', label: 'Избранное', icon: Heart },
  { id: 'family', label: 'Семья', icon: Users },
  { id: 'collections', label: 'Подборки', icon: BookOpen },
  { id: 'profile', label: 'Профиль', icon: User },
]

const Navigation = () => {
  const { currentTab, setTab, isMobileMenuOpen, toggleMobileMenu } = useUIStore()
  const { isAuthenticated } = useAuthStore()

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden md:flex fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 flex-col z-50">
        {/* Logo */}
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-500 to-accent-500 bg-clip-text text-transparent">
            DiscountHub
          </h1>
          <p className="text-xs text-gray-500 mt-1">Скидки и Промо</p>
        </div>
        
        {/* Nav Items */}
        <div className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentTab === item.id
            
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`nav-item w-full ${isActive ? 'nav-item-active' : ''}`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            )
          })}
        </div>
        
        {/* Subscription CTA */}
        {!isAuthenticated && (
          <div className="p-4 border-t border-gray-100">
            <div className="bg-gradient-to-br from-primary-50 to-accent-50 rounded-xl p-4">
              <h3 className="font-semibold text-gray-900 mb-1">Premium доступ</h3>
              <p className="text-xs text-gray-600 mb-3">
                Получите доступ ко всем функциям сервиса
              </p>
              <button className="btn-primary w-full text-sm">
                Попробовать бесплатно
              </button>
            </div>
          </div>
        )}
      </nav>
      
      {/* Mobile Header */}
      <header className="md:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50 safe-area-top">
        <div className="flex items-center justify-between px-4 py-3">
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary-500 to-accent-500 bg-clip-text text-transparent">
            DiscountHub
          </h1>
          <button 
            onClick={toggleMobileMenu}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-600" />
            ) : (
              <Menu className="w-6 h-6 text-gray-600" />
            )}
          </button>
        </div>
      </header>
      
      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={toggleMobileMenu}
        >
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25 }}
            className="absolute right-0 top-0 bottom-0 w-64 bg-white"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-gray-100 flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">Меню</h2>
              <button 
                onClick={toggleMobileMenu}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            
            <div className="p-4 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = currentTab === item.id
                
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setTab(item.id)
                      toggleMobileMenu()
                    }}
                    className={`nav-item w-full ${isActive ? 'nav-item-active' : ''}`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                )
              })}
            </div>
          </motion.div>
        </motion.div>
      )}
      
      {/* Mobile Bottom Navigation */}
      <nav className="mobile-bottom-nav md:hidden">
        <div className="flex items-center justify-around">
          {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon
            const isActive = currentTab === item.id
            
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-all ${
                  isActive 
                    ? 'text-primary-600 bg-primary-50' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className={`w-6 h-6 ${isActive ? 'fill-current' : ''}`} />
                <span className="text-xs">{item.label}</span>
              </button>
            )
          })}
        </div>
      </nav>
    </>
  )
}

export default Navigation
