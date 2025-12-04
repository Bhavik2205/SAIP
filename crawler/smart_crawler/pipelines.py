# Data pipelines for cleaning and storing articles

import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
from smart_crawler.items import ArticleItem

logger = logging.getLogger(__name__)


class DualColumnPipeline:
    """Pipeline to implement dual-column storage strategy"""
    
    def process_item(self, item, spider):
        """
        Process item:
        1. Capture raw HTML
        2. Clean content using BeautifulSoup
        3. Pass to next pipeline
        """
        
        if not isinstance(item, ArticleItem):
            return item
        
        # Ensure raw_content exists
        if 'raw_content' not in item or not item['raw_content']:
            logger.warning(f"No raw_content for {item.get('url', 'unknown')}")
            return item
        
        # Extract and clean content
        try:
            clean_text = self._clean_html(item['raw_content'])
            item['clean_content'] = clean_text
        except Exception as e:
            logger.error(f"Error cleaning content from {item.get('url')}: {e}")
            item['clean_content'] = ""
        
        return item
    
    @staticmethod
    def _clean_html(raw_html):
        """
        Clean HTML content:
        - Remove script, style, and navigation tags
        - Extract text content
        - Normalize whitespace
        """
        try:
            soup = BeautifulSoup(raw_html, 'lxml')
            
            # Remove unwanted tags
            for tag in soup.find_all(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            
            # Normalize whitespace
            text = ' '.join(text.split())
            
            return text
        
        except Exception as e:
            logger.error(f"BeautifulSoup parsing error: {e}")
            return raw_html


class PostgresPipeline:
    """Pipeline to store items in PostgreSQL with upsert logic"""
    
    def __init__(self, database_url):
        self.database_url = database_url
        self.connection = None
    
    @classmethod
    def from_crawler(cls, crawler):
        database_url = os.environ.get(
            'DATABASE_URL',
            'postgresql://postgres:admin@localhost:5432/intel_db'
        )
        return cls(database_url)
    
    def open_spider(self, spider):
        """Open database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("Database connection opened")
        except psycopg2.OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close_spider(self, spider):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def process_item(self, item, spider):
        """
        Insert or update item in PostgreSQL
        Upsert on url to prevent duplicates
        """
        
        if not isinstance(item, ArticleItem):
            return item
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare values
            url = item.get('url')
            sector = item.get('sector')
            raw_content = item.get('raw_content', '')
            clean_content = item.get('clean_content', '')
            metadata = {
                'title': item.get('title'),
                'description': item.get('description'),
                'scraped_at': item.get('scraped_at'),
            }
            
            # PostgreSQL UPSERT (INSERT ... ON CONFLICT)
            insert_query = """
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
            
            cursor.execute(
                insert_query,
                (url, sector, raw_content, clean_content, str(metadata))
            )
            
            article_id = cursor.fetchone()[0]
            self.connection.commit()
            
            logger.info(f"Article stored: {url} (ID: {article_id})")
            item['id'] = article_id
            
        except psycopg2.IntegrityError as e:
            self.connection.rollback()
            logger.warning(f"Integrity error for {url}: {e}")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error storing item {url}: {e}")
            raise
        finally:
            cursor.close()
        
        return item
