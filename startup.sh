#!/bin/bash

echo "🚀 Sentinel Startup Verification"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ docker-compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ docker-compose found${NC}"
echo ""

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Using default environment variables.${NC}"
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi

echo ""
echo "📦 Starting Sentinel services..."
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "🔍 Checking service health..."
echo ""

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker-compose exec postgres pg_isready -U sentinel_user &> /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Check Redis
echo -n "Redis: "
if docker-compose exec redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Check Backend
echo -n "Backend API: "
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy (starting up...)${NC}"
fi

# Check Frontend
echo -n "Frontend: "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Starting up...${NC}"
fi

# Check Nginx
echo -n "Nginx Proxy: "
if curl -s http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Starting up...${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✓ Sentinel Installation Complete!${NC}"
echo ""
echo "📍 Access Points:"
echo "   • Frontend:     http://localhost:3000"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • Nginx Proxy:  http://localhost:80"
echo ""
echo "📊 Services Running:"
docker-compose ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "💡 Useful Commands:"
echo "   • View logs:    docker-compose logs -f [service]"
echo "   • Stop services: docker-compose down"
echo "   • Access DB:    docker-compose exec postgres psql -U sentinel_user -d sentinel_db"
echo ""
echo "📖 Full documentation in README.md"
echo ""
