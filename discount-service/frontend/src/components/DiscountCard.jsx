import { motion } from 'framer-motion'
import { ShoppingCart, Tag, Percent, Clock } from 'lucide-react'

const DiscountCard = ({ discount, onFavorite, isFavorite }) => {
  const discountPercent = discount.discount_percent || 0
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="card-discount relative overflow-hidden cursor-pointer"
    >
      {/* Discount Badge */}
      <div className="discount-tag">
        -{discountPercent}%
      </div>
      
      {/* Store Logo */}
      <div className="p-4 pb-2">
        <div className="flex items-center gap-2 mb-3">
          {discount.store?.logo ? (
            <img 
              src={discount.store.logo} 
              alt={discount.store.name}
              className="w-10 h-10 object-contain rounded-lg"
            />
          ) : (
            <ShoppingCart className="w-10 h-10 text-primary-500 bg-primary-100 p-2 rounded-lg" />
          )}
          <div>
            <h3 className="font-semibold text-gray-900">{discount.store?.name}</h3>
            <p className="text-xs text-gray-500">{discount.category?.name}</p>
          </div>
        </div>
        
        {/* Product Info */}
        <div className="mb-3">
          <h4 className="font-medium text-gray-800 line-clamp-2 mb-1">
            {discount.product_name}
          </h4>
          {discount.description && (
            <p className="text-sm text-gray-600 line-clamp-2">
              {discount.description}
            </p>
          )}
        </div>
        
        {/* Price Info */}
        <div className="flex items-center gap-2 mb-3">
          {discount.old_price && (
            <span className="text-sm text-gray-400 line-through">
              {discount.old_price} ₽
            </span>
          )}
          <span className="text-lg font-bold text-accent-600">
            {discount.price} ₽
          </span>
          {discount.base_discount && (
            <span className="badge badge-primary">
              +{discount.base_discount}% кэшбэк
            </span>
          )}
        </div>
        
        {/* Validity */}
        {discount.valid_until && (
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-3">
            <Clock className="w-3 h-3" />
            <span>
              До {new Date(discount.valid_until).toLocaleDateString('ru-RU')}
            </span>
          </div>
        )}
        
        {/* Actions */}
        <div className="flex gap-2">
          <button className="btn-primary flex-1 text-sm py-2">
            Получить купон
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onFavorite?.(discount.id)
            }}
            className={`px-3 py-2 rounded-lg transition-all ${
              isFavorite 
                ? 'bg-accent-100 text-accent-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Tag className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Gradient Overlay */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 via-accent-500 to-primary-500" />
    </motion.div>
  )
}

export default DiscountCard
