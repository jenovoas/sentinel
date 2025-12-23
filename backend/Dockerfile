FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    netcat-traditional \
    curl \
    git \
    network-manager \
    wireless-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app/ ./app/

# Copy Alembic migrations
COPY backend/alembic.ini ./alembic.ini
COPY backend/alembic ./alembic/

# Copy entrypoint script
COPY backend/entrypoint.sh /entrypoint.sh
# Ensure Unix line endings to avoid "exec /entrypoint.sh: no such file or directory" on Windows hosts
RUN sed -i 's/\r$//' /entrypoint.sh && chmod 755 /entrypoint.sh

# Create logs directory
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
