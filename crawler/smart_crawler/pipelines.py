import os
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
from smart_crawler.items import ArticleItem

logger = logging.getLogger(__name__)


class DualColumnPipeline:
    """Pipeline to extract raw + clean content"""

    def process_item(self, item, spider):
        if not isinstance(item, ArticleItem):
            return item

        raw_html = item.get("raw_content")
        if not raw_html:
            return item

        try:
            item["clean_content"] = self.clean_html(raw_html)
        except Exception as e:
            logger.error(f"HTML cleaning error: {e}")
            item["clean_content"] = ""

        return item

    def clean_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        for tag in soup.find_all(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(" ", strip=True)
        return " ".join(text.split())


class PostgresPipeline:
    """Store scraped data in PostgreSQL with safe JSON handling"""

    def __init__(self, database_url):
        self.database_url = database_url
        self.connection = None

    @classmethod
    def from_crawler(cls, crawler):
        db_url = os.environ.get(
            "DATABASE_URL", "postgresql://postgres:admin@localhost:5432/intel_db"
        )
        return cls(db_url)

    def open_spider(self, spider):
        self.connection = psycopg2.connect(self.database_url)
        logger.info("Database connection opened")

    def close_spider(self, spider):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def process_item(self, item, spider):
        if not isinstance(item, ArticleItem):
            return item

        cursor = self.connection.cursor()

        url = item.get("url")
        sector = item.get("sector")

        # Convert HTML to JSON-friendly string
        raw_content = json.dumps(item.get("raw_content", ""))

        clean_content = item.get("clean_content", "")

        metadata = {
            "title": item.get("title"),
            "description": item.get("description"),
            "scraped_at": item.get("scraped_at"),
        }
        metadata_json = json.dumps(metadata)

        query = """
            INSERT INTO articles (url, sector, raw_content, clean_content, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url)
            DO UPDATE SET
                raw_content = EXCLUDED.raw_content,
                clean_content = EXCLUDED.clean_content,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id;
        """

        try:
            cursor.execute(
                query, (url, sector, raw_content, clean_content, metadata_json)
            )
            article_id = cursor.fetchone()[0]
            self.connection.commit()
            item["id"] = article_id
            logger.info(f"Stored: {url}")

        except Exception as e:
            self.connection.rollback()
            logger.error(f"DB Insert Error: {e}")
            raise

        finally:
            cursor.close()

        return item
