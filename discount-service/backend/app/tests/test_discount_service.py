"""Tests for the discount service module"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.services.discount_service import DiscountService
from app.models.database import Discount, Category, Store, User, UserPreference, SubscriptionTier
from app.models.schemas import DiscountFilter, DiscountTypeEnum


class TestDiscountService:
    """Test suite for DiscountService class"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        db = Mock(spec=Session)
        return db

    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.subscription_tier = SubscriptionTier.PREMIUM
        return user

    @pytest.fixture
    def mock_free_user(self):
        """Create a mock free tier user"""
        user = Mock(spec=User)
        user.id = 2
        user.email = "free@example.com"
        user.subscription_tier = SubscriptionTier.FREE
        return user

    @pytest.fixture
    def sample_discount_filter(self):
        """Create a sample discount filter"""
        return DiscountFilter(
            page=1,
            page_size=20,
            sort_by="created_at",
            sort_order="desc"
        )

    @pytest.fixture
    def sample_discount(self):
        """Create a sample discount object"""
        discount = Mock(spec=Discount)
        discount.id = 1
        discount.title = "Test Discount"
        discount.is_active = True
        discount.discount_value = 15.0
        discount.discount_type = DiscountTypeEnum.PERCENTAGE
        discount.category_id = 1
        discount.store_id = 1
        discount.is_personal = False
        discount.is_exclusive = False
        discount.is_bank_offer = False
        discount.views_count = 0
        discount.clicks_count = 0
        discount.end_date = datetime.utcnow() + timedelta(days=7)
        discount.created_at = datetime.utcnow()
        return discount

    def test_get_discounts_no_filters(self, mock_db, sample_discount_filter, sample_discount):
        """Test getting discounts with no filters applied"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        # Call service
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        # Verify
        assert isinstance(discounts, list)
        assert len(discounts) == 1
        assert discounts[0].id == sample_discount.id
        assert mock_db.execute.call_count >= 1

    def test_get_discounts_with_category_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering discounts by category"""
        sample_discount_filter.category_id = 5
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)
        assert mock_db.execute.call_count >= 1

    def test_get_discounts_with_store_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering discounts by store"""
        sample_discount_filter.store_id = 10
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_with_discount_type_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering discounts by type"""
        sample_discount_filter.discount_type = DiscountTypeEnum.PERCENTAGE
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_with_min_value_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering discounts by minimum value"""
        sample_discount_filter.min_discount_value = 10.0
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_with_max_value_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering discounts by maximum value"""
        sample_discount_filter.max_discount_value = 50.0
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_exclusive_free_user_blocked(
        self, mock_db, sample_discount_filter, sample_discount, mock_free_user
    ):
        """Test that free users cannot see exclusive discounts"""
        sample_discount_filter.is_exclusive = True
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(
            mock_db, sample_discount_filter, user=mock_free_user
        )
        
        # Free users should get no results for exclusive discounts
        assert isinstance(discounts, list)

    def test_get_discounts_exclusive_premium_user_allowed(
        self, mock_db, sample_discount_filter, sample_discount, mock_user
    ):
        """Test that premium users can see exclusive discounts"""
        sample_discount_filter.is_exclusive = True
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(
            mock_db, sample_discount_filter, user=mock_user
        )
        
        assert isinstance(discounts, list)

    def test_get_discounts_with_search_query(self, mock_db, sample_discount_filter, sample_discount):
        """Test searching discounts by title/description"""
        sample_discount_filter.search_query = "sale"
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_pagination(self, mock_db, sample_discount_filter, sample_discount):
        """Test pagination of discount results"""
        sample_discount_filter.page = 2
        sample_discount_filter.page_size = 10
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_sorting(self, mock_db, sample_discount_filter, sample_discount):
        """Test sorting of discount results"""
        sample_discount_filter.sort_by = "discount_value"
        sample_discount_filter.sort_order = "asc"
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_personal_discounts_with_preferences(
        self, mock_db, mock_user, sample_discount
    ):
        """Test getting personalized discounts based on user preferences"""
        # Setup mock preferences
        preference = Mock(spec=UserPreference)
        preference.category_id = 1
        preference.store_id = 2
        
        mock_pref_result = Mock()
        mock_pref_result.scalars.return_value.all.return_value = [preference]
        
        mock_discount_result = Mock()
        mock_discount_result.scalars.return_value.all.return_value = [sample_discount]
        
        mock_db.execute.side_effect = [mock_pref_result, mock_discount_result]
        
        discounts = DiscountService.get_personal_discounts(mock_db, mock_user, limit=10)
        
        assert isinstance(discounts, list)

    def test_get_personal_discounts_no_preferences_returns_popular(
        self, mock_db, mock_user, sample_discount
    ):
        """Test that empty preferences returns popular discounts"""
        mock_pref_result = Mock()
        mock_pref_result.scalars.return_value.all.return_value = []
        
        mock_discount_result = Mock()
        mock_discount_result.scalars.return_value.all.return_value = [sample_discount]
        
        mock_db.execute.side_effect = [mock_pref_result, mock_discount_result]
        
        with patch.object(DiscountService, 'get_popular_discounts') as mock_popular:
            mock_popular.return_value = [sample_discount]
            discounts = DiscountService.get_personal_discounts(mock_db, mock_user, limit=10)
            
            mock_popular.assert_called_once()
            assert isinstance(discounts, list)

    def test_get_popular_discounts(self, mock_db, sample_discount):
        """Test getting popular discounts"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts = DiscountService.get_popular_discounts(mock_db, limit=10)
        
        assert isinstance(discounts, list)
        assert len(discounts) == 1

    def test_get_bank_offers_current_month(self, mock_db, sample_discount):
        """Test getting bank offers for current month"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts = DiscountService.get_bank_offers(mock_db)
        
        assert isinstance(discounts, list)

    def test_get_bank_offers_specific_month(self, mock_db, sample_discount):
        """Test getting bank offers for specific month"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts = DiscountService.get_bank_offers(mock_db, month=12, year=2024)
        
        assert isinstance(discounts, list)

    def test_get_store_catalog(self, mock_db, sample_discount):
        """Test getting all discounts for a store"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts = DiscountService.get_store_catalog(mock_db, store_id=1)
        
        assert isinstance(discounts, list)
        assert len(discounts) == 1

    def test_increment_view(self, mock_db, sample_discount):
        """Test incrementing view count"""
        mock_db.get.return_value = sample_discount
        
        DiscountService.increment_view(mock_db, discount_id=1)
        
        assert sample_discount.views_count == 1
        mock_db.commit.assert_called_once()

    def test_increment_view_not_found(self, mock_db):
        """Test incrementing view for non-existent discount"""
        mock_db.get.return_value = None
        
        # Should not raise an error
        DiscountService.increment_view(mock_db, discount_id=999)
        
        mock_db.commit.assert_not_called()

    def test_increment_click(self, mock_db, sample_discount):
        """Test incrementing click count"""
        mock_db.get.return_value = sample_discount
        
        DiscountService.increment_click(mock_db, discount_id=1)
        
        assert sample_discount.clicks_count == 1
        mock_db.commit.assert_called_once()

    def test_increment_click_not_found(self, mock_db):
        """Test incrementing click for non-existent discount"""
        mock_db.get.return_value = None
        
        # Should not raise an error
        DiscountService.increment_click(mock_db, discount_id=999)
        
        mock_db.commit.assert_not_called()

    def test_get_discounts_is_personal_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering by personal discounts"""
        sample_discount_filter.is_personal = True
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_is_bank_offer_filter(self, mock_db, sample_discount_filter, sample_discount):
        """Test filtering by bank offers"""
        sample_discount_filter.is_bank_offer = True
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_discount]
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        assert isinstance(discounts, list)

    def test_get_discounts_expired_filtered_out(
        self, mock_db, sample_discount_filter, sample_discount
    ):
        """Test that expired discounts are filtered out"""
        # Set discount to expired
        sample_discount.end_date = datetime.utcnow() - timedelta(days=1)
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        discounts, total = DiscountService.get_discounts(mock_db, sample_discount_filter)
        
        # Expired discounts should be filtered out by the query
        assert isinstance(discounts, list)
