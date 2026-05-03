#!/usr/bin/env python3
"""
Discount Daemon - Сервис для автоматического сбора скидок
Запускается как демон, работает по расписанию или по команде
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import signal
import json
import re

import aiohttp
import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telethon import TelegramClient, events
from telethon.tl.types import Message
import hashlib
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/discount_daemon.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('discount_daemon')


class DiscountDaemon:
    """Основной класс демона для сбора скидок"""
    
    def __init__(self):
        # Конфигурация из переменных окружения
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/discounts'
        )
        self.telegram_api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        self.telegram_api_hash = os.getenv('TELEGRAM_API_HASH', '')
        self.telegram_session = os.getenv('TELEGRAM_SESSION', 'discount_daemon.session')
        self.scrape_interval_hours = int(os.getenv('SCRAPE_INTERVAL', '6'))
        
        # Каналы Telegram для мониторинга
        self.telegram_channels = os.getenv(
            'TELEGRAM_CHANNELS',
            'skidki_online,golddays,edadeal'
        ).split(',')
        
        # Сайты для парсинга
        self.target_websites = json.loads(os.getenv(
            'TARGET_WEBSITES',
            '''[
                {"name": "Пятерочка", "url": "https://5ka.ru/promo", "type": "grocery"},
                {"name": "Перекресток", "url": "https://perekrestok.ru/catalog/promo", "type": "grocery"},
                {"name": "Магнит", "url": "https://magnit.ru/promo", "type": "grocery"},
                {"name": "Лента", "url": "https://lenta.com/promo", "type": "grocery"}
            ]'''
        ))
        
        # Клиенты
        self.db_pool: Optional[asyncpg.Pool] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.telegram_client: Optional[TelegramClient] = None
        self.scheduler: Optional[AsyncIOScheduler] = None
        
        # Флаги управления
        self.running = False
        self.processed_message_ids: set = set()
        
    async def initialize(self):
        """Инициализация всех компонентов"""
        logger.info("Инициализация демона...")
        
        # Инициализация пула соединений с БД
        self.db_pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("Подключение к базе данных установлено")
        
        # Инициализация HTTP сессии
        self.http_session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        logger.info("HTTP сессия создана")
        
        # Инициализация Telegram клиента
        if self.telegram_api_id and self.telegram_api_hash:
            self.telegram_client = TelegramClient(
                self.telegram_session,
                self.telegram_api_id,
                self.telegram_api_hash
            )
            await self.telegram_client.start()
            logger.info(f"Telegram клиент инициализирован")
        else:
            logger.warning("Telegram API не настроен, мониторинг каналов отключен")
        
        # Инициализация планировщика
        self.scheduler = AsyncIOScheduler()
        logger.info("Планировщик задач создан")
        
    async def cleanup(self):
        """Очистка ресурсов"""
        logger.info("Остановка демона...")
        self.running = False
        
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
        
        if self.http_session:
            await self.http_session.close()
        
        if self.db_pool:
            await self.db_pool.close()
        
        if self.telegram_client:
            await self.telegram_client.disconnect()
        
        logger.info("Демон остановлен")
    
    async def save_discount(self, discount_data: Dict[str, Any]) -> Optional[int]:
        """Сохранение скидки в базу данных"""
        try:
            async with self.db_pool.acquire() as conn:
                # Проверка на дубликаты
                existing = await conn.fetchrow(
                    '''SELECT id FROM discounts 
                       WHERE external_id = $1 OR 
                       (title = $2 AND store_id = $3)''',
                    discount_data.get('external_id'),
                    discount_data.get('title'),
                    discount_data.get('store_id')
                )
                
                if existing:
                    logger.debug(f"Скидка уже существует: {discount_data.get('title')}")
                    return existing['id']
                
                # Вставка новой скидки
                result = await conn.fetchrow(
                    '''INSERT INTO discounts (
                        title, description, discount_type, discount_value,
                        original_price, discounted_price, promo_code,
                        start_date, end_date, source_url, image_url,
                        category_id, store_id, is_personal, is_exclusive,
                        is_bank_offer, bank_name, external_id, scraped_at,
                        is_active, is_verified
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                        $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
                    ) RETURNING id''',
                    discount_data.get('title'),
                    discount_data.get('description', ''),
                    discount_data.get('discount_type', 'percentage'),
                    discount_data.get('discount_value'),
                    discount_data.get('original_price'),
                    discount_data.get('discounted_price'),
                    discount_data.get('promo_code'),
                    discount_data.get('start_date'),
                    discount_data.get('end_date'),
                    discount_data.get('source_url'),
                    discount_data.get('image_url'),
                    discount_data.get('category_id'),
                    discount_data.get('store_id'),
                    discount_data.get('is_personal', False),
                    discount_data.get('is_exclusive', False),
                    discount_data.get('is_bank_offer', False),
                    discount_data.get('bank_name'),
                    discount_data.get('external_id'),
                    discount_data.get('scraped_at', datetime.utcnow()),
                    True,
                    False
                )
                
                discount_id = result['id']
                logger.info(f"Сохранена новая скидка ID={discount_id}: {discount_data.get('title')}")
                return discount_id
                
        except Exception as e:
            logger.error(f"Ошибка при сохранении скидки: {e}")
            return None
    
    async def get_or_create_store(self, store_name: str, store_type: str = 'other') -> int:
        """Получить или создать магазин"""
        async with self.db_pool.acquire() as conn:
            # Поиск существующего
            existing = await conn.fetchrow(
                'SELECT id FROM stores WHERE name = $1',
                store_name
            )
            
            if existing:
                return existing['id']
            
            # Создание нового
            type_mapping = {
                'grocery': 'grocery',
                'electronics': 'electronics',
                'clothing': 'clothing',
                'services': 'services',
                'restaurant': 'restaurant',
                'online': 'online',
                'other': 'other'
            }
            
            result = await conn.fetchrow(
                '''INSERT INTO stores (name, store_type, is_active)
                   VALUES ($1, $2, true) RETURNING id''',
                store_name,
                type_mapping.get(store_type, 'other')
            )
            
            return result['id']
    
    async def scrape_website(self, website: Dict[str, str]) -> List[Dict[str, Any]]:
        """Парсинг сайта на наличие скидок"""
        logger.info(f"Парсинг сайта: {website['name']} ({website['url']})")
        discounts = []
        
        try:
            async with self.http_session.get(website['url']) as response:
                if response.status != 200:
                    logger.warning(f"Ошибка доступа к {website['url']}: статус {response.status}")
                    return discounts
                
                html = await response.text()
                
                # Простая эвристика для поиска скидок
                # В реальном проекте здесь будет более сложный парсер
                soup = BeautifulSoup(html, 'lxml')
                
                # Поиск элементов с ценами
                price_patterns = [
                    {'class': 'price'},
                    {'class': 'product-price'},
                    {'class': 'cost'},
                    {'data-price': True},
                ]
                
                for pattern in price_patterns:
                    elements = soup.find_all(**pattern)
                    for elem in elements[:10]:  # Ограничим количество
                        text = elem.get_text(strip=True)
                        if text and any(c.isdigit() for c in text):
                            # Попытка извлечь цену
                            prices = re.findall(r'(\d+(?:[.,]\d+)?)\s*(?:₽|руб|RUB)?', text, re.IGNORECASE)
                            if prices:
                                discounts.append({
                                    'title': f"Акция в {website['name']}",
                                    'description': text[:200],
                                    'discount_type': 'percentage',
                                    'discounted_price': float(prices[0].replace(',', '.')),
                                    'store_name': website['name'],
                                    'store_type': website.get('type', 'other'),
                                    'source_url': website['url'],
                                    'scraped_at': datetime.utcnow()
                                })
                                break  # Один товар на паттерн
                
        except Exception as e:
            logger.error(f"Ошибка парсинга {website['url']}: {e}")
        
        return discounts
    
    async def process_telegram_messages(self):
        """Обработка сообщений из Telegram каналов"""
        if not self.telegram_client:
            return
        
        logger.info("Проверка Telegram каналов...")
        
        try:
            for channel in self.telegram_channels:
                channel = channel.strip()
                if not channel:
                    continue
                    
                try:
                    entity = await self.telegram_client.get_entity(channel)
                    
                    async for message in self.telegram_client.iter_messages(entity, limit=50):
                        if message.id in self.processed_message_ids:
                            continue
                        
                        if not message.text:
                            continue
                        
                        # Поиск скидок в сообщении
                        discount_info = self.parse_telegram_discount(message)
                        if discount_info:
                            # Получаем или создаем магазин
                            store_id = await self.get_or_create_store(
                                f"Telegram: {channel}",
                                'online'
                            )
                            
                            discount_info['store_id'] = store_id
                            discount_info['external_id'] = f"tg_{channel}_{message.id}"
                            
                            await self.save_discount(discount_info)
                            self.processed_message_ids.add(message.id)
                            
                            # Ограничим размер множества
                            if len(self.processed_message_ids) > 10000:
                                self.processed_message_ids = set(
                                    list(self.processed_message_ids)[-5000:]
                                )
                
                except Exception as e:
                    logger.error(f"Ошибка обработки канала {channel}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка при работе с Telegram: {e}")
    
    def parse_telegram_discount(self, message: Message) -> Optional[Dict[str, Any]]:
        """Извлечение информации о скидке из сообщения Telegram"""
        text = message.text.lower()
        
        # Ключевые слова для определения скидок
        discount_keywords = [
            'скидка', 'акция', 'распродажа', 'sale', 'discount',
            '%', 'офф', 'off', 'выгода', 'промокод', 'промо'
        ]
        
        if not any(keyword in text for keyword in discount_keywords):
            return None
        
        # Извлечение промокода
        promo_match = re.search(r'(?:промокод|promo)[:\s]*([A-Z0-9]{4,20})', text, re.IGNORECASE)
        promo_code = promo_match.group(1).upper() if promo_match else None
        
        # Извлечение процента скидки
        percent_match = re.search(r'(\d{1,2})\s*%', text)
        discount_value = float(percent_match.group(1)) if percent_match else None
        
        # Извлечение цены
        price_match = re.search(r'(\d{3,})\s*(?:₽|руб|rub)?', text)
        price = float(price_match.group(1)) if price_match else None
        
        # Определение типа скидки
        discount_type = 'percentage' if discount_value else 'fixed'
        
        # Заголовок - первые 100 символов
        title = message.text.split('\n')[0][:200]
        
        # Дата окончания (если упомянута)
        end_date = None
        date_match = re.search(r'до\s+(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})', text)
        if date_match:
            try:
                date_str = date_match.group(1).replace('-', '.').replace('/', '.')
                if len(date_str.split('.')[-1]) == 2:
                    date_str = date_str[:-2] + '20' + date_str[-2:]
                end_date = datetime.strptime(date_str, '%d.%m.%Y')
            except:
                pass
        
        return {
            'title': title,
            'description': message.text[:500] if message.text else '',
            'discount_type': discount_type,
            'discount_value': discount_value,
            'discounted_price': price,
            'promo_code': promo_code,
            'end_date': end_date,
            'source_url': f'https://t.me/{message.chat.username}/{message.id}' if message.chat.username else None,
            'scraped_at': datetime.utcnow()
        }
    
    async def run_scraping_cycle(self):
        """Запуск полного цикла сбора скидок"""
        logger.info("=== Запуск цикла сбора скидок ===")
        
        # 1. Парсинг веб-сайтов
        for website in self.target_websites:
            discounts = await self.scrape_website(website)
            for discount in discounts:
                store_id = await self.get_or_create_store(
                    discount.pop('store_name'),
                    discount.pop('store_type', 'other')
                )
                discount['store_id'] = store_id
                
                # Генерация external_id
                discount['external_id'] = hashlib.md5(
                    f"{discount['title']}:{discount.get('source_url', '')}".encode()
                ).hexdigest()
                
                await self.save_discount(discount)
        
        # 2. Проверка Telegram каналов
        await self.process_telegram_messages()
        
        logger.info("=== Цикл сбора скидок завершен ===")
    
    async def manual_trigger(self, command: str = 'all'):
        """Ручной запуск сбора по команде"""
        logger.info(f"Ручной запуск: {command}")
        
        if command in ['all', 'web']:
            await self.run_scraping_cycle()
        
        if command in ['all', 'telegram']:
            await self.process_telegram_messages()
    
    def setup_scheduler(self):
        """Настройка расписания задач"""
        # Основной цикл сбора каждые N часов
        self.scheduler.add_job(
            self.run_scraping_cycle,
            IntervalTrigger(hours=self.scrape_interval_hours),
            id='main_scraping_cycle',
            name='Основной цикл сбора скидок',
            replace_existing=True
        )
        
        # Проверка Telegram чаще - каждые 30 минут
        self.scheduler.add_job(
            self.process_telegram_messages,
            IntervalTrigger(minutes=30),
            id='telegram_check',
            name='Проверка Telegram каналов',
            replace_existing=True
        )
        
        # Очистка старых данных каждую ночь в 3:00
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour=3, minute=0),
            id='cleanup_old_data',
            name='Очистка старых данных',
            replace_existing=True
        )
        
        logger.info(f"Планировщик настроен: основной цикл каждые {self.scrape_interval_hours}ч, Telegram каждые 30мин")
    
    async def cleanup_old_data(self):
        """Очистка устаревших скидок"""
        try:
            async with self.db_pool.acquire() as conn:
                # Удаляем скидки, у которых end_date прошел более 30 дней назад
                result = await conn.execute(
                    '''UPDATE discounts SET is_active = false 
                       WHERE end_date < NOW() - INTERVAL '30 days' 
                       AND is_active = true'''
                )
                
                # Удаляем完全不активные записи старше 90 дней
                result = await conn.execute(
                    '''DELETE FROM discounts 
                       WHERE created_at < NOW() - INTERVAL '90 days'
                       AND is_active = false'''
                )
                
                logger.info(f"Очистка старых данных завершена")
                
        except Exception as e:
            logger.error(f"Ошибка при очистке данных: {e}")
    
    async def run(self):
        """Основной цикл работы демона"""
        await self.initialize()
        
        # Настройка обработчиков сигналов
        loop = asyncio.get_event_loop()
        
        def signal_handler(sig):
            logger.info(f"Получен сигнал {sig.name}")
            asyncio.create_task(self.cleanup())
            loop.stop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: signal_handler(s)
            )
        
        # Запуск планировщика
        self.setup_scheduler()
        self.scheduler.start()
        
        # Первоначальный запуск
        logger.info("Первоначальный запуск сбора скидок...")
        await self.run_scraping_cycle()
        
        self.running = True
        logger.info("Демон запущен и работает")
        
        # Основной цикл
        while self.running:
            await asyncio.sleep(1)


def main():
    """Точка входа"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Discount Daemon - сборщик скидок')
    parser.add_argument(
        '--command', '-c',
        choices=['run', 'scrape', 'telegram', 'status'],
        default='run',
        help='Команда для выполнения'
    )
    
    args = parser.parse_args()
    
    daemon = DiscountDaemon()
    
    if args.command == 'status':
        print("Discount Daemon готов к работе")
        print(f"База данных: {os.getenv('DATABASE_URL', 'не настроена')}")
        print(f"Telegram API: {'настроен' if os.getenv('TELEGRAM_API_ID') else 'не настроен'}")
        print(f"Интервал скрапинга: {os.getenv('SCRAPE_INTERVAL', '6')} часов")
        return 0
    
    try:
        if args.command == 'run':
            # Запуск в режиме демона
            asyncio.run(daemon.run())
        elif args.command == 'scrape':
            # Однократный запуск парсинга
            asyncio.run(daemon.initialize())
            asyncio.run(daemon.run_scraping_cycle())
            asyncio.run(daemon.cleanup())
        elif args.command == 'telegram':
            # Однократная проверка Telegram
            asyncio.run(daemon.initialize())
            asyncio.run(daemon.process_telegram_messages())
            asyncio.run(daemon.cleanup())
    except KeyboardInterrupt:
        logger.info("Прервано пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
