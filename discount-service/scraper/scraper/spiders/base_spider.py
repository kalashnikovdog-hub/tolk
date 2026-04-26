import scrapy
import random
from datetime import datetime
from typing import Optional, Dict, Any

from scraper.settings import SCRAPER_USER_AGENTS


class BaseSpider(scrapy.Spider):
    """Base spider with common functionality"""
    
    name = "base_spider"
    allowed_domains = []
    start_urls = []
    
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 3,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store_info = {}
        self.scraped_at = datetime.utcnow()
    
    def get_random_user_agent(self) -> str:
        """Get random user agent from list"""
        return random.choice(SCRAPER_USER_AGENTS)
    
    def parse_discount_value(self, value_str: str) -> Optional[float]:
        """Parse discount value from string"""
        if not value_str:
            return None
        
        # Remove common symbols
        value_str = value_str.replace('%', '').replace('₽', '').replace('руб', '').strip()
        
        try:
            # Handle ranges like "10-20%"
            if '-' in value_str:
                parts = value_str.split('-')
                return float(parts[0])
            
            return float(value_str)
        except (ValueError, IndexError):
            return None
    
    def parse_price(self, price_str: str) -> Optional[float]:
        """Parse price from string"""
        if not price_str:
            return None
        
        # Remove common symbols and spaces
        price_str = price_str.replace('₽', '').replace('руб', '').replace(' ', '').strip()
        
        try:
            return float(price_str)
        except ValueError:
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats"""
        if not date_str:
            return None
        
        date_formats = [
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d %B %Y',
            '%d %b %Y',
            '%B %d, %Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def create_discount_item(
        self,
        title: str,
        description: Optional[str] = None,
        discount_type: str = "percentage",
        discount_value: Optional[float] = None,
        original_price: Optional[float] = None,
        discounted_price: Optional[float] = None,
        promo_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_url: Optional[str] = None,
        image_url: Optional[str] = None,
        category: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a standardized discount item"""
        
        return {
            'title': title,
            'description': description or '',
            'discount_type': discount_type,
            'discount_value': discount_value,
            'original_price': original_price,
            'discounted_price': discounted_price,
            'promo_code': promo_code,
            'start_date': start_date,
            'end_date': end_date,
            'source_url': source_url or self.start_urls[0] if self.start_urls else None,
            'image_url': image_url,
            'category': category,
            'external_id': external_id,
            'store_name': self.store_info.get('name'),
            'store_type': self.store_info.get('type', 'other'),
            'scraped_at': self.scraped_at,
        }
