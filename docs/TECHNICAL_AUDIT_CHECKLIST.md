# 🔍 Sentinel - Technical Audit Checklist

**Production readiness review - Critical patterns to verify**

---

## 📋 Overview

Este documento contiene los patrones críticos que debes revisar en Sentinel antes de producción. Cada sección incluye qué verificar, cómo hacerlo, y qué arreglar si hay problemas.

---

## 🛡️ 1. High Availability (HA) Debugging

### Patrones a Verificar

#### 1.1 PostgreSQL HA (Patroni + etcd)

**Verificar**:
```bash
# Estado del cluster
docker-compose exec postgres patronictl list

# Debe mostrar:
# + Cluster: sentinel (7123456789012345678) -----+----+-----------+
# | Member   | Host        | Role    | State   | TL | Lag in MB |
# +----------+-------------+---------+---------+----+-----------+
# | postgres | 172.18.0.2  | Leader  | running |  1 |           |
# | replica1 | 172.18.0.3  | Replica | running |  1 |         0 |
```

**Problemas Comunes**:
- ❌ Replica no sincroniza → Check network, check `postgresql.conf`
- ❌ Failover no automático → Check etcd quorum
- ❌ Split-brain → Check etcd connectivity

**Debug Commands**:
```bash
# Ver logs de Patroni
docker-compose logs -f patroni

# Ver estado de etcd
docker-compose exec etcd etcdctl member list

# Forzar failover (testing)
docker-compose exec postgres patronictl failover

# Ver replication lag
docker-compose exec postgres psql -U sentinel_user -c "SELECT * FROM pg_stat_replication;"
```

#### 1.2 Redis HA (Sentinel)

**Verificar**:
```bash
# Estado de Redis Sentinel
docker-compose exec redis-sentinel redis-cli -p 26379 SENTINEL masters

# Debe mostrar master con 2+ sentinels
```

**Problemas Comunes**:
- ❌ Sentinel no detecta master → Check `sentinel.conf`
- ❌ Failover lento → Ajustar `down-after-milliseconds`
- ❌ Quorum incorrecto → Debe ser mayoría (2 de 3)

**Debug Commands**:
```bash
# Ver configuración de Sentinel
docker-compose exec redis-sentinel redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# Simular fallo de master
docker-compose stop redis-master

# Ver logs de failover
docker-compose logs -f redis-sentinel
```

#### 1.3 Application HA

**Verificar**:
```bash
# Health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/live

# Todos deben retornar 200 OK
```

**Problemas Comunes**:
- ❌ `/health` falla → Check database connection
- ❌ `/ready` falla → Check dependencies (Redis, etc.)
- ❌ Graceful shutdown no funciona → Check signal handlers

**Debug Commands**:
```bash
# Ver health checks en logs
docker-compose logs backend | grep health

# Simular restart
docker-compose restart backend

# Verificar que no hay requests perdidos
ab -n 1000 -c 10 http://localhost:8000/health
```

---

## 🗄️ 2. PostgreSQL Query Optimization

### Patrones a Verificar

#### 2.1 Slow Queries

**Verificar**:
```sql
-- Habilitar logging de slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1 segundo
SELECT pg_reload_conf();

-- Ver queries lentas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**Problemas Comunes**:
- ❌ Queries > 1s → Necesitan optimización
- ❌ Full table scans → Faltan índices
- ❌ N+1 queries → Usar JOINs o eager loading

**Optimizaciones**:
```sql
-- Ejemplo: Query lenta
SELECT * FROM events WHERE organization_id = 123 AND created_at > NOW() - INTERVAL '7 days';

-- Crear índice compuesto
CREATE INDEX idx_events_org_created ON events(organization_id, created_at DESC);

-- Verificar que usa el índice
EXPLAIN ANALYZE SELECT * FROM events WHERE organization_id = 123 AND created_at > NOW() - INTERVAL '7 days';
```

#### 2.2 Missing Indexes

**Verificar**:
```sql
-- Queries que necesitan índices
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.1;

-- Tablas sin índices (excepto PK)
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname NOT LIKE '%_pkey';
```

**Índices Críticos para Sentinel**:
```sql
-- Organizations
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_created_at ON organizations(created_at DESC);

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org_id ON users(organization_id);

-- Events (telemetry)
CREATE INDEX idx_events_org_timestamp ON events(organization_id, timestamp DESC);
CREATE INDEX idx_events_severity ON events(severity) WHERE severity >= 'WARNING';

-- Metrics
CREATE INDEX idx_metrics_org_name_timestamp ON metrics(organization_id, metric_name, timestamp DESC);
```

#### 2.3 Connection Pooling

**Verificar**:
```sql
-- Ver conexiones activas
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Debe ser < max_connections (default 100)
```

**Configuración Óptima**:
```python
# backend/app/database.py
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Conexiones permanentes
    max_overflow=10,       # Conexiones adicionales bajo carga
    pool_timeout=30,       # Timeout para obtener conexión
    pool_recycle=3600,     # Reciclar conexiones cada hora
    pool_pre_ping=True,    # Verificar conexión antes de usar
)
```

---

## ⚡ 3. FastAPI Features Implementation

### Patrones a Verificar

#### 3.1 Async/Await Correctamente

**Verificar**:
```python
# ❌ INCORRECTO - Bloquea el event loop
@app.get("/users")
def get_users():
    users = db.query(User).all()  # Sync query
    return users

# ✅ CORRECTO - Non-blocking
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

**Buscar en código**:
```bash
# Encontrar funciones sync que deberían ser async
grep -r "def get_\|def create_\|def update_" backend/app/api/ | grep -v "async def"
```

#### 3.2 Dependency Injection

**Verificar**:
```python
# ✅ Usar Depends para DB, auth, etc.
@app.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return {"user": current_user.email}
```

**Patrones a seguir**:
```python
# backend/app/api/deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Validar token, obtener user
    pass

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(403)
    return current_user
```

#### 3.3 Error Handling

**Verificar**:
```python
# ✅ Exception handlers globales
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
```

#### 3.4 Request Validation (Pydantic)

**Verificar**:
```python
# ✅ Schemas bien definidos
class UserCreate(BaseModel):
    email: EmailStr  # Valida formato email
    password: str = Field(..., min_length=8)
    organization_id: int = Field(..., gt=0)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Must contain uppercase')
        return v
```

#### 3.5 Background Tasks

**Verificar**:
```python
# ✅ Usar BackgroundTasks para operaciones lentas
from fastapi import BackgroundTasks

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email)
    return {"message": "Notification queued"}

# O mejor: usar Celery para tasks pesados
@celery_app.task
def process_large_dataset(data_id: int):
    # Procesamiento pesado
    pass
```

---

## 🔄 4. CI/CD Pipeline Configuration

### Patrones a Verificar

#### 4.1 GitHub Actions Workflow

**Verificar archivo**: `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linters
        run: |
          pip install black flake8 mypy
          black --check backend/
          flake8 backend/
          mypy backend/
  
  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker-compose build
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker-compose push
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/sentinel
            git pull origin main
            docker-compose pull
            docker-compose up -d
            docker-compose exec backend alembic upgrade head
```

#### 4.2 Pre-commit Hooks

**Verificar archivo**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--ignore=E203,W503']
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Instalar**:
```bash
pip install pre-commit
pre-commit install
```

#### 4.3 Docker Multi-stage Builds

**Verificar**: `backend/Dockerfile`

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Non-root user
RUN useradd -m -u 1000 sentinel && chown -R sentinel:sentinel /app
USER sentinel

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4.4 Environment-specific Configs

**Verificar estructura**:
```
config/
├── production.env
├── staging.env
└── development.env

docker-compose.production.yml
docker-compose.staging.yml
docker-compose.yml (development)
```

**Deploy script**:
```bash
#!/bin/bash
# scripts/deploy.sh

ENV=$1  # production, staging, development

if [ -z "$ENV" ]; then
    echo "Usage: ./deploy.sh [production|staging|development]"
    exit 1
fi

# Load environment
export $(cat config/${ENV}.env | xargs)

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.${ENV}.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Health check
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployed to $ENV successfully"
```

---

## 📊 Checklist de Auditoría

### High Availability
- [ ] PostgreSQL Patroni cluster funciona
- [ ] Failover automático probado
- [ ] Redis Sentinel configurado
- [ ] Health endpoints responden
- [ ] Graceful shutdown implementado
- [ ] Load balancer configurado (HAProxy/Nginx)

### Database Performance
- [ ] Slow query log habilitado
- [ ] Índices en todas las foreign keys
- [ ] Índices en campos de búsqueda frecuente
- [ ] Connection pooling configurado
- [ ] VACUUM y ANALYZE automáticos
- [ ] Backup automático funcionando

### FastAPI Best Practices
- [ ] Todas las rutas usan async/await
- [ ] Dependency injection para DB y auth
- [ ] Exception handlers globales
- [ ] Request validation con Pydantic
- [ ] Background tasks para operaciones lentas
- [ ] Rate limiting implementado
- [ ] CORS configurado correctamente

### CI/CD
- [ ] Tests automáticos en cada PR
- [ ] Coverage > 80%
- [ ] Linters configurados (black, flake8, mypy)
- [ ] Pre-commit hooks instalados
- [ ] Docker images optimizadas (multi-stage)
- [ ] Deploy automático a staging
- [ ] Deploy manual a production (con aprobación)
- [ ] Rollback plan documentado

### Security
- [ ] Secrets en variables de entorno (no hardcoded)
- [ ] HTTPS habilitado
- [ ] JWT tokens con expiración
- [ ] SQL injection prevention (ORM)
- [ ] XSS prevention (sanitización)
- [ ] CSRF protection
- [ ] Rate limiting por IP

### Monitoring
- [ ] Prometheus scraping métricas
- [ ] Grafana dashboards configurados
- [ ] Alertas para errores críticos
- [ ] Logs centralizados (Loki)
- [ ] APM para tracing (opcional)

---

## 🚀 Comandos Rápidos de Auditoría

```bash
# Verificar todo de una vez
./scripts/audit.sh

# O manualmente:

# 1. HA Status
docker-compose exec postgres patronictl list
docker-compose exec redis-sentinel redis-cli -p 26379 SENTINEL masters

# 2. Database Health
docker-compose exec postgres psql -U sentinel_user -d sentinel_db -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS rows
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# 3. Slow Queries
docker-compose exec postgres psql -U sentinel_user -d sentinel_db -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# 4. API Health
curl http://localhost:8000/health | jq .
curl http://localhost:8000/metrics | grep -E "http_requests|db_connections"

# 5. Test Coverage
cd backend && pytest --cov=app --cov-report=term-missing

# 6. Linting
black --check backend/
flake8 backend/
mypy backend/
```

---

**Última actualización**: Diciembre 2024  
**Próxima auditoría**: Antes de cada release a producción
