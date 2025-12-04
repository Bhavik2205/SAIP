#!/usr/bin/env python3
"""
Smart Intel Platform - NLP Processor Service

This service:
1. Monitors the articles table for new entries
2. Performs NLP analysis on clean_content
3. Stores analysis results and insights
4. Prepares data for the UI dashboard
"""

import os
import logging
import time
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticleProcessor:
    """Process articles for ML/NLP analysis"""
    
    def __init__(self, database_url):
        self.database_url = database_url
        self.connection = None
        self.processed_count = 0
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("Connected to database")
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from database")
    
    def fetch_unprocessed_articles(self, batch_size=10):
        """Fetch articles that haven't been processed yet"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            # This is a placeholder - you can expand to track processing status
            query = """
                SELECT id, url, sector, clean_content 
                FROM articles 
                WHERE clean_content IS NOT NULL 
                AND clean_content != '' 
                LIMIT %s;
            """
            
            cursor.execute(query, (batch_size,))
            articles = cursor.fetchall()
            cursor.close()
            
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []
    
    def process_article(self, article):
        """
        Process a single article
        Placeholder for NLP/ML analysis
        """
        try:
            article_id = article['id']
            content = article['clean_content']
            
            # Placeholder analysis
            analysis = {
                'word_count': len(content.split()),
                'char_count': len(content),
                'processed_at': datetime.now().isoformat(),
                'status': 'processed'
            }
            
            logger.info(
                f"Processed article {article_id} - "
                f"Words: {analysis['word_count']}, "
                f"Chars: {analysis['char_count']}"
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error processing article {article.get('id')}: {e}")
            return None
    
    def run(self):
        """Main processing loop"""
        logger.info("Starting Article Processor...")
        
        try:
            self.connect()
            
            while True:
                articles = self.fetch_unprocessed_articles(batch_size=10)
                
                if not articles:
                    logger.info("No articles to process. Waiting...")
                    time.sleep(30)
                    continue
                
                for article in articles:
                    analysis = self.process_article(article)
                    if analysis:
                        self.processed_count += 1
                
                logger.info(
                    f"Processed batch of {len(articles)} articles. "
                    f"Total: {self.processed_count}"
                )
                
                time.sleep(10)
        
        except KeyboardInterrupt:
            logger.info("Shutting down processor...")
        except Exception as e:
            logger.error(f"Processor error: {e}")
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    
    database_url = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:admin@localhost:5432/intel_db'
    )
    
    processor = ArticleProcessor(database_url)
    processor.run()


if __name__ == '__main__':
    main()
