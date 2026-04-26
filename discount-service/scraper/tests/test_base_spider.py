"""Tests for the base spider module"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from scraper.spiders.base_spider import BaseSpider


class TestBaseSpider:
    """Test suite for BaseSpider class"""

    @pytest.fixture
    def spider(self):
        """Create a base spider instance for testing"""
        return BaseSpider()

    def test_get_random_user_agent(self, spider):
        """Test getting a random user agent"""
        with patch('scraper.spiders.base_spider.SCRAPER_USER_AGENTS', 
                   ['Agent1', 'Agent2', 'Agent3']):
            user_agent = spider.get_random_user_agent()
            
            assert user_agent in ['Agent1', 'Agent2', 'Agent3']

    def test_parse_discount_value_percentage(self, spider):
        """Test parsing percentage discount value"""
        result = spider.parse_discount_value("15%")
        assert result == 15.0

    def test_parse_discount_value_fixed(self, spider):
        """Test parsing fixed discount value"""
        result = spider.parse_discount_value("100₽")
        assert result == 100.0

    def test_parse_discount_value_rubles(self, spider):
        """Test parsing ruble discount value"""
        result = spider.parse_discount_value("50руб")
        assert result == 50.0

    def test_parse_discount_value_range(self, spider):
        """Test parsing range discount value"""
        result = spider.parse_discount_value("10-20%")
        assert result == 10.0

    def test_parse_discount_value_plain_number(self, spider):
        """Test parsing plain number"""
        result = spider.parse_discount_value("25")
        assert result == 25.0

    def test_parse_discount_value_empty(self, spider):
        """Test parsing empty string"""
        result = spider.parse_discount_value("")
        assert result is None

    def test_parse_discount_value_none(self, spider):
        """Test parsing None value"""
        result = spider.parse_discount_value(None)
        assert result is None

    def test_parse_discount_value_invalid(self, spider):
        """Test parsing invalid value"""
        result = spider.parse_discount_value("invalid")
        assert result is None

    def test_parse_price_with_spaces(self, spider):
        """Test parsing price with spaces"""
        result = spider.parse_price("1 000 ₽")
        assert result == 1000.0

    def test_parse_price_with_ruble_symbol(self, spider):
        """Test parsing price with ruble symbol"""
        result = spider.parse_price("500₽")
        assert result == 500.0

    def test_parse_price_with_rub_text(self, spider):
        """Test parsing price with rub text"""
        result = spider.parse_price("750руб")
        assert result == 750.0

    def test_parse_price_plain_number(self, spider):
        """Test parsing plain number price"""
        result = spider.parse_price("999")
        assert result == 999.0

    def test_parse_price_empty(self, spider):
        """Test parsing empty price"""
        result = spider.parse_price("")
        assert result is None

    def test_parse_price_none(self, spider):
        """Test parsing None price"""
        result = spider.parse_price(None)
        assert result is None

    def test_parse_price_invalid(self, spider):
        """Test parsing invalid price"""
        result = spider.parse_price("free")
        assert result is None

    def test_parse_date_dd_mm_yyyy(self, spider):
        """Test parsing DD.MM.YYYY format"""
        result = spider.parse_date("25.12.2024")
        assert result == datetime(2024, 12, 25)

    def test_parse_date_dd_slash_mm_slash_yyyy(self, spider):
        """Test parsing DD/MM/YYYY format"""
        result = spider.parse_date("25/12/2024")
        assert result == datetime(2024, 12, 25)

    def test_parse_date_iso_format(self, spider):
        """Test parsing ISO format"""
        result = spider.parse_date("2024-12-25")
        assert result == datetime(2024, 12, 25)

    def test_parse_date_full_month_name(self, spider):
        """Test parsing full month name format"""
        result = spider.parse_date("25 December 2024")
        assert result == datetime(2024, 12, 25)

    def test_parse_date_abbreviated_month(self, spider):
        """Test parsing abbreviated month format"""
        result = spider.parse_date("25 Dec 2024")
        assert result == datetime(2024, 12, 25)

    def test_parse_date_us_format(self, spider):
        """Test parsing US format"""
        result = spider.parse_date("December 25, 2024")
        assert result == datetime(2024, 12, 25)

    def test_parse_date_empty(self, spider):
        """Test parsing empty date"""
        result = spider.parse_date("")
        assert result is None

    def test_parse_date_none(self, spider):
        """Test parsing None date"""
        result = spider.parse_date(None)
        assert result is None

    def test_parse_date_invalid(self, spider):
        """Test parsing invalid date"""
        result = spider.parse_date("not a date")
        assert result is None

    def test_create_discount_item_minimal(self, spider):
        """Test creating minimal discount item"""
        result = spider.create_discount_item(title="Test Discount")
        
        assert result['title'] == "Test Discount"
        assert result['description'] == ''
        assert result['discount_type'] == "percentage"
        assert 'scraped_at' in result

    def test_create_discount_item_full(self, spider):
        """Test creating full discount item"""
        result = spider.create_discount_item(
            title="Sale",
            description="Big sale",
            discount_type="fixed",
            discount_value=100.0,
            original_price=500.0,
            discounted_price=400.0,
            promo_code="SAVE100",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            source_url="https://example.com",
            image_url="https://example.com/image.jpg",
            category="electronics",
            external_id="ext123"
        )
        
        assert result['title'] == "Sale"
        assert result['description'] == "Big sale"
        assert result['discount_type'] == "fixed"
        assert result['discount_value'] == 100.0
        assert result['original_price'] == 500.0
        assert result['discounted_price'] == 400.0
        assert result['promo_code'] == "SAVE100"
        assert result['category'] == "electronics"
        assert result['external_id'] == "ext123"

    def test_create_discount_item_with_store_info(self, spider):
        """Test creating discount item with store info"""
        spider.store_info = {'name': 'Test Store', 'type': 'grocery'}
        
        result = spider.create_discount_item(title="Test")
        
        assert result['store_name'] == 'Test Store'
        assert result['store_type'] == 'grocery'

    def test_init_sets_scraped_at(self, spider):
        """Test that __init__ sets scraped_at timestamp"""
        assert isinstance(spider.scraped_at, datetime)

    def test_init_empty_store_info(self, spider):
        """Test that __init__ initializes empty store_info"""
        assert spider.store_info == {}


class TestBaseSpiderInheritance:
    """Test suite for spiders inheriting from BaseSpider"""

    def test_grocery_spider_inherits_base_methods(self):
        """Test that GrocerySpider inherits base parsing methods"""
        from scraper.spiders.grocery_spider import GrocerySpider
        
        spider = GrocerySpider(store="5ka")
        
        # Should inherit parse_discount_value
        assert hasattr(spider, 'parse_discount_value')
        result = spider.parse_discount_value("20%")
        assert result == 20.0
        
        # Should inherit parse_price
        assert hasattr(spider, 'parse_price')
        result = spider.parse_price("100₽")
        assert result == 100.0
        
        # Should inherit parse_date
        assert hasattr(spider, 'parse_date')
        result = spider.parse_date("01.01.2024")
        assert result == datetime(2024, 1, 1)
        
        # Should inherit create_discount_item
        assert hasattr(spider, 'create_discount_item')
