import scrapy
from typing import List, Dict, Any
from datetime import datetime, timedelta

from scraper.spiders.base_spider import BaseSpider


class GrocerySpider(BaseSpider):
    """Spider for grocery stores (Пятерочка, Перекресток, Магнит, etc.)"""
    
    name = "grocery_spider"
    allowed_domains = [
        "5ka.ru",
        "perekrestok.ru",
        "magnit.ru",
        "lenta.com",
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
    }
    
    def __init__(self, store: str = "all", *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.stores_config = {
            "5ka": {
                "name": "Пятерочка",
                "url": "https://5ka.ru/promo",
                "type": "grocery",
            },
            "perekrestok": {
                "name": "Перекресток",
                "url": "https://perekrestok.ru/catalog/promo",
                "type": "grocery",
            },
            "magnit": {
                "name": "Магнит",
                "url": "https://magnit.ru/promo",
                "type": "grocery",
            },
            "lenta": {
                "name": "Лента",
                "url": "https://lenta.com/promo",
                "type": "grocery",
            },
        }
        
        if store == "all":
            self.start_urls = [config["url"] for config in self.stores_config.values()]
        elif store in self.stores_config:
            self.store_info = self.stores_config[store]
            self.start_urls = [self.stores_config[store]["url"]]
        else:
            self.logger.warning(f"Unknown store: {store}, using all stores")
            self.start_urls = [config["url"] for config in self.stores_config.values()]
    
    def start_requests(self):
        """Generate initial requests with proper headers"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={'User-Agent': self.get_random_user_agent()},
                meta={'dont_redirect': True}
            )
    
    def parse(self, response):
        """Parse store page and extract discounts"""
        # Determine which store we're parsing
        for store_key, store_config in self.stores_config.items():
            if store_config["url"] in response.url:
                self.store_info = store_config
                break
        
        # Parse based on store type
        if "5ka.ru" in response.url:
            yield from self.parse_5ka(response)
        elif "perekrestok.ru" in response.url:
            yield from self.parse_perekrestok(response)
        elif "magnit.ru" in response.url:
            yield from self.parse_magnit(response)
        elif "lenta.com" in response.url:
            yield from self.parse_lenta(response)
        else:
            # Generic parsing
            yield from self.parse_generic(response)
    
    def parse_5ka(self, response) -> List[Dict[str, Any]]:
        """Parse Пятерочка discounts"""
        items = response.css('.product-card, .promo-item')
        
        for item in items:
            title = item.css('.product-title::text, .title::text').get()
            if not title:
                continue
            
            price_str = item.css('.price-current::text, .price::text').get()
            old_price_str = item.css('.price-old::text').get()
            
            discount_value = None
            if old_price_str and price_str:
                try:
                    old_price = self.parse_price(old_price_str)
                    new_price = self.parse_price(price_str)
                    if old_price and new_price and old_price > new_price:
                        discount_value = round(((old_price - new_price) / old_price) * 100, 1)
                except:
                    pass
            
            image_url = item.css('img::attr(src)').get()
            if image_url and not image_url.startswith('http'):
                image_url = response.urljoin(image_url)
            
            yield self.create_discount_item(
                title=title.strip(),
                discount_type="percentage",
                discount_value=discount_value,
                original_price=self.parse_price(old_price_str),
                discounted_price=self.parse_price(price_str),
                image_url=image_url,
                end_date=datetime.utcnow() + timedelta(days=7),  # Default validity
            )
    
    def parse_perekrestok(self, response) -> List[Dict[str, Any]]:
        """Parse Перекресток discounts"""
        items = response.css('.product-card, .catalog-item')
        
        for item in items:
            title = item.css('.product-name::text, .name::text').get()
            if not title:
                continue
            
            price_str = item.css('.current-price::text, .price::text').get()
            old_price_str = item.css('.old-price::text').get()
            
            yield self.create_discount_item(
                title=title.strip(),
                discount_type="percentage",
                original_price=self.parse_price(old_price_str),
                discounted_price=self.parse_price(price_str),
                end_date=datetime.utcnow() + timedelta(days=7),
            )
    
    def parse_magnit(self, response) -> List[Dict[str, Any]]:
        """Parse Магнит discounts"""
        items = response.css('.goods-item, .product-card')
        
        for item in items:
            title = item.css('.goods-name::text, .title::text').get()
            if not title:
                continue
            
            price_str = item.css('.price-value::text, .price::text').get()
            
            yield self.create_discount_item(
                title=title.strip(),
                discounted_price=self.parse_price(price_str),
                end_date=datetime.utcnow() + timedelta(days=7),
            )
    
    def parse_lenta(self, response) -> List[Dict[str, Any]]:
        """Parse Лента discounts"""
        items = response.css('.product-tile, .card-product')
        
        for item in items:
            title = item.css('.product-title::text, .title::text').get()
            if not title:
                continue
            
            price_str = item.css('.price-current::text, .price::text').get()
            old_price_str = item.css('.price-old::text').get()
            
            yield self.create_discount_item(
                title=title.strip(),
                original_price=self.parse_price(old_price_str),
                discounted_price=self.parse_price(price_str),
                end_date=datetime.utcnow() + timedelta(days=7),
            )
    
    def parse_generic(self, response) -> List[Dict[str, Any]]:
        """Generic parser for unknown store layouts"""
        # Try to find any product-like elements
        selectors = [
            '.product', '.item', '.card', '.offer', '.deal', '.promo'
        ]
        
        for selector in selectors:
            items = response.css(selector)
            for item in items:
                title = item.css('h1::text, h2::text, h3::text, .title::text, a::text').get()
                if title:
                    yield self.create_discount_item(
                        title=title.strip()[:200],
                        end_date=datetime.utcnow() + timedelta(days=7),
                    )
                    break  # Only take first match per selector
