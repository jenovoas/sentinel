.PHONY: help up down build restart logs shell clean health test db-check

help:
	@echo "Sentinel - Multi-tenant SaaS Platform"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Build all containers"
	@echo "  make rebuild         - Rebuild containers without cache"
	@echo "  make restart         - Restart all services"
	@echo "  make restart-backend - Restart backend service only"
	@echo "  make logs            - View logs from all services"
	@echo "  make logs-backend    - View backend logs"
	@echo "  make logs-frontend   - View frontend logs"
	@echo "  make logs-worker     - View Celery worker logs"
	@echo "  make logs-db         - View database logs"
	@echo "  make shell-backend   - Open shell in backend container"
	@echo "  make shell-frontend  - Open shell in frontend container"
	@echo "  make shell-db        - Open PostgreSQL shell"
	@echo "  make db-backup       - Backup database"
	@echo "  make health          - Check service health"
	@echo "  make db-check        - Run local DB import/connection/health checks"
	@echo "  make db-migrate      - Run Alembic migrations (backend container)"
	@echo "  make clean           - Stop services and remove volumes"
	@echo "  make test-api        - Test API endpoints"
	@echo "  make ps              - Show running containers"
	@echo ""

up:
	@echo "Starting Sentinel services..."
	docker-compose up -d
	@echo "✓ Services started. Use 'make health' to check status."

down:
	@echo "Stopping Sentinel services..."
	docker-compose down

build:
	@echo "Building containers..."
	docker-compose build

rebuild:
	@echo "Rebuilding containers (no cache)..."
	docker-compose build --no-cache

restart:
	@echo "Restarting all services..."
	docker-compose restart

restart-backend:
	@echo "Restarting backend..."
	docker-compose restart backend

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-worker:
	docker-compose logs -f celery_worker

logs-db:
	docker-compose logs -f postgres

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend bash

shell-db:
	docker-compose exec postgres psql -U sentinel_user -d sentinel_db

db-backup:
	@echo "Creating database backup..."
	docker-compose exec -T postgres pg_dump -U sentinel_user sentinel_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup created"

health:
	@echo "Checking service health..."
	@echo ""
	@echo "PostgreSQL:"
	@docker-compose exec postgres pg_isready -U sentinel_user || echo "✗ Not ready"
	@echo ""
	@echo "Redis:"
	@docker-compose exec redis redis-cli ping || echo "✗ Not ready"
	@echo ""
	@echo "Backend API:"
	@curl -s http://localhost:8000/api/v1/health | jq . || echo "✗ Not ready"
	@echo ""
	@echo "Services status:"
	@docker-compose ps

clean:
	@echo "Cleaning up Sentinel..."
	docker-compose down -v
	@echo "✓ Cleaned"

test-api:
	@echo "Testing API endpoints..."
	@echo ""
	@echo "1. Health check:"
	@curl -s http://localhost:8000/api/v1/health | jq .
	@echo ""
	@echo "2. List tenants:"
	@curl -s http://localhost:8000/api/v1/tenants/ | jq .
	@echo ""
	@echo "3. List users:"
	@curl -s http://localhost:8000/api/v1/users/ | jq .

ps:
	docker-compose ps

# Local database connectivity checks (import, connect, health)
db-check:
	@cd backend && \
		( [ -x .venv/bin/python ] || python -m venv .venv ) && \
		.venv/bin/pip install -r requirements.txt && \
		.venv/bin/python -c "from app.database import engine, Base; print('✅ Import OK')" && \
		.venv/bin/python -c "import asyncio; from app.database import test_connection; print('Testing connection...'); print(f'✅ Connection: {asyncio.run(test_connection())}')" && \
		.venv/bin/python -c "import asyncio; from app.database import health_check; print('Health check:', asyncio.run(health_check()))"

# Database commands
db-migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

db-downgrade:
	@echo "Downgrading database..."
	docker-compose exec backend alembic downgrade -1

db-create-revision:
	@echo "Creating new migration..."
	docker-compose exec backend alembic revision --autogenerate -m "$(message)"

# Celery commands
celery-tasks:
	@echo "Active Celery tasks:"
	docker-compose exec celery_worker celery -A app.celery_app inspect active

celery-purge:
	@echo "Purging Celery queue..."
	docker-compose exec celery_worker celery -A app.celery_app purge

celery-stats:
	@echo "Celery worker stats:"
	docker-compose exec celery_worker celery -A app.celery_app inspect stats

# Development commands
dev-install-backend:
	docker-compose exec backend pip install -r requirements.txt

dev-install-frontend:
	docker-compose exec frontend npm install

format-backend:
	docker-compose exec backend black .
	docker-compose exec backend isort .

lint-backend:
	docker-compose exec backend flake8 app/

lint-frontend:
	docker-compose exec frontend npm run lint

type-check-frontend:
	docker-compose exec frontend npm run type-check

# Docker cleanup
docker-clean:
	@echo "Cleaning up Docker resources..."
	docker system prune -a -f
	@echo "✓ Cleaned"

docker-full-clean:
	@echo "Full Docker cleanup (WARNING: removes all unused resources)..."
	docker system prune -a --volumes -f
	@echo "✓ Cleaned"

.DEFAULT_GOAL := help
