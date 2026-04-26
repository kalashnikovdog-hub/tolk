from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

# Таблица связи многие-ко-многим для коллекций и скидок
collection_discounts = Table(
    'collection_discounts',
    Base.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True),
    Column('discount_id', Integer, ForeignKey('discounts.id'), primary_key=True)
)

# Таблица связи для семейных карт
family_card_members = Table(
    'family_card_members',
    Base.metadata,
    Column('card_id', Integer, ForeignKey('family_cards.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


class SubscriptionTier(enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    FAMILY = "family"


class DiscountType(enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    CASHBACK = "cashback"


class StoreType(enum.Enum):
    GROCERY = "grocery"  # Продукты (Пятерочка, Перекресток)
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    SERVICES = "services"
    RESTAURANT = "restaurant"
    ONLINE = "online"
    OTHER = "other"


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(20))
    
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    collections = relationship("Collection", back_populates="owner", cascade="all, delete-orphan")
    family_cards_owned = relationship("FamilyCard", foreign_keys="FamilyCard.owner_id", back_populates="owner")
    family_cards_member = relationship("FamilyCard", secondary=family_card_members, back_populates="members")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Store(Base):
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    store_type = Column(SQLEnum(StoreType), default=StoreType.OTHER)
    
    website_url = Column(String(500))
    logo_url = Column(String(500))
    catalog_url = Column(String(500))  # URL цифрового каталога
    
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    discounts = relationship("Discount", back_populates="store", cascade="all, delete-orphan")
    categories = relationship("StoreCategory", back_populates="store", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Store(id={self.id}, name={self.name})>"


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    icon_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    discounts = relationship("Discount", back_populates="category")
    store_categories = relationship("StoreCategory", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class StoreCategory(Base):
    """Связь магазинов с категориями (у разных магазинов могут быть разные категории)"""
    __tablename__ = 'store_categories'
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    external_category_id = Column(String(255))  # ID категории во внешней системе
    
    name = Column(String(255))  # Название категории в конкретном магазине
    
    store = relationship("Store", back_populates="categories")
    category = relationship("Category", back_populates="store_categories")
    
    def __repr__(self):
        return f"<StoreCategory(store_id={self.store_id}, category_id={self.category_id})>"


class Discount(Base):
    __tablename__ = 'discounts'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    discount_type = Column(SQLEnum(DiscountType), default=DiscountType.PERCENTAGE)
    discount_value = Column(Float, nullable=False)  # Размер скидки (процент или сумма)
    min_purchase_amount = Column(Float)  # Минимальная сумма покупки
    
    original_price = Column(Float)
    discounted_price = Column(Float)
    
    category_id = Column(Integer, ForeignKey('categories.id'))
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    
    promo_code = Column(String(100))  # Промокод
    promo_code_description = Column(Text)  # Описание условий промокода
    
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    is_personal = Column(Boolean, default=False)  # Персональная скидка
    is_exclusive = Column(Boolean, default=False)  # Эксклюзивная для подписчиков
    is_bank_offer = Column(Boolean, default=False)  # Специальное предложение от банка
    bank_name = Column(String(255))  # Название банка
    
    source_url = Column(String(500))  # URL источника
    image_url = Column(String(500))  # Изображение акции
    
    terms_and_conditions = Column(Text)  # Условия акции
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Проверено модератором
    views_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    
    external_id = Column(String(255), index=True)  # ID во внешней системе
    scraped_at = Column(DateTime(timezone=True))  # Когда найдено скрапером
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="discounts")
    store = relationship("Store", back_populates="discounts")
    collections = relationship("Collection", secondary=collection_discounts, back_populates="discounts")
    
    def __repr__(self):
        return f"<Discount(id={self.id}, title={self.title})>"


class Collection(Base):
    """Пользовательская подборка предложений"""
    __tablename__ = 'collections'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    is_public = Column(Boolean, default=False)  # Публичная подборка
    is_featured = Column(Boolean, default=False)  # Featured подборка
    
    cover_image_url = Column(String(500))
    
    views_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="collections")
    discounts = relationship("Discount", secondary=collection_discounts, back_populates="collections")
    
    def __repr__(self):
        return f"<Collection(id={self.id}, title={self.title})>"


class FamilyCard(Base):
    """Семейная карта скидок"""
    __tablename__ = 'family_cards'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    card_number = Column(String(20), unique=True, index=True)
    
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    max_members = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="family_cards_owned")
    members = relationship("User", secondary=family_card_members, back_populates="family_cards_member")
    
    def __repr__(self):
        return f"<FamilyCard(id={self.id}, name={self.name})>"


class UserPreference(Base):
    """Предпочтения пользователя для персональных рекомендаций"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    category_id = Column(Integer, ForeignKey('categories.id'))
    store_id = Column(Integer, ForeignKey('stores.id'))
    
    preference_type = Column(String(50))  # 'favorite', 'disliked', 'frequent'
    score = Column(Float, default=0.0)  # Вес предпочтения
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    category = relationship("Category")
    store = relationship("Store")
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, type={self.preference_type})>"


class BankOffer(Base):
    """Специальные предложения от банков (раз в месяц)"""
    __tablename__ = 'bank_offers'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    bank_name = Column(String(255), nullable=False)
    discount_value = Column(Float, nullable=False)  # Кэшбэк или скидка
    
    category_ids = Column(Text)  # JSON список категорий
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BankOffer(id={self.id}, bank={self.bank_name})>"


class ScrapedSource(Base):
    """Источники для скрапинга"""
    __tablename__ = 'scraped_sources'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    
    source_type = Column(String(50))  # 'website', 'api', 'rss', 'catalog'
    spider_name = Column(String(255))  # Имя скрапера
    
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True))
    scrape_frequency = Column(Integer, default=3600)  # Частота в секундах
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ScrapedSource(id={self.id}, name={self.name})>"
