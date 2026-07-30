.PHONY: help up down build restart logs shell clean health certify ps
 
help:
	@echo "Sentinel - Plataforma SaaS Multi-tenant (Protocolo YATRA)"
	@echo "=========================================================="
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make up              - Iniciar todos los servicios (Podman)"
	@echo "  make down            - Detener todos los servicios"
	@echo "  make build           - Construir todas las imágenes"
	@echo "  make restart         - Reiniciar todos los servicios"
	@echo "  make logs            - Ver logs de todos los servicios"
	@echo "  make shell-cortex    - Abrir terminal en el contenedor Cortex"
	@echo "  make health          - Verificar salud de los servicios"
	@echo "  make certify         - Ejecutar certificación aritmética S60"
	@echo "  make clean           - Limpiar servicios y volúmenes"
	@echo "  make ps              - Listar contenedores activos"
	@echo ""

certify:
	@echo "🧪 Ejecutando Certificación de Integridad Aritmética S60..."
	cargo run --release -p sentinel-cortex --bin certify_s60


up:
	@echo "🚀 Starting Full Sentinel Stack (Infrastructure + Backend + UI + Observability)..."
	docker-compose up -d
	@echo "✓ Full stack active. Use 'make health' to check status."

up-core:
	@echo "🧠 Starting Sentinel Core (DB + Cache + Backend)..."
	docker-compose up -d postgres redis backend celery_worker celery_beat
	@echo "✓ Core services active. RAM usage: Minimal."

up-dev:
	@echo "🛠️  Starting Development Stack (DB + Cache + Backend + Frontend)..."
	docker-compose up -d postgres redis backend frontend
	@echo "✓ Dev mode active. Antigravity should run smoothly now."

up-ai:
	@echo "🤖 Starting AI Engine (Ollama)..."
	docker-compose up -d ollama
	@echo "✓ AI active. Remember model loading consumes significant RAM."

down:
	@echo "Stopping Sentinel services..."
	docker-compose down

build:
	@echo "Building Sentinel components (Rust)..."
	cargo build --release -p sentinel-cortex
	@echo "✅ sentinel-cortex built"

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
