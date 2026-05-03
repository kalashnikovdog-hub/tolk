package model

import "time"

// DiscountFilter represents filters for discount listing
type DiscountFilter struct {
	CategoryID       *int64       `json:"category_id,omitempty"`
	StoreID          *int64       `json:"store_id,omitempty"`
	DiscountType     *DiscountType `json:"discount_type,omitempty"`
	MinDiscountValue *float64     `json:"min_discount_value,omitempty"`
	MaxDiscountValue *float64     `json:"max_discount_value,omitempty"`
	IsPersonal       *bool        `json:"is_personal,omitempty"`
	IsExclusive      *bool        `json:"is_exclusive,omitempty"`
	IsBankOffer      *bool        `json:"is_bank_offer,omitempty"`
	SearchQuery      string       `json:"search_query,omitempty"`
	Page             int          `json:"page"`
	PageSize         int          `json:"page_size"`
	SortBy           string       `json:"sort_by"`
	SortOrder        string       `json:"sort_order"`
}

// DefaultDiscountFilter returns default filter values
func DefaultDiscountFilter() *DiscountFilter {
	return &DiscountFilter{
		Page:      1,
		PageSize:  20,
		SortBy:    "created_at",
		SortOrder: "desc",
	}
}

// PaginatedResponse represents a paginated response
type PaginatedResponse[T any] struct {
	Items    []T `json:"items"`
	Total    int `json:"total"`
	Page     int `json:"page"`
	PageSize int `json:"page_size"`
	Pages    int `json:"pages"`
}

// APIResponse represents a standard API response
type APIResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
}

// LoginRequest represents a login request
type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

// TokenResponse represents JWT token response
type TokenResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	ExpiresIn   int    `json:"expires_in"`
}

// DiscountCreate represents request to create a discount
type DiscountCreate struct {
	Title                string       `json:"title"`
	Description          string       `json:"description,omitempty"`
	DiscountType         DiscountType `json:"discount_type"`
	DiscountValue        float64      `json:"discount_value"`
	MinPurchaseAmount    *float64     `json:"min_purchase_amount,omitempty"`
	OriginalPrice        *float64     `json:"original_price,omitempty"`
	DiscountedPrice      *float64     `json:"discounted_price,omitempty"`
	CategoryID           *int64       `json:"category_id,omitempty"`
	StoreID              int64        `json:"store_id"`
	PromoCode            string       `json:"promo_code,omitempty"`
	PromoCodeDescription string       `json:"promo_code_description,omitempty"`
	StartDate            *time.Time   `json:"start_date,omitempty"`
	EndDate              *time.Time   `json:"end_date,omitempty"`
	IsPersonal           bool         `json:"is_personal"`
	IsExclusive          bool         `json:"is_exclusive"`
	IsBankOffer          bool         `json:"is_bank_offer"`
	BankName             string       `json:"bank_name,omitempty"`
	SourceURL            string       `json:"source_url,omitempty"`
	ImageURL             string       `json:"image_url,omitempty"`
	TermsAndConditions   string       `json:"terms_and_conditions,omitempty"`
	ExternalID           string       `json:"external_id,omitempty"`
}

// DiscountUpdate represents request to update a discount
type DiscountUpdate struct {
	Title              string   `json:"title,omitempty"`
	Description        string   `json:"description,omitempty"`
	DiscountValue      *float64 `json:"discount_value,omitempty"`
	PromoCode          string   `json:"promo_code,omitempty"`
	IsActive           *bool    `json:"is_active,omitempty"`
	IsVerified         *bool    `json:"is_verified,omitempty"`
}

// StoreCreate represents request to create a store
type StoreCreate struct {
	Name        string    `json:"name"`
	Description string    `json:"description,omitempty"`
	StoreType   StoreType `json:"store_type"`
	WebsiteURL  string    `json:"website_url,omitempty"`
	LogoURL     string    `json:"logo_url,omitempty"`
	CatalogURL  string    `json:"catalog_url,omitempty"`
}

// StoreUpdate represents request to update a store
type StoreUpdate struct {
	Name        string    `json:"name,omitempty"`
	Description string    `json:"description,omitempty"`
	StoreType   *StoreType `json:"store_type,omitempty"`
	WebsiteURL  string    `json:"website_url,omitempty"`
	LogoURL     string    `json:"logo_url,omitempty"`
	CatalogURL  string    `json:"catalog_url,omitempty"`
	IsActive    *bool     `json:"is_active,omitempty"`
}

// CategoryCreate represents request to create a category
type CategoryCreate struct {
	Name     string `json:"name"`
	Slug     string `json:"slug"`
	ParentID *int64 `json:"parent_id,omitempty"`
	IconURL  string `json:"icon_url,omitempty"`
}

// CollectionCreate represents request to create a collection
type CollectionCreate struct {
	Title         string  `json:"title"`
	Description   string  `json:"description,omitempty"`
	CoverImageURL string  `json:"cover_image_url,omitempty"`
	DiscountIDs   []int64 `json:"discount_ids,omitempty"`
}

// FamilyCardCreate represents request to create a family card
type FamilyCardCreate struct {
	Name string `json:"name"`
}

// UserPreferenceCreate represents request to create/update user preference
type UserPreferenceCreate struct {
	CategoryID     *int64  `json:"category_id,omitempty"`
	StoreID        *int64  `json:"store_id,omitempty"`
	PreferenceType string  `json:"preference_type"`
	Score          float64 `json:"score"`
}
