package model

import (
	"time"
)

// SubscriptionTier represents user subscription level
type SubscriptionTier string

const (
	SubscriptionTierFree    SubscriptionTier = "free"
	SubscriptionTierPremium SubscriptionTier = "premium"
	SubscriptionTierFamily  SubscriptionTier = "family"
)

// DiscountType represents the type of discount
type DiscountType string

const (
	DiscountTypePercentage DiscountType = "percentage"
	DiscountTypeFixed      DiscountType = "fixed"
	DiscountTypeCashback   DiscountType = "cashback"
)

// StoreType represents the type of store
type StoreType string

const (
	StoreTypeGrocery    StoreType = "grocery"
	StoreTypeElectronics StoreType = "electronics"
	StoreTypeClothing   StoreType = "clothing"
	StoreTypeServices   StoreType = "services"
	StoreTypeRestaurant StoreType = "restaurant"
	StoreTypeOnline     StoreType = "online"
	StoreTypeOther      StoreType = "other"
)

// User represents a platform user
type User struct {
	ID               int64          `json:"id"`
	Email            string         `json:"email"`
	PasswordHash     string         `json:"-"`
	FullName         string         `json:"full_name,omitempty"`
	Phone            string         `json:"phone,omitempty"`
	SubscriptionTier SubscriptionTier `json:"subscription_tier"`
	SubscriptionStart *time.Time    `json:"subscription_start,omitempty"`
	SubscriptionEnd   *time.Time    `json:"subscription_end,omitempty"`
	IsActive         bool           `json:"is_active"`
	IsVerified       bool           `json:"is_verified"`
	CreatedAt        time.Time      `json:"created_at"`
	UpdatedAt        *time.Time     `json:"updated_at,omitempty"`
}

// Store represents a retail store
type Store struct {
	ID          int64      `json:"id"`
	Name        string     `json:"name"`
	Description string     `json:"description,omitempty"`
	StoreType   StoreType  `json:"store_type"`
	WebsiteURL  string     `json:"website_url,omitempty"`
	LogoURL     string     `json:"logo_url,omitempty"`
	CatalogURL  string     `json:"catalog_url,omitempty"`
	IsActive    bool       `json:"is_active"`
	LastUpdated time.Time  `json:"last_updated"`
	CreatedAt   time.Time  `json:"created_at"`
}

// Category represents a discount category
type Category struct {
	ID        int64      `json:"id"`
	Name      string     `json:"name"`
	Slug      string     `json:"slug"`
	ParentID  *int64     `json:"parent_id,omitempty"`
	IconURL   string     `json:"icon_url,omitempty"`
	IsActive  bool       `json:"is_active"`
	CreatedAt time.Time  `json:"created_at"`
	Children  []Category `json:"children,omitempty"`
}

// Discount represents a discount offer
type Discount struct {
	ID                  int64       `json:"id"`
	Title               string      `json:"title"`
	Description         string      `json:"description,omitempty"`
	DiscountType        DiscountType `json:"discount_type"`
	DiscountValue       float64     `json:"discount_value"`
	MinPurchaseAmount   *float64    `json:"min_purchase_amount,omitempty"`
	OriginalPrice       *float64    `json:"original_price,omitempty"`
	DiscountedPrice     *float64    `json:"discounted_price,omitempty"`
	CategoryID          *int64      `json:"category_id,omitempty"`
	StoreID             int64       `json:"store_id"`
	PromoCode           string      `json:"promo_code,omitempty"`
	PromoCodeDescription string     `json:"promo_code_description,omitempty"`
	StartDate           *time.Time  `json:"start_date,omitempty"`
	EndDate             *time.Time  `json:"end_date,omitempty"`
	IsPersonal          bool        `json:"is_personal"`
	IsExclusive         bool        `json:"is_exclusive"`
	IsBankOffer         bool        `json:"is_bank_offer"`
	BankName            string      `json:"bank_name,omitempty"`
	SourceURL           string      `json:"source_url,omitempty"`
	ImageURL            string      `json:"image_url,omitempty"`
	TermsAndConditions  string      `json:"terms_and_conditions,omitempty"`
	IsActive            bool        `json:"is_active"`
	IsVerified          bool        `json:"is_verified"`
	ViewsCount          int64       `json:"views_count"`
	ClicksCount         int64       `json:"clicks_count"`
	ExternalID          string      `json:"external_id,omitempty"`
	ScrapedAt           *time.Time  `json:"scraped_at,omitempty"`
	CreatedAt           time.Time   `json:"created_at"`
	UpdatedAt           *time.Time  `json:"updated_at,omitempty"`
	Store               *Store      `json:"store,omitempty"`
	Category            *Category   `json:"category,omitempty"`
}

// Collection represents a user collection of discounts
type Collection struct {
	ID            int64      `json:"id"`
	Title         string     `json:"title"`
	Description   string     `json:"description,omitempty"`
	OwnerID       int64      `json:"owner_id"`
	IsPublic      bool       `json:"is_public"`
	IsFeatured    bool       `json:"is_featured"`
	CoverImageURL string     `json:"cover_image_url,omitempty"`
	ViewsCount    int64      `json:"views_count"`
	SharesCount   int64      `json:"shares_count"`
	Discounts     []Discount `json:"discounts,omitempty"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     *time.Time `json:"updated_at,omitempty"`
}

// FamilyCard represents a family discount card
type FamilyCard struct {
	ID         int64     `json:"id"`
	Name       string    `json:"name"`
	CardNumber string    `json:"card_number"`
	OwnerID    int64     `json:"owner_id"`
	MaxMembers int       `json:"max_members"`
	IsActive   bool      `json:"is_active"`
	Members    []User    `json:"members,omitempty"`
	CreatedAt  time.Time `json:"created_at"`
	UpdatedAt  *time.Time `json:"updated_at,omitempty"`
}

// UserPreference represents user preferences for recommendations
type UserPreference struct {
	ID              int64     `json:"id"`
	UserID          int64     `json:"user_id"`
	CategoryID      *int64    `json:"category_id,omitempty"`
	StoreID         *int64    `json:"store_id,omitempty"`
	PreferenceType  string    `json:"preference_type"`
	Score           float64   `json:"score"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       *time.Time `json:"updated_at,omitempty"`
}

// BankOffer represents special bank offers
type BankOffer struct {
	ID          int64     `json:"id"`
	Title       string    `json:"title"`
	Description string    `json:"description,omitempty"`
	BankName    string    `json:"bank_name"`
	DiscountValue float64 `json:"discount_value"`
	CategoryIDs string    `json:"category_ids"` // JSON array
	StartDate   time.Time `json:"start_date"`
	EndDate     time.Time `json:"end_date"`
	IsActive    bool      `json:"is_active"`
	CreatedAt   time.Time `json:"created_at"`
}
