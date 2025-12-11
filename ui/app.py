#!/usr/bin/env python3
"""
Smart Intel Platform - Streamlit Dashboard

Real-time visualization of crawled articles and intelligence insights
"""

import os
import logging
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Smart Intel Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("🔍 Smart Intel Platform")
st.sidebar.markdown("---")

# Database configuration
@st.cache_resource
def get_db_connection():
    """Get cached database connection"""
    try:
        database_url = os.environ.get(
            'DATABASE_URL',
            'postgresql://postgres:admin@localhost:5432/intel_db'
        )
        conn = psycopg2.connect(database_url)
        logger.info("Database connected")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        st.error(f"Database Error: {e}")
        return None


@st.cache_data(ttl=300)
def fetch_articles(limit=100):
    """Fetch recent articles from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT id, url, sector, clean_content, created_at 
            FROM articles 
            ORDER BY created_at DESC 
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        articles = cursor.fetchall()
        cursor.close()
        
        return pd.DataFrame(articles)
    
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_sector_stats():
    """Fetch statistics by sector"""
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT sector, COUNT(*) as count, 
                   MAX(created_at) as last_updated
            FROM articles 
            GROUP BY sector 
            ORDER BY count DESC;
        """
        cursor.execute(query)
        stats = cursor.fetchall()
        cursor.close()
        
        return pd.DataFrame(stats)
    
    except Exception as e:
        logger.error(f"Error fetching sector stats: {e}")
        return pd.DataFrame()


def main():
    """Main dashboard"""
    
    # Header
    st.title("🔍 Smart Intel Platform")
    st.markdown("Real-time intelligence gathering and analysis dashboard")
    st.markdown("---")
    
    # Key metrics
    articles_df = fetch_articles()
    sector_stats = fetch_sector_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Articles",
            value=len(articles_df),
            delta="Last 24h"
        )
    
    with col2:
        st.metric(
            label="Active Sectors",
            value=len(sector_stats) if not sector_stats.empty else 0
        )
    
    with col3:
        if not articles_df.empty:
            latest = articles_df['created_at'].max()
            st.metric(
                label="Last Updated",
                value=latest.strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            st.metric(label="Last Updated", value="N/A")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Articles by Sector")
        if not sector_stats.empty:
            fig = px.bar(
                sector_stats,
                x='sector',
                y='count',
                title="Article Count by Sector",
                labels={'count': 'Count', 'sector': 'Sector'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sector data available")
    
    with col2:
        st.subheader("📈 Articles Over Time")
        if not articles_df.empty:
            articles_df['created_at'] = pd.to_datetime(articles_df['created_at'])
            daily_counts = articles_df.groupby(
                articles_df['created_at'].dt.date
            ).size().reset_index(name='count')
            
            fig = px.line(
                daily_counts,
                x='created_at',
                y='count',
                title="Articles Crawled Over Time",
                labels={'created_at': 'Date', 'count': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No time-series data available")
    
    st.markdown("---")
    
    # Recent articles
    st.subheader("📄 Recent Articles")
    
    if not articles_df.empty:
        # Add search functionality
        search_term = st.text_input("Search articles by URL or sector:")
        
        if search_term:
            filtered_df = articles_df[
                articles_df['url'].str.contains(search_term, case=False) |
                articles_df['sector'].str.contains(search_term, case=False)
            ]
        else:
            filtered_df = articles_df.head(20)
        
        # Display table
        display_df = filtered_df[['url', 'sector', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Article detail view
        st.subheader("📖 Article Details")
        selected_index = st.selectbox(
            "Select an article to view full content:",
            range(len(filtered_df)),
            format_func=lambda i: filtered_df.iloc[i]['url'][:80] + "..."
        )
        
        if selected_index is not None:
            selected_article = filtered_df.iloc[selected_index]
            st.write(f"**URL:** {selected_article['url']}")
            st.write(f"**Sector:** {selected_article['sector']}")
            st.write(f"**Created:** {selected_article['created_at']}")
            st.write("**Content Preview:**")
            content = selected_article['clean_content']
            st.text_area(
                "Article Content",
                value=content[:2000] if content else "No content available",
                height=200,
                disabled=True
            )
    
    else:
        st.info("No articles available yet. Start the crawler to begin collecting data.")
    
    st.markdown("---")
    st.caption("Smart Intel Platform © 2024 | Real-time web intelligence gathering")


if __name__ == '__main__':
    main()
