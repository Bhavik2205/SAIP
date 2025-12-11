

BOT_NAME = "smart_crawler"

SPIDER_MODULES = ["smart_crawler.spiders"]
NEWSPIDER_MODULE = "smart_crawler.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 1
COOKIES_ENABLED = False
DOWNLOAD_TIMEOUT = 120

RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

HTTPERROR_ALLOW_ALL = True

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# KEEP OFFSITE MIDDLEWARE → REQUIRED
# SPIDER_MIDDLEWARES = {
#     'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
# }

# DOWNLOADER_MIDDLEWARES = {
#     "smart_crawler.middlewares.StealthMiddleware": 543,
# }

ITEM_PIPELINES = {
    "smart_crawler.pipelines.DualColumnPipeline": 100,
    "smart_crawler.pipelines.PostgresPipeline": 200,
}

ITEM_PIPELINES = {
    "smart_crawler.pipelines.DualColumnPipeline": 300,
    "smart_crawler.pipelines.PostgresPipeline": 400,
}


OFFSITE_ENABLED = False

LOG_LEVEL = "DEBUG"
DUPEFILTER_DEBUG = True
TELNETCONSOLE_ENABLED = False
