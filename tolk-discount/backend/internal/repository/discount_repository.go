package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/discount-hub/api-gateway/internal/model"
)

// DiscountRepository handles discount data access
type DiscountRepository struct {
	db *sql.DB
}

// NewDiscountRepository creates a new discount repository
func NewDiscountRepository(db *sql.DB) *DiscountRepository {
	return &DiscountRepository{db: db}
}

// GetDiscounts retrieves discounts with filters
func (r *DiscountRepository) GetDiscounts(ctx context.Context, filters *model.DiscountFilter) ([]model.Discount, int64, error) {
	query := `
		SELECT d.id, d.title, d.description, d.discount_type, d.discount_value,
		       d.min_purchase_amount, d.original_price, d.discounted_price,
		       d.category_id, d.store_id, d.promo_code, d.promo_code_description,
		       d.start_date, d.end_date, d.is_personal, d.is_exclusive, d.is_bank_offer,
		       d.bank_name, d.source_url, d.image_url, d.terms_and_conditions,
		       d.is_active, d.is_verified, d.views_count, d.clicks_count,
		       d.external_id, d.scraped_at, d.created_at, d.updated_at,
		       s.id as store_id, s.name as store_name, s.description as store_description,
		       s.store_type, s.website_url, s.logo_url, s.catalog_url,
		       c.id as category_id, c.name as category_name, c.slug, c.icon_url
		FROM discounts d
		LEFT JOIN stores s ON d.store_id = s.id
		LEFT JOIN categories c ON d.category_id = c.id
		WHERE d.is_active = true
	`

	args := []interface{}{}
	argCount := 0

	if filters.CategoryID != nil {
		argCount++
		query += fmt.Sprintf(" AND d.category_id = $%d", argCount)
		args = append(args, *filters.CategoryID)
	}

	if filters.StoreID != nil {
		argCount++
		query += fmt.Sprintf(" AND d.store_id = $%d", argCount)
		args = append(args, *filters.StoreID)
	}

	if filters.DiscountType != nil {
		argCount++
		query += fmt.Sprintf(" AND d.discount_type = $%d", argCount)
		args = append(args, *filters.DiscountType)
	}

	if filters.MinDiscountValue != nil {
		argCount++
		query += fmt.Sprintf(" AND d.discount_value >= $%d", argCount)
		args = append(args, *filters.MinDiscountValue)
	}

	if filters.MaxDiscountValue != nil {
		argCount++
		query += fmt.Sprintf(" AND d.discount_value <= $%d", argCount)
		args = append(args, *filters.MaxDiscountValue)
	}

	if filters.IsPersonal != nil {
		argCount++
		query += fmt.Sprintf(" AND d.is_personal = $%d", argCount)
		args = append(args, *filters.IsPersonal)
	}

	if filters.IsExclusive != nil {
		argCount++
		query += fmt.Sprintf(" AND d.is_exclusive = $%d", argCount)
		args = append(args, *filters.IsExclusive)
	}

	if filters.IsBankOffer != nil {
		argCount++
		query += fmt.Sprintf(" AND d.is_bank_offer = $%d", argCount)
		args = append(args, *filters.IsBankOffer)
	}

	if filters.SearchQuery != "" {
		argCount++
		query += fmt.Sprintf(" AND (d.title ILIKE $%d OR d.description ILIKE $%d)", argCount, argCount)
		args = append(args, "%"+filters.SearchQuery+"%")
	}

	// Filter by date (only active discounts)
	argCount++
	query += fmt.Sprintf(" AND (d.end_date IS NULL OR d.end_date > $%d)", argCount)
	args = append(args, time.Now())

	// Count query
	countQuery := `SELECT COUNT(*) FROM (` + query + `) AS count_subquery`
	var total int64
	err := r.db.QueryRowContext(ctx, countQuery, args...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count discounts: %w", err)
	}

	// Sorting
	sortColumn := "d." + filters.SortBy
	if filters.SortOrder == "desc" {
		query += " ORDER BY " + sortColumn + " DESC"
	} else {
		query += " ORDER BY " + sortColumn + " ASC"
	}

	// Pagination
	offset := (filters.Page - 1) * filters.PageSize
	argCount++
	query += fmt.Sprintf(" LIMIT $%d OFFSET $%d", argCount+1, argCount+2)
	args = append(args, filters.PageSize, offset)

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query discounts: %w", err)
	}
	defer rows.Close()

	discounts, err := scanDiscounts(rows)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to scan discounts: %w", err)
	}

	return discounts, total, nil
}

// GetDiscountByID retrieves a discount by ID
func (r *DiscountRepository) GetDiscountByID(ctx context.Context, id int64) (*model.Discount, error) {
	query := `
		SELECT d.id, d.title, d.description, d.discount_type, d.discount_value,
		       d.min_purchase_amount, d.original_price, d.discounted_price,
		       d.category_id, d.store_id, d.promo_code, d.promo_code_description,
		       d.start_date, d.end_date, d.is_personal, d.is_exclusive, d.is_bank_offer,
		       d.bank_name, d.source_url, d.image_url, d.terms_and_conditions,
		       d.is_active, d.is_verified, d.views_count, d.clicks_count,
		       d.external_id, d.scraped_at, d.created_at, d.updated_at,
		       s.id as store_id, s.name as store_name, s.description as store_description,
		       s.store_type, s.website_url, s.logo_url, s.catalog_url,
		       c.id as category_id, c.name as category_name, c.slug, c.icon_url
		FROM discounts d
		LEFT JOIN stores s ON d.store_id = s.id
		LEFT JOIN categories c ON d.category_id = c.id
		WHERE d.id = $1
	`

	row := r.db.QueryRowContext(ctx, query, id)
	discounts, err := scanDiscountRows(row)
	if err != nil {
		return nil, err
	}

	if len(discounts) == 0 {
		return nil, sql.ErrNoRows
	}

	return &discounts[0], nil
}

// CreateDiscount creates a new discount
func (r *DiscountRepository) CreateDiscount(ctx context.Context, discount *model.DiscountCreate) (*model.Discount, error) {
	query := `
		INSERT INTO discounts (title, description, discount_type, discount_value, min_purchase_amount,
			original_price, discounted_price, category_id, store_id, promo_code, promo_code_description,
			start_date, end_date, is_personal, is_exclusive, is_bank_offer, bank_name, source_url,
			image_url, terms_and_conditions, external_id)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
		RETURNING id, created_at, updated_at
	`

	var createdAt, updatedAt time.Time
	err := r.db.QueryRowContext(ctx, query,
		discount.Title, discount.Description, discount.DiscountType, discount.DiscountValue,
		discount.MinPurchaseAmount, discount.OriginalPrice, discount.DiscountedPrice,
		discount.CategoryID, discount.StoreID, discount.PromoCode, discount.PromoCodeDescription,
		discount.StartDate, discount.EndDate, discount.IsPersonal, discount.IsExclusive,
		discount.IsBankOffer, discount.BankName, discount.SourceURL, discount.ImageURL,
		discount.TermsAndConditions, discount.ExternalID,
	).Scan(&createdAt, &updatedAt)

	if err != nil {
		return nil, fmt.Errorf("failed to create discount: %w", err)
	}

	result := &model.Discount{
		ID:                 0, // Will be populated after fetch
		Title:              discount.Title,
		Description:        discount.Description,
		DiscountType:       discount.DiscountType,
		DiscountValue:      discount.DiscountValue,
		MinPurchaseAmount:  discount.MinPurchaseAmount,
		OriginalPrice:      discount.OriginalPrice,
		DiscountedPrice:    discount.DiscountedPrice,
		CategoryID:         discount.CategoryID,
		StoreID:            discount.StoreID,
		PromoCode:          discount.PromoCode,
		PromoCodeDescription: discount.PromoCodeDescription,
		StartDate:          discount.StartDate,
		EndDate:            discount.EndDate,
		IsPersonal:         discount.IsPersonal,
		IsExclusive:        discount.IsExclusive,
		IsBankOffer:        discount.IsBankOffer,
		BankName:           discount.BankName,
		SourceURL:          discount.SourceURL,
		ImageURL:           discount.ImageURL,
		TermsAndConditions: discount.TermsAndConditions,
		IsActive:           true,
		IsVerified:         false,
		CreatedAt:          createdAt,
		UpdatedAt:          updatedAt,
	}

	return result, nil
}

// IncrementView increments the view count for a discount
func (r *DiscountRepository) IncrementView(ctx context.Context, id int64) error {
	query := `UPDATE discounts SET views_count = views_count + 1 WHERE id = $1`
	_, err := r.db.ExecContext(ctx, query, id)
	return err
}

// IncrementClick increments the click count for a discount
func (r *DiscountRepository) IncrementClick(ctx context.Context, id int64) error {
	query := `UPDATE discounts SET clicks_count = clicks_count + 1 WHERE id = $1`
	_, err := r.db.ExecContext(ctx, query, id)
	return err
}

func scanDiscounts(rows *sql.Rows) ([]model.Discount, error) {
	var discounts []model.Discount
	for rows.Next() {
		d, err := scanDiscountRow(rows)
		if err != nil {
			return nil, err
		}
		discounts = append(discounts, d)
	}
	return discounts, rows.Err()
}

func scanDiscountRows(row interface{ Scan(...interface{}) error }) ([]model.Discount, error) {
	d, err := scanDiscountRow(row)
	if err != nil {
		return nil, err
	}
	return []model.Discount{d}, nil
}

func scanDiscountRow(row interface{ Scan(...interface{}) error }) (model.Discount, error) {
	var d model.Discount
	var categoryID, storeCategoryID sql.NullInt64
	var startDate, endDate, scrapedAt, updatedAt sql.NullTime
	var minPurchaseAmount, originalPrice, discountedPrice sql.NullFloat64

	var store model.Store
	var category model.Category

	err := row.Scan(
		&d.ID, &d.Title, &d.Description, &d.DiscountType, &d.DiscountValue,
		&minPurchaseAmount, &originalPrice, &discountedPrice,
		&categoryID, &d.StoreID, &d.PromoCode, &d.PromoCodeDescription,
		&startDate, &endDate, &d.IsPersonal, &d.IsExclusive, &d.IsBankOffer,
		&d.BankName, &d.SourceURL, &d.ImageURL, &d.TermsAndConditions,
		&d.IsActive, &d.IsVerified, &d.ViewsCount, &d.ClicksCount,
		&d.ExternalID, &scrapedAt, &d.CreatedAt, &updatedAt,
		&store.ID, &store.Name, &store.Description, &store.StoreType, &store.WebsiteURL, &store.LogoURL, &store.CatalogURL,
		&category.ID, &category.Name, &category.Slug, &category.IconURL,
	)

	if err != nil {
		return d, err
	}

	if categoryID.Valid {
		d.CategoryID = &categoryID.Int64
		d.Category = &category
	}
	if store.ID > 0 {
		d.Store = &store
	}
	if minPurchaseAmount.Valid {
		d.MinPurchaseAmount = &minPurchaseAmount.Float64
	}
	if originalPrice.Valid {
		d.OriginalPrice = &originalPrice.Float64
	}
	if discountedPrice.Valid {
		d.DiscountedPrice = &discountedPrice.Float64
	}
	if startDate.Valid {
		d.StartDate = &startDate.Time
	}
	if endDate.Valid {
		d.EndDate = &endDate.Time
	}
	if scrapedAt.Valid {
		d.ScrapedAt = &scrapedAt.Time
	}
	if updatedAt.Valid {
		d.UpdatedAt = &updatedAt.Time
	}

	return d, nil
}
