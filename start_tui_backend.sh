#!/bin/bash
# Start only essential Sentinel services for TUI/CLI usage
# No frontend, no observability stack - minimal resource usage

set -e

echo "🛡️ Starting Sentinel TUI Backend (minimal mode)..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

# Stop any running containers first
echo -e "${BLUE}🛑 Stopping any running containers...${NC}"
docker-compose stop 2>/dev/null || true

# Start only essential services
echo -e "${BLUE}🚀 Starting essential services...${NC}"
echo -e "${YELLOW}   - PostgreSQL (database)${NC}"
echo -e "${YELLOW}   - Redis (cache)${NC}"
echo -e "${YELLOW}   - Backend API${NC}"

docker-compose up -d postgres redis backend

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"

# Wait for database
echo -n "   Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U sentinel_user &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Wait for Redis
echo -n "   Waiting for Redis..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Wait for backend
echo -n "   Waiting for Backend API..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

# Check system Ollama (not Docker)
echo -e "${BLUE}🤖 Checking system Ollama (GPU-enabled)...${NC}"
if systemctl is-active --quiet ollama; then
    echo -e "${GREEN}✓ Ollama service running${NC}"
    
    # Check if model is available
    if ollama list | grep -q "llama3.2:3b"; then
        echo -e "${GREEN}✓ Model llama3.2:3b ready${NC}"
    else
        echo -e "${YELLOW}⚠️  Model llama3.2:3b not found${NC}"
        echo -e "${YELLOW}   Available models:${NC}"
        ollama list
    fi
else
    echo -e "${RED}❌ Ollama service not running${NC}"
    echo -e "${YELLOW}   Start with: sudo systemctl start ollama${NC}"
fi

echo ""
echo -e "${GREEN}✅ Sentinel TUI Backend ready!${NC}"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose ps postgres redis backend
echo ""
echo -e "${BLUE}🎯 You can now use:${NC}"
echo -e "   ${GREEN}sentinel-tui${NC}  - Interactive TUI"
echo -e "   ${GREEN}sentinel-cli${NC}  - Command-line queries"
echo ""
echo -e "${YELLOW}💡 To stop services:${NC}"
echo -e "   docker-compose stop"
echo ""
echo -e "${BLUE}ℹ️  Using system Ollama (GPU-enabled) at http://localhost:11434${NC}"
echo ""
