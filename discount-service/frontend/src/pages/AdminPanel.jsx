import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  Database, 
  Activity, 
  Trash2, 
  Edit, 
  Check, 
  X, 
  Search,
  Plus,
  RefreshCw,
  Play,
  Square,
  Server,
  BarChart3,
  Settings,
  Users,
  Store,
  Tag
} from 'lucide-react'
import { useAuthStore } from '../hooks/stores'
import { adminAPI } from '../utils/api'

const AdminPanel = () => {
  const { user, isAuthenticated, token } = useAuthStore()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)
  
  // Dashboard stats
  const [stats, setStats] = useState(null)
  const [daemonStatus, setDaemonStatus] = useState(null)
  
  // Discounts
  const [discounts, setDiscounts] = useState([])
  const [discountFilters, setDiscountFilters] = useState({
    page: 1,
    page_size: 20,
    is_active: null,
    is_verified: null,
    search_query: ''
  })
  const [totalDiscounts, setTotalDiscounts] = useState(0)
  const [editingDiscount, setEditingDiscount] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // Sources
  const [sources, setSources] = useState([])
  const [editingSource, setEditingSource] = useState(null)

  useEffect(() => {
    checkAdminAccess()
  }, [])

  useEffect(() => {
    if (isAdmin) {
      loadDashboardStats()
      loadDaemonStatus()
    }
  }, [isAdmin])

  useEffect(() => {
    if (activeTab === 'discounts' && isAdmin) {
      loadDiscounts()
    } else if (activeTab === 'sources' && isAdmin) {
      loadSources()
    }
  }, [activeTab, discountFilters, isAdmin])

  const checkAdminAccess = async () => {
    if (!isAuthenticated || !token) {
      setLoading(false)
      return
    }
    
    try {
      // Check if user has admin access
      // In production, this would check user role
      const adminEmails = ['admin@tolk.ru', 'admin@example.com']
      if (user && adminEmails.includes(user.email)) {
        setIsAdmin(true)
      }
    } catch (error) {
      console.error('Failed to check admin access:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadDashboardStats = async () => {
    try {
      const response = await adminAPI.getStatistics()
      setStats(response.data.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const loadDaemonStatus = async () => {
    try {
      const response = await adminAPI.getDaemonStatus()
      setDaemonStatus(response.data.data)
    } catch (error) {
      console.error('Failed to load daemon status:', error)
    }
  }

  const loadDiscounts = async () => {
    try {
      const response = await adminAPI.getDiscounts(discountFilters)
      setDiscounts(response.data.items)
      setTotalDiscounts(response.data.total)
    } catch (error) {
      console.error('Failed to load discounts:', error)
    }
  }

  const loadSources = async () => {
    try {
      const response = await adminAPI.getSources()
      setSources(response.data)
    } catch (error) {
      console.error('Failed to load sources:', error)
    }
  }

  const handleDeleteDiscount = async (id) => {
    if (!confirm('Вы уверены, что хотите удалить эту скидку?')) return
    
    try {
      await adminAPI.deleteDiscount(id)
      loadDiscounts()
    } catch (error) {
      console.error('Failed to delete discount:', error)
      alert('Ошибка при удалении')
    }
  }

  const handleBulkVerify = async (verified) => {
    const selectedIds = discounts.filter(d => d.selected).map(d => d.id)
    if (selectedIds.length === 0) {
      alert('Выберите скидки для обработки')
      return
    }
    
    try {
      await adminAPI.bulkVerify(selectedIds, verified)
      loadDiscounts()
    } catch (error) {
      console.error('Failed to bulk verify:', error)
    }
  }

  const handleDaemonAction = async (action) => {
    try {
      await adminAPI.daemonAction(action)
      loadDaemonStatus()
      alert(`Daemon ${action} successfully`)
    } catch (error) {
      console.error('Failed to perform daemon action:', error)
      alert('Ошибка выполнения команды')
    }
  }

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-4 rounded-xl ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  )

  const renderDashboard = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Панель управления</h2>
        <p className="text-gray-600">Обзор системы и статистика</p>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Всего скидок"
            value={stats.total_discounts || 0}
            icon={Tag}
            color="bg-gradient-to-br from-blue-500 to-blue-600"
          />
          <StatCard
            title="Активные"
            value={stats.active_discounts || 0}
            icon={Activity}
            color="bg-gradient-to-br from-green-500 to-green-600"
          />
          <StatCard
            title="Проверено"
            value={stats.verified_discounts || 0}
            icon={Check}
            color="bg-gradient-to-br from-purple-500 to-purple-600"
          />
          <StatCard
            title="Источников"
            value={stats.total_sources || 0}
            icon={Server}
            color="bg-gradient-to-br from-orange-500 to-orange-600"
          />
        </div>
      )}

      {/* Daemon Control */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-100 rounded-xl">
              <Server className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Скрапер-демон</h3>
              <p className="text-sm text-gray-500">Управление сбором данных</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              daemonStatus?.is_running 
                ? 'bg-green-100 text-green-700' 
                : 'bg-gray-100 text-gray-700'
            }`}>
              {daemonStatus?.is_running ? 'Запущен' : 'Остановлен'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">Активных источников</p>
            <p className="text-2xl font-bold text-gray-900">{daemonStatus?.active_sources || 0}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">Последний скрапинг</p>
            <p className="text-sm font-medium text-gray-900">
              {daemonStatus?.last_scrape 
                ? new Date(daemonStatus.last_scrape).toLocaleString('ru-RU')
                : 'Никогда'}
            </p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">Статус</p>
            <p className="text-sm font-medium text-green-600">Работает нормально</p>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => handleDaemonAction('start')}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <Play className="w-4 h-4" />
            Запустить
          </button>
          <button
            onClick={() => handleDaemonAction('stop')}
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            <Square className="w-4 h-4" />
            Остановить
          </button>
          <button
            onClick={() => handleDaemonAction('run-now')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Скрапить сейчас
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Быстрые действия</h3>
          <div className="space-y-3">
            <button
              onClick={() => setActiveTab('discounts')}
              className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <Tag className="w-5 h-5 text-blue-500" />
              <span>Управление скидками</span>
            </button>
            <button
              onClick={() => setActiveTab('sources')}
              className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <Database className="w-5 h-5 text-green-500" />
              <span>Источники данных</span>
            </button>
            <button
              onClick={() => setActiveTab('stores')}
              className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <Store className="w-5 h-5 text-purple-500" />
              <span>Магазины</span>
            </button>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Система активна</h3>
          <p className="text-indigo-100 mb-4">
            Все сервисы работают в штатном режиме
          </p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm">Online</span>
          </div>
        </div>
      </div>
    </div>
  )

  const renderDiscounts = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Управление скидками</h2>
          <p className="text-gray-600">Просмотр и редактирование всех скидок</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Добавить
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск..."
                value={discountFilters.search_query}
                onChange={(e) => setDiscountFilters({...discountFilters, search_query: e.target.value})}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <select
            value={discountFilters.is_verified || ''}
            onChange={(e) => setDiscountFilters({...discountFilters, is_verified: e.target.value ? e.target.value === 'true' : null})}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Все статусы</option>
            <option value="true">Проверенные</option>
            <option value="false">Непроверенные</option>
          </select>
          <select
            value={discountFilters.is_active || ''}
            onChange={(e) => setDiscountFilters({...discountFilters, is_active: e.target.value ? e.target.value === 'true' : null})}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Все</option>
            <option value="true">Активные</option>
            <option value="false">Неактивные</option>
          </select>
        </div>
      </div>

      {/* Bulk Actions */}
      <div className="flex gap-3">
        <button
          onClick={() => handleBulkVerify(true)}
          className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          <Check className="w-4 h-4" />
          Проверить выбранные
        </button>
        <button
          onClick={() => handleBulkVerify(false)}
          className="flex items-center gap-2 px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
        >
          <X className="w-4 h-4" />
          Снять проверку
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Название
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Скидка
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Магазин
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {discounts.map((discount) => (
              <tr key={discount.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  #{discount.id}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{discount.title}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm font-semibold text-green-600">
                    -{discount.discount_value}%
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {discount.store?.name || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex gap-2">
                    {discount.is_verified && (
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                        Проверено
                      </span>
                    )}
                    {discount.is_active ? (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                        Активно
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        Неактивно
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setEditingDiscount(discount)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteDiscount(discount.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Показано {discounts.length} из {totalDiscounts}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setDiscountFilters({...discountFilters, page: discountFilters.page - 1})}
            disabled={discountFilters.page === 1}
            className="px-4 py-2 border border-gray-200 rounded-lg disabled:opacity-50"
          >
            Назад
          </button>
          <button
            onClick={() => setDiscountFilters({...discountFilters, page: discountFilters.page + 1})}
            disabled={discounts.length < discountFilters.page_size}
            className="px-4 py-2 border border-gray-200 rounded-lg disabled:opacity-50"
          >
            Вперед
          </button>
        </div>
      </div>
    </div>
  )

  const renderSources = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Источники данных</h2>
          <p className="text-gray-600">Telegram каналы и сайты для парсинга</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
          <Plus className="w-4 h-4" />
          Добавить источник
        </button>
      </div>

      <div className="grid gap-4">
        {sources.map((source) => (
          <div key={source.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${
                  source.source_type === 'telegram' 
                    ? 'bg-blue-100' 
                    : 'bg-green-100'
                }`}>
                  {source.source_type === 'telegram' ? (
                    <Users className="w-6 h-6 text-blue-600" />
                  ) : (
                    <Database className="w-6 h-6 text-green-600" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{source.name}</h3>
                  <p className="text-sm text-gray-500">{source.url}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`px-3 py-1 rounded-full text-sm ${
                  source.is_active 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {source.is_active ? 'Активен' : 'Отключен'}
                </span>
                <button className="p-2 hover:bg-gray-100 rounded-lg">
                  <Settings className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Доступ запрещен</h2>
          <p className="text-gray-600">Только администраторы могут accessing эту страницу</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Shield className="w-8 h-8 text-blue-500" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">Админ-панель</h1>
              <p className="text-sm text-gray-500">Tolk Discount Service</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Вернуться на сайт
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex px-6 gap-6 border-t border-gray-100">
          {[
            { id: 'dashboard', label: 'Обзор', icon: BarChart3 },
            { id: 'discounts', label: 'Скидки', icon: Tag },
            { id: 'sources', label: 'Источники', icon: Database },
            { id: 'stores', label: 'Магазины', icon: Store },
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            )
          })}
        </div>
      </header>

      {/* Content */}
      <main className="p-6 max-w-7xl mx-auto">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'discounts' && renderDiscounts()}
        {activeTab === 'sources' && renderSources()}
        {activeTab === 'stores' && (
          <div className="text-center py-12">
            <Store className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Раздел в разработке</h3>
            <p className="text-gray-600">Управление магазинами будет доступно скоро</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default AdminPanel
