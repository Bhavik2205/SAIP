# Universal Spider - The "Brain" of the crawling system

import re
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import yaml
import scrapy
from smart_crawler.items import ArticleItem

logger = logging.getLogger(__name__)


class UniversalSpider(scrapy.Spider):
    """
    Universal Spider with intelligent link ranking ("The Brain")
    - Loads configuration from config.yaml
    - Uses Playwright to bypass JS challenges
    - Implements smart link scoring
    - Extracts and prioritizes links intelligently
    """
    
    name = 'universal'
    allowed_domains = []
    start_urls = []
    
    # Scoring constants
    DATE_PATTERN_SCORE = 50
    KEYWORD_IN_TEXT_SCORE = 30
    PDF_XML_HTML_SCORE = 20
    SCORE_THRESHOLD = 40
    
    # URL patterns for date detection
    DATE_PATTERNS = [
        r'/\d{4}/',          # /2024/ or /2025/
        r'/\d{4}-\d{2}/',    # /2024-12/
        r'/\d{4}-\d{2}-\d{2}/',  # /2024-12-04/
        r'/releases/',
        r'/news/',
        r'/updates/',
        r'/articles/',
    ]
    
    def __init__(self, sector=None, config_path='/app/config.yaml', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sector = sector
        self.config_path = config_path
        self.config = self._load_config()
        self.keywords = []
        self.allowed_domains = []
        self._initialize_sector_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config YAML: {e}")
            return {}
    
    def _initialize_sector_config(self):
        """Initialize spider configuration for specified sector"""
        
        if not self.config or 'sectors' not in self.config:
            logger.error("No sectors defined in config")
            return
        
        # Find matching sector
        sector_config = None
        for sec in self.config['sectors']:
            if sec['name'] == self.sector:
                sector_config = sec
                break
        
        if not sector_config:
            logger.error(f"Sector '{self.sector}' not found in config")
            return
        
        # Set up sector configuration
        self.start_urls = sector_config.get('seeds', [])
        self.keywords = [kw.lower() for kw in sector_config.get('keywords', [])]
        self.allowed_domains = sector_config.get('allowed_domains', [])
        
        logger.info(f"Sector initialized: {self.sector}")
        logger.info(f"Start URLs: {len(self.start_urls)}")
        logger.info(f"Keywords: {len(self.keywords)}")
        logger.info(f"Allowed domains: {self.allowed_domains}")
    
    def start_requests(self):
        """Generate initial requests from seed URLs"""
        
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                # Playwright disabled for Scrapy 2.6.3 compatibility
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'score': 100, # Initial score, as per your scoring logic
                },
                errback=self.errback_play,
            )
    
    async def parse(self, response):
        """
        Main parsing logic:
        1. Extract page content
        2. Find all links
        3. Score links intelligently
        4. Queue high-scoring links
        5. Yield article item
        """
        
        # Extract and store raw content
        raw_content = response.text
        
        # Yield article item
        item = ArticleItem(
            url=response.url,
            sector=self.sector,
            raw_content=raw_content,
            clean_content='',  # Will be set by pipeline
            title=response.xpath('//title/text()').get(''),
            description=response.xpath('//meta[@name="description"]/@content').get(''),
            metadata={
                'status_code': response.status,
                'headers': dict(response.headers),
            },
            scraped_at=datetime.now().isoformat(),
        )
        yield item
        
        # Extract and score links
        links = self._extract_links(response)
        scored_links = [
            (link, score)
            for link, score in links
            if score > self.SCORE_THRESHOLD
        ]
        
        # Sort by score descending
        scored_links.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(scored_links)} high-scoring links on {response.url}")
        
        # Queue high-scoring links
        for link_url, score in scored_links[:10]:  # Limit to top 10 per page
            logger.debug(f"Queueing link (score: {score}): {link_url}")
            
            yield scrapy.Request(
                link_url,
                callback=self.parse,
                # Playwright disabled for Scrapy 2.6.3 compatibility
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'score': score,
                },
                errback=self.errback_play,
            )
    
    def _extract_links(self, response):
        """
        Extract all links from page and score them
        Returns list of (url, score) tuples
        """
        links = []
        
        for href in response.xpath('//a/@href').getall():
            try:
                # Normalize URL
                absolute_url = urljoin(response.url, href)
                parsed = urlparse(absolute_url)
                
                # Check domain whitelist
                if self.allowed_domains:
                    domain_match = any(
                        parsed.netloc.endswith(domain)
                        for domain in self.allowed_domains
                    )
                    if not domain_match:
                        continue
                
                # Get link text
                link_text = response.xpath(
                    f'//a[@href="{href}"]/text()'
                ).get('').lower()
                
                # Score the link
                score = self._score_link(absolute_url, link_text)
                
                if score > 0:
                    links.append((absolute_url, score))
            
            except Exception as e:
                logger.debug(f"Error processing link {href}: {e}")
                continue
        
        return links
    
    def _score_link(self, url, link_text):
        """
        Score a link based on multiple criteria
        
        Scoring:
        - +50: URL matches date pattern
        - +30: Link text contains keyword
        - +20: URL ends with .pdf, .xml, .html
        """
        score = 0
        url_lower = url.lower()
        
        # Check for date patterns
        for pattern in self.DATE_PATTERNS:
            if re.search(pattern, url_lower):
                score += self.DATE_PATTERN_SCORE
                break
        
        # Check for keywords in link text
        for keyword in self.keywords:
            if keyword in link_text:
                score += self.KEYWORD_IN_TEXT_SCORE
                break
        
        # Check for document extensions
        if url_lower.endswith(('.pdf', '.xml', '.html')):
            score += self.PDF_XML_HTML_SCORE
        
        return score
    
    def errback_play(self, failure):
        """Handle Playwright request errors"""
        logger.error(f"Error in request: {failure.request.url}")
        logger.error(f"Error type: {failure.type}")
        logger.error(f"Error value: {failure.value}")
