# 🚀 Running Smart Intel Platform - Setup Guide

## Current Status

⚠️ **Docker Daemon Not Running**

Your system doesn't currently have Docker running. Here are your options:

---

## Option 1: Start Docker Desktop (Recommended for Windows)

### Windows Users:
1. **Open Docker Desktop Application**
   - Search "Docker Desktop" in Windows Start menu
   - Click to launch

2. **Wait for Docker to Initialize**
   - Wait ~30 seconds for initialization
   - Should see Docker icon in system tray

3. **Run the Platform**
   ```bash
   cd c:/Users/BAPS/Desktop/SAIP
   docker-compose up --build -d
   ```

4. **Monitor Progress**
   ```bash
   docker-compose ps
   docker-compose logs -f crawler
   ```

---

## Option 2: Test Crawler Locally (No Docker Required)

If you don't want to use Docker, you can test the crawler locally:

### Step 1: Setup Python Environment
```bash
cd c:/Users/BAPS/Desktop/SAIP
bash dev-setup.sh
# Activate the virtual environment (platform-specific):
# On macOS / Linux:
source venv/bin/activate
# On Windows (Git Bash):
# source venv/Scripts/activate
# On Windows PowerShell:
# .\venv\Scripts\Activate.ps1
```

### Step 2: Run Local Crawler (without Playwright JS support)
```bash
cd crawler
scrapy crawl universal -a sector=Energy_Venezuela -L INFO
```

### Step 3: Output Goes to Console
You'll see crawled articles printed to terminal.

---

## Option 3: Run Database Locally (SQLite)

If you want data persistence without PostgreSQL:

### Modify `crawler/smart_crawler/pipelines.py`:
Replace PostgreSQL pipeline with SQLite:

```python
import sqlite3

class SQLitePipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect('/tmp/articles.db')
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                sector TEXT,
                raw_content TEXT,
                clean_content TEXT
            )
        ''')
        self.connection.commit()
        cursor.close()
    
    def process_item(self, item, spider):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (url, sector, raw_content, clean_content)
            VALUES (?, ?, ?, ?)
        ''', (item['url'], item['sector'], 
              item['raw_content'], item['clean_content']))
        self.connection.commit()
        cursor.close()
        return item
```

---

## Option 4: Use Docker CLI Directly (Manual Start)

If you prefer command-line control:

```bash
# Build images manually
docker build -t saip-crawler ./crawler
docker build -t saip-processor ./processor
docker build -t saip-ui ./ui

# Run PostgreSQL
docker run -d --name saip-db \
  -e POSTGRES_USER=intel_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=intel_db \
  -p 5432:5432 \
  -v saip-data:/var/lib/postgresql/data \
  postgres:16-alpine

# Wait 10 seconds for DB to start

# Run Crawler
docker run -d --name saip-crawler \
  --link saip-db:db \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -e DATABASE_URL=postgresql://intel_user:secure_password@db:5432/intel_db \
  saip-crawler

# Run UI
docker run -d --name saip-ui \
  -p 8501:8501 \
  -e DATABASE_URL=postgresql://intel_user:secure_password@db:5432/intel_db \
  saip-ui
```

---

## Troubleshooting

### "Docker daemon not found"
- **Windows**: Install Docker Desktop from docker.com
- **macOS**: Install Docker Desktop for Mac
- **Linux**: `sudo apt-get install docker-ce docker-compose`

### "Permission denied"
```bash
# On Windows (PowerShell as Admin)
# OR Linux/Mac
sudo usermod -aG docker $USER
newgrp docker
```

### Port Already in Use
Edit `docker-compose.yml`:
```yaml
# Change port mapping
ports:
  - "5433:5432"  # Use 5433 instead of 5432
  - "8502:8501"  # Use 8502 instead of 8501
```

### PostgreSQL Connection Error
```bash
# Check if container is running
docker ps

# Check logs
docker logs saip-db

# Restart database
docker restart saip-db

# Wait 10 seconds then check
docker ps
```

---

## Quick Commands

```bash
# Check Docker status
docker ps

# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Access database
docker exec -it saip-db psql -U intel_user -d intel_db

# Open dashboard
# Browser: http://localhost:8501

# Monitor crawler
docker logs -f saip-crawler

# View article count
docker exec saip-db psql -U intel_user -d intel_db -c "SELECT COUNT(*) FROM articles;"
```

---

## What Happens When Running

### Crawler Service
- Loads `config.yaml`
- Starts with Energy_Venezuela sector
- Visits seed URLs with Playwright
- Scores and queues links
- Sends articles to pipeline
- Stores in PostgreSQL

### Processor Service  
- Monitors new articles
- Performs NLP analysis
- Updates insights

### UI Dashboard
- Queries database
- Shows real-time metrics
- Allows searching articles

---

## Configuration for Local Testing

Edit `config.yaml` to crawl a simple test site:

```yaml
sectors:
  - name: "Test_Wikipedia"
    seeds:
      - "https://en.wikipedia.org/wiki/Web_scraping"
    keywords: ["data", "extraction", "web"]
    allowed_domains: ["wikipedia.org"]

crawler_settings:
  download_delay: 2          # Reduce delay for faster testing
  concurrent_requests: 2
  timeout: 15
```

---

## Next Steps

1. **Ensure Docker is Running**
   - Start Docker Desktop or Docker daemon

2. **Run the Platform**
   ```bash
   cd c:/Users/BAPS/Desktop/SAIP
   docker-compose up --build -d
   ```

3. **Wait for Services**
   ```bash
   # Check status
   docker-compose ps
   
   # Should see: "healthy" for db
   ```

4. **Access Dashboard**
   - Open `http://localhost:8501`

5. **Monitor Crawler**
   ```bash
   docker-compose logs -f crawler
   ```

---

## Support

- **Docker Issues**: https://docs.docker.com/get-docker/
- **Docker Compose**: https://docs.docker.com/compose/
- **Scrapy Docs**: https://docs.scrapy.org/
- **Troubleshooting**: See QUICKSTART.md

---

**Ready to crawl! 🕷️**
