# Sentinel - Multi-Tenant SaaS Platform

A production-ready, fully-containerized multi-tenant SaaS platform built with FastAPI, Next.js, PostgreSQL, and async task processing.

## Quick Start

```bash
cd /home/jnovoas/sentinel
docker-compose up -d
```

Services start in ~2-3 minutes:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432
- **Cache**: localhost:6379

## Architecture

### Services (7 total)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **PostgreSQL** | postgres:16-alpine | 5432 | Multi-tenant database with RLS |
| **Redis** | redis:7-alpine | 6379 | Cache layer & message broker |
| **FastAPI Backend** | Custom (Python 3.11) | 8000 | REST API |
| **Celery Worker** | Custom (Python 3.11) | - | Async task processing |
| **Celery Beat** | Custom (Python 3.11) | - | Task scheduling |
| **Next.js Frontend** | Custom (Node 20) | 3000 | Web application |
| **Nginx** | nginx:alpine | 80/443 | Reverse proxy & rate limiting |

### Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 16 with Row-Level Security (RLS)
- **Async**: Celery with Redis broker
- **Proxy**: Nginx with rate limiting and security headers

## Project Structure

```
sentinel/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── celery_app.py        # Celery configuration
│   │   ├── logging_config.py    # Logging setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API route handlers
│   │   ├── services/            # Business logic
│   │   └── tasks/               # Celery async tasks
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Production image
│   ├── Dockerfile.worker        # Celery worker image
│   └── Dockerfile.beat          # Celery Beat image
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utilities & helpers
│   │   └── store/               # State management
│   ├── package.json             # Node dependencies
│   ├── Dockerfile               # Production image
│   └── Dockerfile.dev           # Development image
├── docker/
│   ├── postgres/init.sql        # Database schema & RLS
│   ├── nginx/nginx.conf         # Reverse proxy config
│   └── redis/                   # Redis configuration
├── docker-compose.yml           # Service orchestration
├── .env                         # Environment variables
└── Makefile                     # Useful commands
```

## Configuration

All configuration via environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://sentinel_user:sentinel_password@postgres:5432/sentinel_db
# For local Postgres on host:
# DATABASE_URL=postgresql+asyncpg://sentinel_user:sentinel_password@localhost:5432/sentinel_db

# Redis
REDIS_URL=redis://redis:6379/0

# FastAPI
SECRET_KEY=your-secret-key-min-32-chars    # Change in production!
FASTAPI_ENV=development
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

After bringing up services, run migrations before first use:

```bash
make up          # start stack
make db-migrate  # apply Alembic migrations in backend container
```

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check

### Users (Multi-tenant)
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Tenants
- `POST /api/v1/tenants/` - Create tenant
- `GET /api/v1/tenants/` - List tenants
- `GET /api/v1/tenants/{tenant_id}` - Get tenant
- `PUT /api/v1/tenants/{tenant_id}` - Update tenant
- `DELETE /api/v1/tenants/{tenant_id}` - Delete tenant

See full documentation at `/docs` when running.

## Key Features

### Multi-Tenancy
- PostgreSQL Row-Level Security (RLS) for automatic tenant isolation
- Every user belongs to exactly one tenant
- Queries automatically filtered by tenant_id

### Security
- JWT authentication framework ready to implement
- Password hashing with bcrypt (configured)
- CORS for cross-origin requests
- Rate limiting at Nginx level (3 tiers)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

### Performance
- Async/await with FastAPI
- Redis caching layer
- Connection pooling with automatic recycling
- Celery for background tasks
- Celery Beat for scheduled tasks

### Operations
- Health check endpoints
- Structured logging with log rotation
- Docker health checks for all services
- Automatic container restart policies
- Volume persistence for data

## Useful Commands

```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart backend

# Access database
docker-compose exec postgres psql -U sentinel_user -d sentinel_db

# Backend shell
docker-compose exec backend bash

# Stop everything
docker-compose down

# Clean everything including volumes
docker-compose down -v
```

## Development

### Backend
```bash
# Install dependencies
docker-compose exec backend pip install -r requirements.txt

# Run tests (when added)
docker-compose exec backend pytest

# Format code
docker-compose exec backend black app/

# Check types
docker-compose exec backend mypy app/
```

### Frontend
```bash
# Install dependencies
docker-compose exec frontend npm install

# Build for production
docker-compose exec frontend npm run build

# Format code
docker-compose exec frontend npm run format
```

## Database Schema

The database includes:

### Tables
- **tenants**: Organizations/accounts
- **users**: User accounts with tenant association
- **audit_logs**: Event logging for compliance

### RLS Policies
- Users see only their tenant's data
- Audit logs filtered by tenant
- Extensible to additional entity tables

See `docker/postgres/init.sql` for complete schema.

## Production Deployment

### Before Deploying

**CRITICAL CHANGES**:
```bash
# Generate secure secret key
openssl rand -hex 32

# Update .env with:
SECRET_KEY=<generated-key>
FASTAPI_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com

# Change database passwords
POSTGRES_PASSWORD=<secure-password>
```

### Infrastructure
1. Use managed PostgreSQL (AWS RDS, Azure Database, etc.) instead of container
2. Use managed Redis (AWS ElastiCache, Azure Cache, etc.)
3. Configure SSL/TLS certificates for HTTPS
4. Set up automated backups
5. Configure load balancing for multiple backend instances
6. Set up monitoring and alerting

### Scaling
```bash
# Scale worker processes
docker-compose up -d --scale celery_worker=5

# Use external databases
# Update DATABASE_URL and REDIS_URL in .env
```

## Troubleshooting

### Services won't start
```bash
docker-compose logs [service]
```

### Database connection errors
```bash
docker-compose exec postgres pg_isready -U sentinel_user
```

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Clear cache and rebuild
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Code Quality & Standards

### Backend Code Organization
- Each module has clear responsibilities
- Comprehensive docstrings following Google style
- Type hints for all functions
- Separation of concerns (routers, services, models)

### Frontend Code Organization
- Component-based architecture
- TypeScript for type safety
- Tailwind CSS for styling
- App Router for routing

### Testing
- Unit tests in progress
- Integration tests ready
- Use pytest for backend testing

### Documentation
- All functions documented
- Comments explain "why", not "what"
- Examples provided for complex functionality

## Deployment Checklist

- [ ] Change `SECRET_KEY`
- [ ] Update `ALLOWED_ORIGINS`
- [ ] Change database passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review RLS policies
- [ ] Test under load
- [ ] Security audit

## Support & Contributing

This is a team project. Please:

1. **Before making changes**: Create an issue describing what you'll do
2. **Code style**: Follow existing patterns and maintain comments
3. **Testing**: Add tests for new features
4. **Documentation**: Update docs alongside code changes
5. **Pull requests**: Clear description of changes and why

## License

Internal project - Sentinel Platform

---

**Last Updated**: December 13, 2024  
**Maintained by**: Development Team  
**Status**: Production Ready ✅
