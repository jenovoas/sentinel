#!/bin/bash
set -e

# Sentinel - One-Command Startup Script
# Starts all services in the correct order with health checks

echo "🚀 Starting Sentinel Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        print_warning ".env not found, copying from .env.example"
        cp .env.example .env
        print_status "Created .env file"
    else
        print_error ".env file not found. Please create one."
        exit 1
    fi
fi

# Load environment variables from .env into the script (so AI_ENABLED and others are available)
if [ -f .env ]; then
    set -o allexport
    # shellcheck disable=SC1091
    . ./.env
    set +o allexport
fi

# Start core infrastructure first
echo ""
echo "📦 Starting Core Infrastructure..."
docker-compose up -d postgres redis
sleep 3

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-sentinel_user} -d ${POSTGRES_DB:-sentinel_db} > /dev/null 2>&1; do
    echo -n "."
    sleep 1
done
print_status "PostgreSQL is ready"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo -n "."
    sleep 1
done
print_status "Redis is ready"

# Start backend services
echo ""
echo "🔧 Starting Backend Services..."
docker-compose up -d backend celery_worker celery_beat
sleep 5

# Wait for backend to be healthy
echo "⏳ Waiting for Backend API..."
until curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
print_status "Backend API is ready"

# Start frontend
echo ""
echo "🎨 Starting Frontend..."
docker-compose up -d frontend nginx
sleep 3
print_status "Frontend started"

# Start observability stack
echo ""
echo "📊 Starting Observability Stack..."
docker-compose up -d prometheus loki promtail node-exporter postgres-exporter redis-exporter
sleep 3
print_status "Metrics collection started"

docker-compose up -d grafana
sleep 5
print_status "Grafana started"

# Start automation
echo ""
echo "🤖 Starting Automation..."
docker-compose up -d n8n
sleep 3
print_status "n8n started"

# Start AI services
echo ""
echo "🧠 Starting AI Services..."
if [ "${AI_ENABLED:-false}" = "true" ]; then
    docker-compose up -d ollama
    sleep 5

    # Check if Ollama is healthy
    if docker-compose ps ollama | grep -q "healthy\|Up"; then
        print_status "Ollama started"

        # Download models if not present
        if ! curl -s http://localhost:11434/api/tags | grep -q "phi3:mini"; then
            print_warning "Downloading AI model (phi3:mini, ~2GB)..."
            print_warning "This may take 5-10 minutes on first run..."
            docker-compose up ollama-init
            print_status "AI model downloaded"
        else
            print_status "AI model already present"
        fi
    else
        print_warning "Ollama started but may not be healthy yet"
    fi
else
    print_status "AI disabled (AI_ENABLED=${AI_ENABLED:-false}), skipping Ollama"
fi

# Final status check
echo ""
echo "🔍 Checking Service Status..."
echo ""

# Check all services
SERVICES=$(docker-compose ps --services)
HEALTHY=0
TOTAL=0

for service in $SERVICES; do
    if [ "$service" = "ollama-init" ] || [ "$service" = "n8n-loader" ]; then
        continue  # Skip one-time services
    fi
    
    TOTAL=$((TOTAL + 1))
    STATUS=$(docker-compose ps $service --format "{{.Status}}" 2>/dev/null || echo "not running")
    
    if echo "$STATUS" | grep -q "Up\|healthy"; then
        print_status "$service"
        HEALTHY=$((HEALTHY + 1))
    else
        print_error "$service - $STATUS"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $HEALTHY -eq $TOTAL ]; then
    echo -e "${GREEN}✓ All services are running! ($HEALTHY/$TOTAL)${NC}"
else
    echo -e "${YELLOW}⚠ Some services may need attention ($HEALTHY/$TOTAL running)${NC}"
fi

echo ""
echo "🌐 Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Frontend:        http://localhost:3000"
echo "  API:             http://localhost:8000"
echo "  API Docs:        http://localhost:8000/docs"
echo "  Grafana:         http://localhost:3001  (admin / darkfenix)"
echo "  Prometheus:      http://localhost:9090"
echo "  n8n:             http://localhost:5678  (admin / darkfenix)"
echo "  Ollama AI:       http://localhost:11434"
echo ""
echo "📚 Documentation:"
echo "  README.md        - Architecture overview"
echo "  docs/            - Detailed guides"
echo ""
echo "🛠️  Useful Commands:"
echo "  docker-compose ps              - View service status"
echo "  docker-compose logs -f SERVICE - View service logs"
echo "  docker-compose down            - Stop all services"
echo "  docker-compose restart SERVICE - Restart a service"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Sentinel is ready!${NC}"
echo ""
