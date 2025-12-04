# Scrapy settings for smart_crawler project

BOT_NAME = 'smart_crawler'

SPIDER_MODULES = ['smart_crawler.spiders']
NEWSPIDER_MODULE = 'smart_crawler.spiders'

# Obey robots.txt rules
# Set to False - we handle ethics via logic and rate-limiting
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests per domain
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Async Configuration for Playwright (disabled for Scrapy 2.6.3 compatibility)
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Download Handler for Playwright (disabled - Playwright not installed with Scrapy 2.6.3)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Playwright Settings (disabled for now)
# PLAYWRIGHT_BROWSER_TYPE = "chromium"
# PLAYWRIGHT_LAUNCH_ARGS = {
#     "headless": True,
#     "args": [
#         "--disable-blink-features=AutomationControlled",
#         "--disable-dev-shm-usage",
#     ],
# }

# Politeness & Delays
DOWNLOAD_DELAY = 1  # Base delay between requests
RANDOMIZE_DOWNLOAD_DELAY = True
COOKIES_ENABLED = False

# Disable cookies
COOKIES_DEBUG = False

# User-Agent Rotation (via middleware)
USER_AGENT_ROTATION_ENABLED = True

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Timeout settings
DOWNLOAD_TIMEOUT = 30
DUPEFILTER_DEBUG = False

# Item Pipeline
ITEM_PIPELINES = {
    'smart_crawler.pipelines.DualColumnPipeline': 100,
    'smart_crawler.pipelines.PostgresPipeline': 200,
}

# Middleware
DOWNLOADER_MIDDLEWARES = {
    'smart_crawler.middlewares.StealthMiddleware': 543,
}

# Logging
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_FILE = '/app/logs/crawler.log'

# Memory limits
MEMDEBUG_ENABLED = False
TELNETCONSOLE_ENABLED = False

# DNS cache
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000
