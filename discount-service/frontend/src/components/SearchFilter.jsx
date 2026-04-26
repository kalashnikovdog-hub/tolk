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
    <div className="bg-white rounded-xl shadow-card p-4 mb-6">
      {/* Search Bar */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Поиск скидок, товаров, магазинов..."
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          className="input-field pl-10"
        />
        {searchValue && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      
      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {/* Category Filter */}
        <div className="relative">
          <select
            value={filters.category || ''}
            onChange={(e) => onFilterChange({ category: e.target.value || null })}
            className="btn-secondary pr-8 appearance-none cursor-pointer"
          >
            <option value="">Все категории</option>
            {categories?.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
          <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
        
        {/* Store Filter */}
        <div className="relative">
          <select
            value={filters.store || ''}
            onChange={(e) => onFilterChange({ store: e.target.value || null })}
            className="btn-secondary pr-8 appearance-none cursor-pointer"
          >
            <option value="">Все магазины</option>
            {stores?.map((store) => (
              <option key={store.id} value={store.id}>
                {store.name}
              </option>
            ))}
          </select>
          <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
        
        {/* Min Discount */}
        <div className="relative">
          <select
            value={filters.minDiscount}
            onChange={(e) => onFilterChange({ minDiscount: Number(e.target.value) })}
            className="btn-secondary pr-8 appearance-none cursor-pointer"
          >
            <option value="0">Любая скидка</option>
            <option value="10">От 10%</option>
            <option value="20">От 20%</option>
            <option value="30">От 30%</option>
            <option value="50">От 50%</option>
          </select>
          <Percent className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
        
        {/* Reset Filters */}
        {(filters.category || filters.store || filters.minDiscount > 0) && (
          <button onClick={onReset} className="btn-secondary text-sm">
            Сбросить
          </button>
        )}
      </div>
      
      {/* Active Filters Tags */}
      {(filters.category || filters.store || filters.minDiscount > 0) && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-gray-100"
        >
          {filters.category && (
            <span className="badge badge-primary flex items-center gap-1">
              {categories?.find(c => c.id === filters.category)?.name}
              <button onClick={() => onFilterChange({ category: null })}>
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.store && (
            <span className="badge badge-primary flex items-center gap-1">
              {stores?.find(s => s.id === filters.store)?.name}
              <button onClick={() => onFilterChange({ store: null })}>
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.minDiscount > 0 && (
            <span className="badge badge-primary flex items-center gap-1">
              От {filters.minDiscount}%
              <button onClick={() => onFilterChange({ minDiscount: 0 })}>
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default SearchFilter
