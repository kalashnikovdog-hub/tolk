FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for scraping
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for headless browser
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV CHROME_BIN=/usr/bin/chromium

# Install Playwright browsers
RUN playwright install chromium

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["scrapy", "crawl", "all_stores"]
