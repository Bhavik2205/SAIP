#!/usr/bin/env python
"""
Custom crawler runner that uses CrawlerRunner instead of CrawlerProcess
to avoid signal handler incompatibilities with Twisted in containerized environments.
"""
import sys
import os
from pathlib import Path

# Add the smart_crawler package to Python path
sys.path.insert(0, str(Path(__file__).parent))

# from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.reactor import install_reactor
from smart_crawler.spiders.universal_spider import UniversalSpider

# Configure logging
configure_logging({'LOG_LEVEL': 'DEBUG'})

def find_config_path():
    """Find config.yaml in multiple possible locations"""
    possible_paths = [
        '/app/config.yaml',
        './config.yaml',
        '../config.yaml',
        '/workspace/config.yaml',
    ]
    for path in possible_paths:
        if Path(path).exists():
            print(f"[+] Found config at: {path}")
            return path
    print(f"[!] Config not found. Searched: {possible_paths}")
    print(f"[!] Spider will attempt to load from: /app/config.yaml (may fail gracefully)")
    return '/app/config.yaml'

def main(sector='Energy_Venezuela'):
    """Run the crawler using CrawlerRunner (avoids signal handler issues)."""
    config_path = find_config_path()
    
    settings_dict = {
        'BOT_NAME': 'smart_crawler',
        'SPIDER_MODULES': ['smart_crawler.spiders'],
        'NEWSPIDER_MODULE': 'smart_crawler.spiders',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },  
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408],
        'DOWNLOAD_TIMEOUT': 30,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
        'ITEM_PIPELINES': {
            'smart_crawler.pipelines.DualColumnPipeline': 100,
            'smart_crawler.pipelines.PostgresPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'smart_crawler.middlewares.StealthMiddleware': 543, # Assuming this is your middleware
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Playwright must be active here, typically with a high priority
            'scrapy_playwright.middlewares.ScrapyPlaywrightProxyMiddleware': 750, 
        },
        'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    }
    
    # 1. Install the requested reactor (AsyncioSelectorReactor)
    install_reactor(settings_dict['TWISTED_REACTOR']) 
    
    # 2. Import the now-correctly-configured reactor
    from twisted.internet import reactor 
    
    # 3. Create runner
    print("[*] Using CrawlerRunner (signal-handler safe)")
    # Create runner without signal handlers
    runner = CrawlerRunner(settings_dict)
    
    # Schedule the spider with config path
    d = runner.crawl(UniversalSpider, sector=sector, config_path=config_path)
    
    # Fire up the reactor
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

if __name__ == '__main__':
    sector = sys.argv[1] if len(sys.argv) > 1 else 'Energy_Venezuela'
    print(f"[*] Starting Smart Crawler for sector: {sector}")
    # print(f"[*] Using CrawlerRunner (signal-handler safe)")
    print(f"[*] Python: {sys.version.split()[0]}")
    main(sector)
