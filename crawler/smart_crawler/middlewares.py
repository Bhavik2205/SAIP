# Scrapy middlewares for stealth and identity rotation

import random
from scrapy import signals
from scrapy.exceptions import IgnoreRequest


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
]

ACCEPT_HEADERS = [
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
]

ACCEPT_LANGUAGE_HEADERS = [
    'en-US,en;q=0.9',
    'en-US,en;q=0.9,es;q=0.8',
    'en-US,en;q=0.9,fr;q=0.8',
]


class StealthMiddleware:
    """Middleware to randomize user identities and bypass anti-bot protections"""
    
    def __init__(self, crawler):
        self.crawler = crawler
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def spider_opened(self, spider):
        spider.logger.info('StealthMiddleware spider opened')
    
    def process_request(self, request, spider):
        """Inject randomized headers to evade detection"""
        
        # Randomize User-Agent
        request.headers['User-Agent'] = random.choice(USER_AGENTS)
        
        # Randomize Accept header
        request.headers['Accept'] = random.choice(ACCEPT_HEADERS)
        
        # Randomize Accept-Language
        request.headers['Accept-Language'] = random.choice(ACCEPT_LANGUAGE_HEADERS)
        
        # Common browser headers
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['DNT'] = '1'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Upgrade-Insecure-Requests'] = '1'
        request.headers['Sec-Fetch-Dest'] = 'document'
        request.headers['Sec-Fetch-Mode'] = 'navigate'
        request.headers['Sec-Fetch-Site'] = 'none'
        request.headers['Cache-Control'] = 'max-age=0'
        
        # Add randomized referer occasionally
        if random.random() > 0.3:
            request.headers['Referer'] = 'https://www.google.com/'
        
        return request
    
    def process_exception(self, request, exception, spider):
        """Handle exceptions"""
        spider.logger.error(f'Exception from {request.url}: {exception}')
        pass
