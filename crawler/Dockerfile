# Multi-platform Dockerfile for Smart Crawler
# Supports both AMD64 (Windows) and ARM64 (Mac M4)

# Use Python 3.11 slim base to avoid pre-installed dependency conflicts
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal, avoid old pre-built packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install dependencies  
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Python package (skip browser install, use system chromium)
RUN pip install --no-cache-dir playwright==1.40.0 || true

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Default command - use custom runner to avoid signal handler incompatibilities
CMD ["python", "run_crawler.py", "Energy_Venezuela"]
