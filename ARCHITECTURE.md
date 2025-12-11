# Smart Intel Platform (SAIP) - Architecture & Implementation Guide

## 🏗️ Project Overview

The **Smart Intel Platform** is a sector-agnostic, intelligent web crawling and data processing system designed to bypass anti-bot protections (Cloudflare, etc.) and extract structured intelligence. The platform is built with **Docker Compose** for cross-platform deployment (Windows AMD64 & Mac ARM64).

---

## 📁 Project Structure

```
smart-intel-platform/
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── config.yaml                 # 🎯 External configuration (seeds, keywords, sectors)
├── docker-compose.yml          # 🐳 Orchestration file
├── start.sh / start.bat        # Quick-start scripts
├── dev-setup.sh                # Local development setup
├── README.md                   # User documentation
├── ARCHITECTURE.md             # This file
│
├── data/                       # 📦 Volume mount for persistence
│   └── db/                     # PostgreSQL data directory
│
├── crawler/                    # 🕷️ SERVICE 1: Web Scraper (Scrapy + Playwright)
│   ├── Dockerfile              # Multi-platform Docker image
│   ├── requirements.txt        # Python dependencies
│   ├── scrapy.cfg              # Scrapy configuration
│   ├── init_db.sql             # Database initialization
│   └── smart_crawler/
│       ├── __init__.py
│       ├── settings.py         # ⚙️ Scrapy & Playwright settings
│       ├── items.py            # Data models (ArticleItem)
│       ├── middlewares.py      # 🎭 Stealth middleware (User-Agent rotation)
│       ├── pipelines.py        # 🧹 Data cleaning & DB storage
│       └── spiders/
│           ├── __init__.py
│           └── universal_spider.py  # 🧠 The Brain (intelligent link ranking)
│
├── processor/                  # 🤖 SERVICE 2: NLP & ML Processing
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py                 # Article processing service
│
└── ui/                         # 📊 SERVICE 3: Streamlit Dashboard
    ├── Dockerfile
    ├── requirements.txt
    └── app.py                  # Interactive analytics dashboard
```

---

## 🔑 Key Features

### 1. **Sector-Agnostic Configuration**
- External `config.yaml` defines crawling targets
- Add new sectors without code changes
- Specify seeds (starting URLs), keywords, and allowed domains

**Example Configuration:**
```yaml
sectors:
  - name: "Energy_Venezuela"
    seeds:
      - "https://ofac.treasury.gov/..."
    keywords: ["sanctions", "Exxon", "PdVSA"]
    allowed_domains: ["treasury.gov", "sec.gov"]
```

### 2. **Stealth Crawling & Anti-Bot Bypass**
- **Playwright Integration**: Executes JavaScript to bypass static analysis
- **User-Agent Rotation**: Randomizes browser identities across requests
- **Header Spoofing**: Mimics legitimate browser traffic
- **Rate Limiting**: Configurable delays between requests (default: 5 sec)
- **Cookie Handling**: Disabled to avoid tracking

**Implementation:** `crawler/smart_crawler/middlewares.py` - `StealthMiddleware`

### 3. **Dual-Column Storage Strategy**
The platform stores two versions of content for different use cases:

| Column | Content | Use Case |
|--------|---------|----------|
| `raw_content` | Full HTML | Future-proofing, advanced parsing |
| `clean_content` | Extracted text | Immediate ML/NLP analysis |

**Cleaning Process:**
- Remove `<script>`, `<style>`, `<nav>`, `<footer>` tags
- Extract pure text content
- Normalize whitespace

**Implementation:** `crawler/smart_crawler/pipelines.py` - `DualColumnPipeline`

### 4. **Intelligent Link Ranking (The "Brain")**
The crawler scores links before visiting to maximize efficiency:

```
Link Scoring:
  +50 points → URL contains date pattern (/2025/, /releases/, etc.)
  +30 points → Link text contains sector keyword
  +20 points → URL ends in .pdf, .xml, or .html
  ────────────────────────────────────────
  Queue if score > 40
```

**Example Scoring:**
- URL: `/articles/2025/sanctions-update.pdf`
  - Date pattern: +50
  - Keyword "sanctions": +30
  - PDF extension: +20
  - **Total: 100** ✅ Queue

**Implementation:** `crawler/smart_crawler/spiders/universal_spider.py` - `_score_link()`

---

## 🐳 Docker Architecture

### Services Orchestration

```
┌─────────────────────────────────────────────────┐
│            Docker Network: intel-network         │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Crawler    │  │Database  │  │Processor │  │
│  │  (Scrapy)    │→→│(PostgreSQL)│→│(NLP/ML)  │  │
│  └──────────────┘  └──────────┘  └──────────┘  │
│         ↓                            ↓           │
│   Mount config.yaml             Monitor &       │
│   (read-only)                   Analyze         │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │           Streamlit UI Dashboard         │  │
│  │         (localhost:8501)                 │  │
│  └──────────────────────────────────────────┘  │
│         Visualize & Query Articles             │
└─────────────────────────────────────────────────┘
```

### Service Details

#### 🕷️ **Crawler Service**
- **Base Image:** `mcr.microsoft.com/playwright/python:v1.40.0-jammy`
- **Ports:** Internal only (no exposed ports)
- **Dependencies:** Waits for PostgreSQL to be healthy
- **Volumes:**
  - `./config.yaml:/app/config.yaml:ro` (read-only config)
  - `./crawler/logs:/app/logs` (persistent logs)
- **Command:** `scrapy crawl universal -a sector=Energy_Venezuela`

#### 💾 **Database Service**
- **Image:** `postgres:16-alpine`
- **Port:** `5432:5432`
- **Volumes:** `./data/db:/var/lib/postgresql/data` (persistent)
- **Init Script:** `init_db.sql` creates `articles` table

#### 🤖 **Processor Service**
- **Base Image:** `python:3.11-slim`
- **Role:** Monitors new articles and performs NLP analysis
- **Trigger:** Runs continuously, checking DB every 10 seconds

#### 📊 **UI Service**
- **Framework:** Streamlit
- **Port:** `8501:8501`
- **Features:**
  - Real-time article metrics
  - Sector statistics charts
  - Article search & filtering
  - Content preview

---

## 🗄️ Database Schema

### `articles` Table

```sql
CREATE TABLE articles (
    id                SERIAL PRIMARY KEY,
    url               VARCHAR(2048) UNIQUE NOT NULL,
    sector            VARCHAR(255) NOT NULL,
    raw_content       TEXT,                       -- Full HTML
    clean_content     TEXT,                       -- Extracted text
    metadata          JSONB DEFAULT '{}',         -- Additional data
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_articles_sector ON articles(sector);
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_created_at ON articles(created_at);
```

### Upsert Logic
The pipeline uses PostgreSQL's `ON CONFLICT` clause to prevent duplicates:

```sql
INSERT INTO articles (url, sector, raw_content, clean_content, metadata)
VALUES (...)
ON CONFLICT (url) 
DO UPDATE SET
    raw_content = EXCLUDED.raw_content,
    clean_content = EXCLUDED.clean_content,
    metadata = EXCLUDED.metadata,
    updated_at = CURRENT_TIMESTAMP;
```

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- 4GB+ RAM available

### Quick Start

**Windows:**
```bash
start.bat
```

**macOS/Linux:**
```bash
bash start.sh
```

**Manual:**
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f crawler
```

### Access Services

| Service | URL/Connection |
|---------|---|
| Database | `localhost:5432` |
| UI Dashboard | `http://localhost:8501` |
| Crawler Logs | `docker-compose logs crawler` |

---

## ⚙️ Configuration Guide

### Edit `config.yaml`

```yaml
sectors:
  - name: "Energy_Venezuela"                    # Sector identifier
    seeds:                                       # Starting URLs
      - "https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions"
      - "https://www.sec.gov/edgar/search-filings"
    keywords:                                    # Terms for link scoring
      - "sanctions"
      - "license"
      - "arbitration"
    allowed_domains:                             # Whitelist domains
      - "treasury.gov"
      - "sec.gov"

crawler_settings:
  download_delay: 5          # Base delay (seconds)
  random_delay: 5            # Random jitter
  concurrent_requests: 4     # Parallel requests
  timeout: 30                # Request timeout
```

### Add New Sector

```yaml
  - name: "Finance_APAC"
    seeds:
      - "https://example.com/finance"
    keywords: ["interest", "bonds", "currency"]
    allowed_domains: ["example.com"]
```

Then start crawling:
```bash
docker-compose exec crawler scrapy crawl universal -a sector=Finance_APAC
```

---

## 🧠 Spider Logic (The Brain)

### Execution Flow

```
1. Load config.yaml
   ↓
2. Initialize sector configuration
   ↓
3. For each seed URL:
   ├─ Make Playwright request (JS execution)
   ├─ Extract all links from page
   ├─ Score each link:
   │  ├─ Check for date patterns (+50)
   │  ├─ Check for keywords in text (+30)
   │  └─ Check for document extensions (+20)
   ├─ Filter links with score > 40
   ├─ Queue top 10 links for crawling
   └─ Yield article item
   ↓
4. Pipeline processes items:
   ├─ Extract raw HTML
   ├─ Clean content with BeautifulSoup
   └─ Upsert to PostgreSQL
```

### Key Methods

**`_extract_links(response)`**
- Finds all `<a>` tags
- Filters by allowed domains
- Returns (url, score) tuples

**`_score_link(url, link_text)`**
- Scores based on URL patterns and link text
- Returns integer score

**`_load_config()`**
- Reads YAML configuration
- Handles missing files gracefully

---

## 🔒 Security & Ethics

### Implemented Safeguards
1. **Rate Limiting:** 5-second delays between requests
2. **Robots.txt:** Disabled with manual rate-limiting
3. **User-Agent Rotation:** Avoids fingerprinting
4. **Timeout Protection:** 30-second request timeout
5. **Retry Logic:** 3 retries for failed requests

### Best Practices
- Always specify `allowed_domains` to prevent crawling unintended sites
- Use appropriate `download_delay` for target websites
- Monitor crawler logs for 429 (rate limit) errors
- Respect `X-Robots-Tag` headers in responses

---

## 📊 Monitoring & Debugging

### Crawler Logs
```bash
docker-compose logs -f crawler
```

### Database Queries
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U intel_user -d intel_db

# Check article count
SELECT COUNT(*) FROM articles;

# Check by sector
SELECT sector, COUNT(*) FROM articles GROUP BY sector;

# Find errors
SELECT * FROM articles WHERE clean_content IS NULL;
```

### Service Health
```bash
docker-compose ps
docker-compose logs -f [service-name]
```

---

## 🔧 Development & Customization

### Local Crawler Testing
```bash
cd crawler
pip install -r requirements.txt
scrapy crawl universal -a sector=Energy_Venezuela
```

### Add Custom Middleware
Edit `crawler/smart_crawler/middlewares.py` to add proxy support, custom headers, etc.

### Extend Link Scoring
Modify `_score_link()` in `universal_spider.py` to adjust scoring algorithm.

### Custom Content Cleaning
Edit `_clean_html()` in `pipelines.py` to implement domain-specific cleaning rules.

---

## 📦 Deployment Notes

### Cross-Platform Compatibility
- ✅ Windows (AMD64) - Docker Desktop
- ✅ macOS (Intel & Apple Silicon) - Docker Desktop
- ✅ Linux (AMD64/ARM64) - Docker Engine

### Resource Requirements
- **Minimum:** 4GB RAM, 2 CPU cores, 10GB disk
- **Recommended:** 8GB RAM, 4 CPU cores, 50GB disk

### Performance Tuning
```yaml
# In docker-compose.yml, adjust:
CONCURRENT_REQUESTS: 8        # Increase for faster crawling
DOWNLOAD_DELAY: 2             # Decrease for faster, riskier crawling
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Database connection refused" | Ensure PostgreSQL started: `docker-compose logs db` |
| "Playwright not found" | Rebuild with: `docker-compose build --no-cache crawler` |
| "Port 5432 already in use" | Change port in `docker-compose.yml`: `"5433:5432"` |
| "Config not loading" | Mount: `./config.yaml:/app/config.yaml:ro` |
| "403/429 errors" | Reduce concurrent requests & increase delays |

---

## 📚 References

- **Scrapy Documentation:** https://docs.scrapy.org/
- **Playwright Python:** https://playwright.dev/python/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Streamlit:** https://docs.streamlit.io/
- **Docker Compose:** https://docs.docker.com/compose/

---

## 📝 License

See `LICENSE` file for details.

---

**Smart Intel Platform © 2024 | Cross-platform, ethical web intelligence gathering**
