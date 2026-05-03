package service

import (
	"context"
	"fmt"
	"time"

	"github.com/discount-hub/api-gateway/internal/model"
	"github.com/discount-hub/api-gateway/internal/repository"
	"github.com/discount-hub/api-gateway/pkg/cache"
)

// DiscountService handles discount business logic
type DiscountService struct {
	repo  *repository.DiscountRepository
	cache *cache.Cache
}

// NewDiscountService creates a new discount service
func NewDiscountService(repo *repository.DiscountRepository, cache *cache.Cache) *DiscountService {
	return &DiscountService{
		repo:  repo,
		cache: cache,
	}
}

// GetDiscounts retrieves discounts with filters
func (s *DiscountService) GetDiscounts(ctx context.Context, filters *model.DiscountFilter) ([]model.Discount, int64, error) {
	// Try cache first
	if s.cache != nil && filters.Page == 1 && filters.SortBy == "created_at" {
		cacheKey := fmt.Sprintf("discounts:list:%d:%d:%s", 
			pageSize(filters), filters.CategoryID, filters.StoreID)
		
		var cached []model.Discount
		if err := s.cache.Get(ctx, cacheKey, &cached); err == nil {
			return cached, int64(len(cached)), nil
		}
	}

	discounts, total, err := s.repo.GetDiscounts(ctx, filters)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to get discounts: %w", err)
	}

	// Cache the result for 5 minutes
	if s.cache != nil && len(discounts) > 0 {
		cacheKey := fmt.Sprintf("discounts:list:%d:%d:%s", 
			filters.PageSize, filters.CategoryID, filters.StoreID)
		s.cache.Set(ctx, cacheKey, discounts, 5*time.Minute)
	}

	return discounts, total, nil
}

// GetDiscountByID retrieves a discount by ID
func (s *DiscountService) GetDiscountByID(ctx context.Context, id int64) (*model.Discount, error) {
	// Try cache first
	if s.cache != nil {
		cacheKey := fmt.Sprintf("discount:%d", id)
		var cached model.Discount
		if err := s.cache.Get(ctx, cacheKey, &cached); err == nil {
			return &cached, nil
		}
	}

	discount, err := s.repo.GetDiscountByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get discount: %w", err)
	}

	// Cache the result for 5 minutes
	if s.cache != nil {
		cacheKey := fmt.Sprintf("discount:%d", id)
		s.cache.Set(ctx, cacheKey, discount, 5*time.Minute)
	}

	return discount, nil
}

// CreateDiscount creates a new discount
func (s *DiscountService) CreateDiscount(ctx context.Context, discount *model.DiscountCreate) (*model.Discount, error) {
	result, err := s.repo.CreateDiscount(ctx, discount)
	if err != nil {
		return nil, fmt.Errorf("failed to create discount: %w", err)
	}

	// Invalidate cache
	if s.cache != nil {
		s.cache.Delete(ctx, "discounts:list:*")
	}

	return result, nil
}

// IncrementView increments the view count for a discount
func (s *DiscountService) IncrementView(ctx context.Context, id int64) error {
	return s.repo.IncrementView(ctx, id)
}

// IncrementClick increments the click count for a discount
func (s *DiscountService) IncrementClick(ctx context.Context, id int64) error {
	return s.repo.IncrementClick(ctx, id)
}

// GetPersonalDiscounts returns personalized discounts for a user
func (s *DiscountService) GetPersonalDiscounts(ctx context.Context, userID int64, limit int) ([]model.Discount, error) {
	// TODO: Implement personalization based on user preferences
	// For now, return popular discounts
	return s.GetPopularDiscounts(ctx, limit)
}

// GetPopularDiscounts returns most popular discounts
func (s *DiscountService) GetPopularDiscounts(ctx context.Context, limit int) ([]model.Discount, error) {
	filters := model.DefaultDiscountFilter()
	filters.PageSize = limit
	filters.SortBy = "views_count"
	filters.SortOrder = "desc"

	discounts, _, err := s.GetDiscounts(ctx, filters)
	return discounts, err
}

// GetBankOffers returns special bank offers for the current month
func (s *DiscountService) GetBankOffers(ctx context.Context, month, year int) ([]model.Discount, error) {
	filters := model.DefaultDiscountFilter()
	filters.IsBankOffer = boolPtr(true)
	filters.PageSize = 100

	discounts, _, err := s.GetDiscounts(ctx, filters)
	return discounts, err
}

func pageSize(f *model.DiscountFilter) int {
	if f.PageSize > 0 {
		return f.PageSize
	}
	return 20
}

func boolPtr(b bool) *bool {
	return &b
}
