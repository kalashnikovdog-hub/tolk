import { motion } from 'framer-motion'
import { Home, Search, Heart, Users, BookOpen, User, Menu, X, Shield } from 'lucide-react'
import { useUIStore, useAuthStore } from '../hooks/stores'

const navItems = [
  { id: 'home', label: 'Главная', icon: Home },
  { id: 'catalog', label: 'Каталог', icon: Search },
  { id: 'favorites', label: 'Избранное', icon: Heart },
  { id: 'family', label: 'Семья', icon: Users },
  { id: 'collections', label: 'Подборки', icon: BookOpen },
  { id: 'profile', label: 'Профиль', icon: User },
]

// Admin-only navigation items (shown separately)
const adminNavItem = { id: 'admin', label: 'Админ', icon: Shield }

const Navigation = () => {
  const { currentTab, setTab, isMobileMenuOpen, toggleMobileMenu } = useUIStore()
  const { isAuthenticated, user } = useAuthStore()
  
  // Check if user is admin
  const isAdmin = user && ['admin@tolk.ru', 'admin@example.com'].includes(user.email)

  return (
    <>
      {/* Desktop Navigation - Liquid Glass */}
      <nav className="hidden md:flex fixed left-0 top-0 bottom-0 w-72 nav-glass flex-col z-50">
        {/* Logo */}
        <div className="p-6 border-b border-white/20">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-500 via-emerald-400 to-accent-500 bg-clip-text text-transparent animate-gradient">
            Tolk
          </h1>
          <p className="text-xs text-gray-600 mt-1 font-medium">Скидки и Промо</p>
        </div>
        
        {/* Nav Items */}
        <div className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentTab === item.id
            
            return (
              <motion.button
                key={item.id}
                onClick={() => setTab(item.id)}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full ${isActive ? 'nav-item-glass-active' : 'nav-item-glass'}`}
              >
                <div className={`p-2 rounded-lg ${isActive ? 'bg-primary-500/20' : ''}`}>
                  <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : ''}`} />
                </div>
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <motion.div 
                    layoutId="activeNav"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500"
                  />
                )}
              </motion.button>
            )
          })}
          
          {/* Admin Link - Only shown to admins */}
          {isAdmin && (
            <motion.button
              onClick={() => setTab('admin')}
              whileHover={{ scale: 1.02, x: 4 }}
              whileTap={{ scale: 0.98 }}
              className={`w-full ${currentTab === 'admin' ? 'nav-item-glass-active' : 'nav-item-glass'}`}
            >
              <div className={`p-2 rounded-lg ${currentTab === 'admin' ? 'bg-indigo-500/20' : ''}`}>
                <Shield className={`w-5 h-5 ${currentTab === 'admin' ? 'text-indigo-600' : ''}`} />
              </div>
              <span className="font-medium">Админ-панель</span>
              {currentTab === 'admin' && (
                <motion.div
                  layoutId="activeNav"
                  className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-500"
                />
              )}
            </motion.button>
          )}
        </div>
        
        {/* Subscription CTA - Glass */}
        {!isAuthenticated && (
          <div className="p-4 border-t border-white/20">
            <div className="glass-card-premium p-4">
              <h3 className="font-semibold text-gray-900 mb-1">Premium доступ</h3>
              <p className="text-xs text-gray-600 mb-3">
                Получите доступ ко всем функциям сервиса
              </p>
              <button className="btn-liquid-primary w-full text-sm">
                Попробовать бесплатно
              </button>
            </div>
          </div>
        )}
      </nav>
      
      {/* Mobile Header - Liquid Glass */}
      <header className="md:hidden nav-glass safe-area-top">
        <div className="flex items-center justify-between px-4 py-3">
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary-500 to-accent-500 bg-clip-text text-transparent">
            Tolk
          </h1>
          <button 
            onClick={toggleMobileMenu}
            className="p-2 hover:bg-white/50 rounded-xl transition-all"
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
          className="md:hidden fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
          onClick={toggleMobileMenu}
        >
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25 }}
            className="absolute right-0 top-0 bottom-0 w-72 nav-glass"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-white/20 flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">Меню</h2>
              <button 
                onClick={toggleMobileMenu}
                className="p-2 hover:bg-white/50 rounded-xl transition-all"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            
            <div className="p-4 space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = currentTab === item.id
                
                return (
                  <motion.button
                    key={item.id}
                    onClick={() => {
                      setTab(item.id)
                      toggleMobileMenu()
                    }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full ${isActive ? 'nav-item-glass-active' : 'nav-item-glass'}`}
                  >
                    <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : ''}`} />
                    <span className="font-medium">{item.label}</span>
                  </motion.button>
                )
              })}
            </div>
          </motion.div>
        </motion.div>
      )}
      
      {/* Mobile Bottom Navigation - Liquid Glass */}
      <nav className="fixed bottom-0 left-0 right-0 nav-glass safe-area-bottom md:hidden border-t border-white/20">
        <div className="flex items-center justify-around px-2 py-2">
          {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon
            const isActive = currentTab === item.id
            
            return (
              <motion.button
                key={item.id}
                onClick={() => setTab(item.id)}
                whileTap={{ scale: 0.9 }}
                className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all ${
                  isActive 
                    ? 'text-primary-600 bg-primary-500/10' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-white/30'
                }`}
              >
                <Icon className={`w-6 h-6 ${isActive ? 'fill-current' : ''}`} />
                <span className="text-[10px] font-medium">{item.label}</span>
              </motion.button>
            )
          })}
        </div>
      </nav>
    </>
  )
}

export default Navigation
