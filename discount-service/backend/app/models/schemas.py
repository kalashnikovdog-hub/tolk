from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubscriptionTierEnum(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    FAMILY = "family"


class DiscountTypeEnum(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    CASHBACK = "cashback"


class StoreTypeEnum(str, Enum):
    GROCERY = "grocery"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    SERVICES = "services"
    RESTAURANT = "restaurant"
    ONLINE = "online"
    OTHER = "other"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: int
    subscription_tier: SubscriptionTierEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Store schemas
class StoreBase(BaseModel):
    name: str
    description: Optional[str] = None
    store_type: StoreTypeEnum = StoreTypeEnum.OTHER
    website_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    catalog_url: Optional[HttpUrl] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    store_type: Optional[StoreTypeEnum] = None
    website_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    catalog_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: int
    is_active: bool
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    icon_url: Optional[HttpUrl] = None


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    children: List['CategoryResponse'] = []
    
    class Config:
        from_attributes = True


# Discount schemas
class DiscountBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    discount_type: DiscountTypeEnum = DiscountTypeEnum.PERCENTAGE
    discount_value: float
    min_purchase_amount: Optional[float] = None
    original_price: Optional[float] = None
    discounted_price: Optional[float] = None
    promo_code: Optional[str] = Field(None, max_length=100)
    promo_code_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source_url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    terms_and_conditions: Optional[str] = None


class DiscountCreate(DiscountBase):
    category_id: Optional[int] = None
    store_id: int
    is_personal: bool = False
    is_exclusive: bool = False
    is_bank_offer: bool = False
    bank_name: Optional[str] = None
    external_id: Optional[str] = None


class DiscountUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    discount_value: Optional[float] = None
    promo_code: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class DiscountResponse(DiscountBase):
    id: int
    category_id: Optional[int]
    store_id: int
    is_personal: bool
    is_exclusive: bool
    is_bank_offer: bool
    bank_name: Optional[str]
    is_active: bool
    is_verified: bool
    views_count: int
    clicks_count: int
    scraped_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    store: Optional[StoreResponse] = None
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True


class DiscountFilter(BaseModel):
    category_id: Optional[int] = None
    store_id: Optional[int] = None
    discount_type: Optional[DiscountTypeEnum] = None
    min_discount_value: Optional[float] = None
    max_discount_value: Optional[float] = None
    is_personal: Optional[bool] = None
    is_exclusive: Optional[bool] = None
    is_bank_offer: Optional[bool] = None
    search_query: Optional[str] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"


# Collection schemas
class CollectionBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    cover_image_url: Optional[HttpUrl] = None


class CollectionCreate(CollectionBase):
    discount_ids: List[int] = []


class CollectionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    cover_image_url: Optional[HttpUrl] = None
    is_public: Optional[bool] = None
    discount_ids: Optional[List[int]] = None


class CollectionResponse(CollectionBase):
    id: int
    owner_id: int
    is_public: bool
    is_featured: bool
    views_count: int
    shares_count: int
    created_at: datetime
    updated_at: datetime
    discounts: List[DiscountResponse] = []
    
    class Config:
        from_attributes = True


# Family Card schemas
class FamilyCardBase(BaseModel):
    name: str = Field(..., max_length=255)


class FamilyCardCreate(FamilyCardBase):
    pass


class FamilyCardMemberAdd(BaseModel):
    user_email: EmailStr


class FamilyCardResponse(FamilyCardBase):
    id: int
    card_number: str
    owner_id: int
    max_members: int
    is_active: bool
    created_at: datetime
    members: List[UserResponse] = []
    
    class Config:
        from_attributes = True


# User Preference schemas
class UserPreferenceBase(BaseModel):
    preference_type: str = Field(..., max_length=50)
    score: float = 0.0


class UserPreferenceCreate(UserPreferenceBase):
    category_id: Optional[int] = None
    store_id: Optional[int] = None


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int
    category_id: Optional[int]
    store_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bank Offer schemas
class BankOfferBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    bank_name: str
    discount_value: float
    category_ids: str  # JSON string
    start_date: datetime
    end_date: datetime


class BankOfferCreate(BankOfferBase):
    pass


class BankOfferResponse(BankOfferBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Response wrappers
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    pages: int


class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
