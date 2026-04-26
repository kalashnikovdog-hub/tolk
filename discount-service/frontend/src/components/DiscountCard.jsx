import { motion } from 'framer-motion'
import { ShoppingCart, Tag, Percent, Clock, Heart } from 'lucide-react'

const DiscountCard = ({ discount, onFavorite, isFavorite }) => {
  const discountPercent = discount.discount_percent || 0
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.03, y: -4 }}
      className="card-discount-liquid group"
    >
      {/* Discount Badge - Liquid Glass */}
      <div className="absolute top-3 right-3 z-10">
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="badge-glass-accent font-bold text-sm animate-pulse-slow"
        >
          -{discountPercent}%
        </motion.div>
      </div>
      
      {/* Store Logo */}
      <div className="mb-3">
        <div className="flex items-center gap-3 mb-3">
          {discount.store?.logo ? (
            <motion.img 
              src={discount.store.logo} 
              alt={discount.store.name}
              whileHover={{ scale: 1.1, rotate: 5 }}
              className="w-12 h-12 object-contain rounded-xl shadow-md bg-white/50 p-1"
            />
          ) : (
            <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-lg">
              <ShoppingCart className="w-6 h-6 text-white" />
            </div>
          )}
          <div>
            <h3 className="font-bold text-gray-900">{discount.store?.name}</h3>
            <p className="text-xs text-gray-600 font-medium">{discount.category?.name}</p>
          </div>
        </div>
        
        {/* Product Info */}
        <div className="mb-4">
          <h4 className="font-semibold text-gray-800 line-clamp-2 mb-2 group-hover:text-primary-600 transition-colors">
            {discount.product_name}
          </h4>
          {discount.description && (
            <p className="text-sm text-gray-600 line-clamp-2">
              {discount.description}
            </p>
          )}
        </div>
        
        {/* Price Info */}
        <div className="flex items-center gap-3 mb-3">
          {discount.old_price && (
            <span className="text-sm text-gray-400 line-through decoration-gray-400/50">
              {discount.old_price} ₽
            </span>
          )}
          <span className="text-xl font-bold bg-gradient-to-r from-accent-600 to-accent-500 bg-clip-text text-transparent">
            {discount.price} ₽
          </span>
          {discount.base_discount && (
            <span className="badge-glass-primary text-xs">
              +{discount.base_discount}% кэшбэк
            </span>
          )}
        </div>
        
        {/* Validity */}
        {discount.valid_until && (
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
            <Clock className="w-3.5 h-3.5" />
            <span className="font-medium">
              До {new Date(discount.valid_until).toLocaleDateString('ru-RU')}
            </span>
          </div>
        )}
        
        {/* Actions */}
        <div className="flex gap-2">
          <motion.button 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="btn-liquid-primary flex-1 text-sm"
          >
            Получить купон
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={(e) => {
              e.stopPropagation()
              onFavorite?.(discount.id)
            }}
            className={`px-3 py-2.5 rounded-xl transition-all duration-300 ${
              isFavorite 
                ? 'bg-gradient-to-br from-accent-500/20 to-accent-600/10 text-accent-600 border border-accent-300/50' 
                : 'bg-white/30 text-gray-600 hover:bg-white/50 border border-white/30'
            }`}
          >
            <Heart className={`w-4 h-4 ${isFavorite ? 'fill-current' : ''}`} />
          </motion.button>
        </div>
      </div>
      
      {/* Gradient Overlay with Shimmer */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 via-emerald-400 to-accent-500 opacity-70 group-hover:opacity-100 transition-opacity" />
      
      {/* Shimmer Effect on Hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-500 overflow-hidden rounded-2xl">
        <div className="absolute inset-0 shimmer-effect" />
      </div>
    </motion.div>
  )
}

export default DiscountCard
