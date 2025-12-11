# Scrapy items for articles

import scrapy


class ArticleItem(scrapy.Item):
    """Item for storing article data with dual-column storage"""
    id = scrapy.Field()
    url = scrapy.Field()                # URL of the article
    sector = scrapy.Field()              # Sector category
    raw_content = scrapy.Field()         # Full HTML (future-proofing)
    clean_content = scrapy.Field()       # Cleaned text (ML analysis)
    metadata = scrapy.Field()            # Additional metadata (JSON)
    title = scrapy.Field()               # Page title
    description = scrapy.Field()         # Meta description
    scraped_at = scrapy.Field()          # Timestamp
