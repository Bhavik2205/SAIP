import re
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
import yaml
import scrapy
from smart_crawler.items import ArticleItem

logger = logging.getLogger(__name__)


class UniversalSpider(scrapy.Spider):
    name = "universal"

    allowed_domains = []
    start_urls = []

    DATE_PATTERN_SCORE = 50
    KEYWORD_IN_TEXT_SCORE = 30
    PDF_XML_HTML_SCORE = 20
    SCORE_THRESHOLD = 40

    DATE_PATTERNS = [
        r"/\d{4}/",
        r"/\d{4}-\d{2}/",
        r"/\d{4}-\d{2}-\d{2}/",
        r"/releases/",
        r"/news/",
        r"/updates/",
        r"/articles/",
    ]

    MAX_LINKS_PER_PAGE = 10

    def __init__(self, sector=None, query=None, config_path="../config.yaml", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sector = sector
        self.query = query
        self.config_path = config_path
        self.config = self._load_config()

        self.keywords = []
        self.allowed_domains = []
        self.is_dynamic_mode = False

        # Detect dynamic mode
        if self.sector == "Dynamic_Search" and self.query:
            self._init_dynamic_search()
        else:
            self._initialize_sector_config()

    # ---------------- LOAD CONFIG ----------------
    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Config load error: {e}")
            return {}

    # ---------------- NORMAL MODE ----------------
    def _initialize_sector_config(self):
        if not self.config or "sectors" not in self.config:
            logger.error("No sectors defined in config.yaml")
            return

        sector_config = next((s for s in self.config["sectors"] if s.get("name") == self.sector), None)

        if not sector_config:
            logger.error(f"Sector '{self.sector}' not found in config")
            return

        self.start_urls = list(dict.fromkeys([s.strip() for s in sector_config.get("seeds", [])]))
        self.keywords = [kw.lower() for kw in sector_config.get("keywords", [])]
        self.allowed_domains = [d.lower().strip() for d in sector_config.get("allowed_domains", [])]

        logger.info(f"[NORMAL MODE] Sector initialized: {self.sector}")
        logger.info(f"Start URLs: {self.start_urls}")
        logger.info(f"Keywords: {self.keywords}")
        logger.info(f"Allowed domains: {self.allowed_domains}")

    # ---------------- DYNAMIC SEARCH MODE ----------------
    def _init_dynamic_search(self):
        self.is_dynamic_mode = True
        query_encoded = self.query.replace(" ", "+")

        self.start_urls = [
            f"https://www.google.com/search?q={query_encoded}",
            f"https://www.bing.com/search?q={query_encoded}",
            f"https://duckduckgo.com/html/?q={query_encoded}"
        ]

        self.keywords = self.query.lower().split()
        self.allowed_domains = []  # allow everything

        logger.info(f"[DYNAMIC MODE ENABLED]")
        logger.info(f"Search Query: {self.query}")
        logger.info(f"Start URLs: {self.start_urls}")
        logger.info(f"Keywords: {self.keywords}")

    # ---------------- START REQUESTS ----------------
    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        }

        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers=headers, dont_filter=True)

    # ---------------- MAIN PARSE ----------------
    def parse(self, response):

        if self.is_dynamic_mode:
            yield from self._parse_search_results(response)

        # Store raw page
        item = ArticleItem(
            url=response.url,
            sector=self.sector,
            raw_content=response.text,
            clean_content="",
            title=response.xpath("//title/text()").get(default="").strip(),
            description=response.xpath("//meta[@name='description']/@content").get(default="").strip(),
            scraped_at=datetime.now().isoformat(),
            metadata={}
        )
        yield item

        # Follow scored links
        links = self._extract_links(response)
        scored_links = [(u, s) for (u, s) in links if s >= self.SCORE_THRESHOLD]

        for link, score in sorted(scored_links, key=lambda x: x[1], reverse=True)[:self.MAX_LINKS_PER_PAGE]:
            yield scrapy.Request(link, callback=self.parse, dont_filter=True)

    # ---------------- PARSE SEARCH ENGINES ----------------
    def _parse_search_results(self, response):

        # GOOGLE
        if "google." in response.url:
            for href in response.xpath("//a/@href").getall():
                if "/url?q=" in href:
                    real = href.split("/url?q=")[1].split("&")[0]
                    if real.startswith("/"):
                        real = "https://www.google.com" + real
                    yield scrapy.Request(real, callback=self.parse, dont_filter=True)

        # BING
        # if "bing.com" in response.url:
        #     for href in response.xpath("//li[@class='b_algo']//a/@href").getall():
        #         yield scrapy.Request(href, callback=self.parse, dont_filter=True)

        # # DUCKDUCKGO FIXED
        # if "duckduckgo.com" in response.url:

        #     for href in response.xpath("//a/@href").getall():

        #         # FIX 1: starts with //
        #         if href.startswith("//"):
        #             href = "https:" + href

        #         # FIX 2: /l/?uddg=...
        #         if href.startswith("/") and not href.startswith("http"):
        #             href = "https://duckduckgo.com" + href

        #         if "javascript:" in href:
        #             continue

        #         yield scrapy.Request(href, callback=self.parse, dont_filter=True)

    # ---------------- NORMAL LINK EXTRACTION ----------------
    def _extract_links(self, response):
        links = []
        anchors = response.xpath("//a[@href]")

        for a in anchors:
            href = a.xpath("./@href").get()
            if not href:
                continue

            absolute_url = urljoin(response.url, href)
            domain = urlparse(absolute_url).netloc.lower()

            # allowed_domains only in normal mode
            if not self.is_dynamic_mode and self.allowed_domains:
                if not any(domain.endswith(d) for d in self.allowed_domains):
                    continue

            text = a.xpath("string(.)").get(default="").strip().lower()
            score = self._score_link(absolute_url, text)

            if score > 0:
                links.append((absolute_url, score))

        best = {}
        for u, s in links:
            if u not in best or s > best[u]:
                best[u] = s

        return list(best.items())

    # ---------------- SCORING ----------------
    def _score_link(self, url, text):
        score = 0
        url_lower = url.lower()

        for pattern in self.DATE_PATTERNS:
            if re.search(pattern, url_lower):
                score += self.DATE_PATTERN_SCORE
                break

        for kw in self.keywords:
            if kw in text:
                score += self.KEYWORD_IN_TEXT_SCORE
                break

        if url_lower.endswith((".pdf", ".xml", ".html")):
            score += self.PDF_XML_HTML_SCORE

        return score
