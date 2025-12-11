# 🚀 Quick Reference Guide - Smart Intel Platform

## 📋 Essential Commands

### Start Platform
```bash
# Windows
start.bat

# macOS/Linux
bash start.sh
```

### Stop Platform
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f crawler
docker-compose logs -f db
docker-compose logs -f processor
docker-compose logs -f ui
```

### Execute Commands in Container
```bash
# Trigger new crawl
docker-compose exec crawler scrapy crawl universal -a sector=Energy_Venezuela

# Access database
docker-compose exec db psql -U intel_user -d intel_db

# Run Python in processor
docker-compose exec processor python main.py
```

---

## 🎯 Configuration Changes

### Change Crawling Sector
Edit `config.yaml`:
```yaml
sectors:
  - name: "YOUR_SECTOR_NAME"
    seeds: ["https://..."]
    keywords: ["key1", "key2"]
    allowed_domains: ["domain.com"]
```

No rebuild needed - changes picked up automatically (volume mount).

### Adjust Crawler Speed
Edit `config.yaml`:
```yaml
crawler_settings:
  download_delay: 3      # Faster (more aggressive)
  concurrent_requests: 8 # More parallel requests
```

### Change Database Credentials
Edit `.env`:
```bash
POSTGRES_USER=my_user
POSTGRES_PASSWORD=my_password
POSTGRES_DB=my_db
DATABASE_URL=postgresql://my_user:my_password@db:5432/my_db
```

Then rebuild: `docker-compose build`

---

## 🔍 Database Queries

```bash
# Connect to DB
docker-compose exec db psql -U intel_user -d intel_db

# In psql prompt:

-- Total articles
SELECT COUNT(*) FROM articles;

-- Articles per sector
SELECT sector, COUNT(*) as count FROM articles GROUP BY sector ORDER BY count DESC;

-- Recent articles
SELECT url, sector, created_at FROM articles ORDER BY created_at DESC LIMIT 10;

-- Articles with error
SELECT * FROM articles WHERE clean_content IS NULL OR clean_content = '';

-- Search articles
SELECT * FROM articles WHERE url LIKE '%keyword%';

-- Articles from specific sector
SELECT * FROM articles WHERE sector = 'Energy_Venezuela';

-- Export to CSV
\COPY (SELECT * FROM articles) TO '/tmp/articles.csv' WITH CSV HEADER;
```

---

## 📊 Monitoring

### Check Service Status
```bash
docker-compose ps
```

### Monitor Resource Usage
```bash
docker stats
```

### Rebuild Services
```bash
# Full rebuild
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache crawler
```

---

## 🧪 Local Development

### Setup Development Environment
```bash
bash dev-setup.sh
source venv/bin/activate
```

### Test Crawler Locally
```bash
cd crawler
scrapy shell https://example.com
>>> response.xpath('//a/@href').getall()
```

### Debug Spider
```bash
# Run with verbose logging
cd crawler
scrapy crawl universal -a sector=Energy_Venezuela --loglevel=DEBUG
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "No database connection" | `docker-compose logs db` - ensure db is running |
| "Port 5432 in use" | Edit `docker-compose.yml`: `"5433:5432"` |
| "Playwright not found" | `docker-compose build --no-cache crawler` |
| "Permission denied start.sh" | `chmod +x start.sh` |
| "Config not updating" | Check volume mount: `docker inspect saip-crawler` |
| "High CPU usage" | Lower `concurrent_requests` in config.yaml |

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `config.yaml` | 🎯 Sectors, seeds, keywords configuration |
| `docker-compose.yml` | 🐳 Service orchestration |
| `.env.example` | 🔐 Environment variables template |
| `crawler/smart_crawler/universal_spider.py` | 🧠 The intelligent crawler brain |
| `crawler/smart_crawler/middlewares.py` | 🎭 Stealth & identity rotation |
| `crawler/smart_crawler/pipelines.py` | 🧹 Data cleaning & storage |
| `ui/app.py` | 📊 Streamlit dashboard |
| `processor/main.py` | 🤖 NLP processing service |

---

## 🌐 Access Points

| Service | URL/Port | Access |
|---------|----------|--------|
| PostgreSQL | `localhost:5432` | `psql -U intel_user -d intel_db` |
| Streamlit UI | `http://localhost:8501` | Web browser |
| Crawler | Internal | `docker-compose logs crawler` |

---

## 📈 Performance Tips

1. **Increase crawling speed:**
   ```yaml
   download_delay: 2          # Reduce delay
   concurrent_requests: 8     # More parallel
   ```

2. **Reduce resource usage:**
   ```yaml
   download_delay: 10         # Increase delay
   concurrent_requests: 2     # Less parallel
   DOWNLOAD_TIMEOUT: 20       # Shorter timeout
   ```

3. **Better data quality:**
   - Refine keywords in `config.yaml`
   - Adjust link scoring thresholds
   - Add more allowed_domains

---

## 🔐 Security Checklist

- [ ] Changed default PostgreSQL password in `.env`
- [ ] Set appropriate `allowed_domains` in config.yaml
- [ ] Configured rate limiting for target sites
- [ ] Monitored logs for 429/403 errors
- [ ] Verified robots.txt compliance
- [ ] Set up backups for `/data` directory

---

## 📞 Support Resources

- **Documentation:** See `README.md` and `ARCHITECTURE.md`
- **Scrapy Docs:** https://docs.scrapy.org/
- **Playwright:** https://playwright.dev/python/
- **Docker Compose:** https://docs.docker.com/compose/
- **PostgreSQL:** https://www.postgresql.org/docs/

---

**Last Updated:** December 4, 2024
**Platform:** Smart Intel Platform v1.0
