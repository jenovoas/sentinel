FROM python:3.11-slim

WORKDIR /app

# Install only the runtime tools required by the API container.
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    libelf1 \
    zlib1g \
    libzstd1 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system sentinel-api && useradd --system --gid sentinel-api \
    --no-create-home --shell /usr/sbin/nologin sentinel-api

# Build context is the repository root so the image includes the shared
# quantum package imported by the FastAPI application.
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app/ ./app/
COPY quantum/ ./quantum/
COPY backend/me60os_core.so ./quantum/me60os_core.so

# Copy Alembic migrations
COPY backend/alembic.ini ./alembic.ini
COPY backend/alembic/ ./alembic/

COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

# Create logs directory
RUN mkdir -p logs && chown sentinel-api:sentinel-api logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Run entrypoint script
USER sentinel-api
ENTRYPOINT ["/entrypoint.sh"]
