import scrapy
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

from scraper.spiders.base_spider import BaseSpider


logger = logging.getLogger(__name__)


class ProxyPool:
    """Simple proxy pool with rotation"""
    
    def __init__(self):
        self.proxies = [
            # Free proxy examples - in production use paid proxy service
            # 'http://proxy1.example.com:8080',
            # 'http://proxy2.example.com:8080',
        ]
        self.current_index = 0
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from pool"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return {'http': proxy, 'https': proxy}
    
    def add_proxy(self, proxy_url: str):
        """Add proxy to pool"""
        if proxy_url not in self.proxies:
            self.proxies.append(proxy_url)


# Global proxy pool
proxy_pool = ProxyPool()


class ImprovedBaseSpider(BaseSpider):
    """Enhanced base spider with retry logic and proxy rotation"""
    
    name = "improved_base_spider"
    
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        },
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed_urls = []
        self.retry_count = {}
    
    def get_random_user_agent(self) -> str:
        """Get random user agent from extended list"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        ]
        return random.choice(user_agents)
    
    def start_requests(self):
        """Generate initial requests with proper headers and proxy rotation"""
        for url in self.start_urls:
            yield self.make_request(url, callback=self.parse)
    
    def make_request(
        self,
        url: str,
        callback=None,
        method: str = 'GET',
        meta: Optional[Dict] = None
    ):
        """Create request with headers and optional proxy"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
        }
        
        # Add proxy if available
        proxy = proxy_pool.get_next_proxy()
        
        request_meta = {
            'dont_redirect': True,
            'handle_httpstatus_list': [301, 302, 429],
            **(meta or {})
        }
        
        return scrapy.Request(
            url=url,
            callback=callback,
            method=method,
            headers=headers,
            meta=request_meta,
            dont_filter=True
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(scrapy.exceptions.IgnoreRequest)
    )
    def parse_with_retry(self, response):
        """Parse with automatic retry on failure"""
        return self.parse(response)
    
    def handle_error(self, failure):
        """Handle request failures"""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {repr(failure)}")
        
        # Track failed URLs
        self.failed_urls.append({
            'url': failure.request.url,
            'error': str(failure.value),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Retry with different proxy if available
        if failure.check(scrapy.exceptions.IgnoreRequest):
            proxy = proxy_pool.get_next_proxy()
            if proxy:
                self.logger.info(f"Retrying with new proxy: {proxy}")
                return self.make_request(
                    failure.request.url,
                    callback=self.parse
                )
    
    def is_valid_response(self, response) -> bool:
        """Check if response is valid (not blocked/captcha)"""
        # Check for common block indicators
        block_indicators = [
            'captcha',
            'access denied',
            'blocked',
            'forbidden',
            'too many requests'
        ]
        
        response_text = response.text.lower()
        for indicator in block_indicators:
            if indicator in response_text:
                self.logger.warning(f"Response appears to be blocked: {indicator}")
                return False
        
        # Check status code
        if response.status in [403, 429, 503]:
            self.logger.warning(f"Blocked with status {response.status}")
            return False
        
        # Check content length (too short might indicate block)
        if len(response.body) < 1000:
            self.logger.warning("Response too short, possible block")
            return False
        
        return True


class ImprovedGrocerySpider(ImprovedBaseSpider):
    """Enhanced grocery spider with retry logic and proxy rotation"""
    
    name = "improved_grocery_spider"
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
        """Parse store page and extract discounts with validation"""
        # Validate response first
        if not self.is_valid_response(response):
            self.logger.warning(f"Invalid response from {response.url}, skipping")
            return
        
        # Determine which store we're parsing
        for store_key, store_config in self.stores_config.items():
            if store_config["url"] in response.url:
                self.store_info = store_config
                break
        
        # Parse based on store type
        try:
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
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")
            # Track error for monitoring
            self.failed_urls.append({
                'url': response.url,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
    
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
