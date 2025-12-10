# Universal Spider - The "Brain" of the crawling system
# Cleaned and hardened for Scrapy-only operation (no Playwright)

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
    - Extracts and scores links, follows high scoring ones
    - Designed to run as a plain Scrapy spider (Playwright disabled)
    """
    name = "universal"

    # Default values (will be overridden in __init__)
    allowed_domains = []
    start_urls = []

    # Scoring constants
    DATE_PATTERN_SCORE = 50
    KEYWORD_IN_TEXT_SCORE = 30
    PDF_XML_HTML_SCORE = 20
    SCORE_THRESHOLD = 40

    # URL patterns for date detection
    DATE_PATTERNS = [
        r"/\d{4}/",                 # /2024/ or /2025/
        r"/\d{4}-\d{2}/",           # /2024-12/
        r"/\d{4}-\d{2}-\d{2}/",     # /2024-12-04/
        r"/releases/",
        r"/news/",
        r"/updates/",
        r"/articles/",
    ]

    # Safety: limit number of links queued per page
    MAX_LINKS_PER_PAGE = 10

    def __init__(self, sector=None, config_path="/app/config.yaml", *args, **kwargs):
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
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
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
        if not self.config or "sectors" not in self.config:
            logger.error("No sectors defined in config")
            return

        sector_config = None
        for sec in self.config["sectors"]:
            if sec.get("name") == self.sector:
                sector_config = sec
                break

        if not sector_config:
            logger.error(f"Sector '{self.sector}' not found in config")
            return

        # Normalize seeds (remove duplicates & strip)
        seeds = sector_config.get("seeds", []) or []
        normalized = []
        seen = set()
        for s in seeds:
            s_stripped = s.strip()
            if s_stripped and s_stripped not in seen:
                normalized.append(s_stripped)
                seen.add(s_stripped)

        self.start_urls = normalized
        self.keywords = [kw.lower() for kw in sector_config.get("keywords", [])]
        # keep domains as provided, but normalize to lower-case
        self.allowed_domains = [d.lower().strip() for d in sector_config.get("allowed_domains", [])]

        logger.info(f"Sector initialized: {self.sector}")
        logger.info(f"Start URLs: {len(self.start_urls)} -> {self.start_urls}")
        logger.info(f"Keywords: {len(self.keywords)} -> {self.keywords}")
        logger.info(f"Allowed domains: {self.allowed_domains}")

    def start_requests(self):
        """Generate initial requests from seed URLs (deduplicated)"""
        if not self.start_urls:
            logger.error("No start URLs found; nothing to crawl.")
            return

        for url in self.start_urls:
            logger.debug(f"Scheduling seed: {url}")
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"score": 100},
                errback=self.errback_play,
            )

    def parse(self, response):
        """
        Main parsing logic (synchronous):
        1. Extract page content & yield ArticleItem
        2. Extract links, score them, queue top-scoring ones
        """
        try:
            raw_content = response.text or ""
        except Exception:
            raw_content = ""

        # Build item
        item = ArticleItem(
            url=response.url,
            sector=self.sector,
            raw_content=raw_content,
            clean_content="",  # pipeline will handle cleaning
            title=response.xpath("//title/text()").get(default="").strip(),
            description=response.xpath("//meta[@name='description']/@content").get(default="").strip(),
            metadata={
                "status_code": getattr(response, "status", None),
                "headers": {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in response.headers.items()},
            },
            scraped_at=datetime.now().isoformat(),
        )
        yield item

        # Extract and score links
        links = self._extract_links(response)
        # Filter by threshold and sort
        scored_links = [(u, s) for (u, s) in links if s > self.SCORE_THRESHOLD]
        if not scored_links:
            logger.debug(f"No high-scoring links found on {response.url}")
            return

        scored_links.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Found {len(scored_links)} high-scoring links on {response.url}")

        # Queue top N links
        queued = 0
        for link_url, score in scored_links:
            if queued >= self.MAX_LINKS_PER_PAGE:
                break
            logger.debug(f"Queueing link (score: {score}): {link_url}")
            queued += 1
            yield scrapy.Request(
                link_url,
                callback=self.parse,
                meta={"score": score},
                errback=self.errback_play,
            )

    def _extract_links(self, response):
        """
        Extract anchor tags and score them.
        Returns list of (absolute_url, score) tuples.
        """
        links = []
        anchors = response.xpath("//a[(@href and string-length(normalize-space(.))>0) or @href]")
        for a in anchors:
            try:
                href = a.xpath("./@href").get()
                if not href:
                    continue
                absolute_url = urljoin(response.url, href)
                parsed = urlparse(absolute_url)
                netloc = (parsed.netloc or "").lower()

                # Domain whitelist check (if provided)
                if self.allowed_domains:
                    domain_match = any(netloc.endswith(domain) for domain in self.allowed_domains)
                    if not domain_match:
                        logger.debug(f"Skipping off-domain link: {absolute_url}")
                        continue

                # Get anchor visible text (string() gives combined text)
                link_text = a.xpath("string(.)").get(default="").strip().lower()

                score = self._score_link(absolute_url, link_text)
                if score > 0:
                    links.append((absolute_url, score))
            except Exception as e:
                logger.debug(f"Error processing anchor: {e}", exc_info=True)
                continue

        # Deduplicate links while keeping highest score
        best = {}
        for u, s in links:
            if u not in best or s > best[u]:
                best[u] = s
        deduped = list(best.items())
        return deduped

    def _score_link(self, url, link_text):
        """
        Score a link based on multiple criteria:
        - +50: URL matches date pattern
        - +30: Link text contains keyword
        - +20: URL ends with .pdf, .xml, .html
        """
        score = 0
        url_lower = (url or "").lower()

        # date patterns
        for pattern in self.DATE_PATTERNS:
            try:
                if re.search(pattern, url_lower):
                    score += self.DATE_PATTERN_SCORE
                    break
            except re.error:
                continue

        # keyword in link text
        for keyword in self.keywords:
            if keyword and keyword in link_text:
                score += self.KEYWORD_IN_TEXT_SCORE
                break

        # document extension
        if url_lower.endswith((".pdf", ".xml", ".html")):
            score += self.PDF_XML_HTML_SCORE

        return score

    def errback_play(self, failure):
        """Handle request errors (generic for HTTP/connection errors)"""
        try:
            req = failure.request
            logger.error(f"Request failed: {getattr(req, 'url', 'unknown')}")
        except Exception:
            logger.error("Request failed (couldn't get request object)")

        try:
            logger.error(f"Failure type: {failure.type}")
            logger.error(f"Failure value: {failure.value}")
            # optionally: logger.exception(failure) to get stack trace
        except Exception:
            pass
