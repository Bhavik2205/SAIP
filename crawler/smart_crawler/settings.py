BOT_NAME = 'smart_crawler'

SPIDER_MODULES = ['smart_crawler.spiders']
NEWSPIDER_MODULE = 'smart_crawler.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 30

COOKIES_ENABLED = False

RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# ❌ Playwright disabled
# DOWNLOAD_HANDLERS = {}
# DOWNLOADER_MIDDLEWARES = {
#     'smart_crawler.middlewares.StealthMiddleware': 543,
# }
TWISTED_REACTOR = "twisted.internet.selectreactor.SelectReactor"


ITEM_PIPELINES = {
    'smart_crawler.pipelines.DualColumnPipeline': 100,
    'smart_crawler.pipelines.PostgresPipeline': 200,
}

LOG_LEVEL = 'DEBUG'
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000
