import { motion } from 'framer-motion'
import { Search, Filter, X } from 'lucide-react'

const SearchFilter = ({ 
  searchValue, 
  onSearchChange, 
  categories, 
  stores, 
  filters, 
  onFilterChange,
  onReset 
}) => {
  return (
    <div className="glass-card-premium p-5 mb-6">
      {/* Search Bar - Liquid */}
      <div className="relative mb-4">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Поиск скидок, товаров, магазинов..."
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          className="input-liquid pl-12"
        />
        {searchValue && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            onClick={() => onSearchChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 hover:bg-white/50 rounded-lg transition-all text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </motion.button>
        )}
      </div>
      
      {/* Filters - Glass Pills */}
      <div className="flex flex-wrap gap-2.5">
        {/* Category Filter */}
        <div className="relative group">
          <select
            value={filters.category || ''}
            onChange={(e) => onFilterChange({ category: e.target.value || null })}
            className="btn-liquid-secondary pr-9 appearance-none cursor-pointer text-sm"
          >
            <option value="">Все категории</option>
            {categories?.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
          <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-primary-500 transition-colors" />
        </div>
        
        {/* Store Filter */}
        <div className="relative group">
          <select
            value={filters.store || ''}
            onChange={(e) => onFilterChange({ store: e.target.value || null })}
            className="btn-liquid-secondary pr-9 appearance-none cursor-pointer text-sm"
          >
            <option value="">Все магазины</option>
            {stores?.map((store) => (
              <option key={store.id} value={store.id}>
                {store.name}
              </option>
            ))}
          </select>
          <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-primary-500 transition-colors" />
        </div>
        
        {/* Min Discount */}
        <div className="relative group">
          <select
            value={filters.minDiscount}
            onChange={(e) => onFilterChange({ minDiscount: Number(e.target.value) })}
            className="btn-liquid-secondary pr-9 appearance-none cursor-pointer text-sm"
          >
            <option value="0">Любая скидка</option>
            <option value="10">От 10%</option>
            <option value="20">От 20%</option>
            <option value="30">От 30%</option>
            <option value="50">От 50%</option>
          </select>
          <Percent className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none group-hover:text-accent-500 transition-colors" />
        </div>
        
        {/* Reset Filters */}
        {(filters.category || filters.store || filters.minDiscount > 0) && (
          <motion.button 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={onReset} 
            className="btn-liquid-secondary text-sm text-accent-600 hover:text-accent-700"
          >
            Сбросить
          </motion.button>
        )}
      </div>
      
      {/* Active Filters Tags - Glass */}
      {(filters.category || filters.store || filters.minDiscount > 0) && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/20"
        >
          {filters.category && (
            <motion.span 
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="badge-glass-primary flex items-center gap-1.5"
            >
              {categories?.find(c => c.id === filters.category)?.name}
              <motion.button 
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => onFilterChange({ category: null })}
              >
                <X className="w-3.5 h-3.5" />
              </motion.button>
            </motion.span>
          )}
          {filters.store && (
            <motion.span 
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="badge-glass-primary flex items-center gap-1.5"
            >
              {stores?.find(s => s.id === filters.store)?.name}
              <motion.button 
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => onFilterChange({ store: null })}
              >
                <X className="w-3.5 h-3.5" />
              </motion.button>
            </motion.span>
          )}
          {filters.minDiscount > 0 && (
            <motion.span 
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="badge-glass-accent flex items-center gap-1.5"
            >
              От {filters.minDiscount}%
              <motion.button 
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => onFilterChange({ minDiscount: 0 })}
              >
                <X className="w-3.5 h-3.5" />
              </motion.button>
            </motion.span>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default SearchFilter
