#!/bin/bash

# Sentinel Installation Verification Script
# This script verifies that all required files and directories are in place

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Sentinel - Installation Verification                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Helper functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        ((ERRORS++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/"
        ((ERRORS++))
        return 1
    fi
}

warn_file() {
    if [ ! -f "$1" ]; then
        echo -e "${YELLOW}⚠${NC} $1 (optional)"
        ((WARNINGS++))
    fi
}

echo -e "${BLUE}📋 Checking Core Configuration Files...${NC}"
check_file "docker-compose.yml"
check_file ".env"
check_file "README.md"
check_file "SETUP.md"
check_file "Makefile"
check_file "startup.sh"
echo ""

echo -e "${BLUE}📁 Checking Backend Structure...${NC}"
check_dir "backend"
check_dir "backend/app"
check_file "backend/requirements.txt"
check_file "backend/Dockerfile"
check_file "backend/Dockerfile.worker"
check_file "backend/Dockerfile.beat"
echo ""

echo -e "${BLUE}🐍 Checking Backend Python Files...${NC}"
check_file "backend/app/__init__.py"
check_file "backend/app/main.py"
check_file "backend/app/config.py"
check_file "backend/app/database.py"
check_file "backend/app/celery_app.py"
check_file "backend/app/logging_config.py"
echo ""

echo -e "${BLUE}📦 Checking Backend Modules...${NC}"
check_dir "backend/app/models"
check_dir "backend/app/schemas"
check_dir "backend/app/routers"
check_dir "backend/app/services"
check_dir "backend/app/tasks"
check_file "backend/app/models/__init__.py"
check_file "backend/app/schemas/__init__.py"
check_file "backend/app/routers/__init__.py"
check_file "backend/app/services/__init__.py"
check_file "backend/app/tasks/__init__.py"
echo ""

echo -e "${BLUE}🛣️  Checking Backend Routers...${NC}"
check_file "backend/app/routers/health.py"
check_file "backend/app/routers/users.py"
check_file "backend/app/routers/tenants.py"
echo ""

echo -e "${BLUE}⚙️  Checking Backend Tasks...${NC}"
check_file "backend/app/tasks/cleanup.py"
check_file "backend/app/tasks/health.py"
echo ""

echo -e "${BLUE}⚛️  Checking Frontend Structure...${NC}"
check_dir "frontend"
check_dir "frontend/src"
check_dir "frontend/public"
check_file "frontend/package.json"
check_file "frontend/next.config.js"
check_file "frontend/tsconfig.json"
check_file "frontend/tailwind.config.js"
check_file "frontend/postcss.config.js"
check_file "frontend/Dockerfile"
check_file "frontend/Dockerfile.dev"
echo ""

echo -e "${BLUE}📄 Checking Frontend App Files...${NC}"
check_dir "frontend/src/app"
check_file "frontend/src/app/layout.tsx"
check_file "frontend/src/app/page.tsx"
check_file "frontend/src/app/globals.css"
echo ""

echo -e "${BLUE}📁 Checking Frontend Directories...${NC}"
check_dir "frontend/src/components"
check_dir "frontend/src/lib"
check_dir "frontend/src/hooks"
check_dir "frontend/src/store"
echo ""

echo -e "${BLUE}🗄️  Checking Docker Configuration...${NC}"
check_dir "docker"
check_dir "docker/postgres"
check_dir "docker/nginx"
check_dir "docker/redis"
check_file "docker/postgres/init.sql"
check_file "docker/nginx/nginx.conf"
check_file "docker/nginx/Dockerfile"
echo ""

echo -e "${BLUE}📝 Checking Documentation...${NC}"
check_file "README.md"
check_file "SETUP.md"
check_file "INSTALLED.md"
warn_file "docker/.env.example"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Verification Results                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Summary
echo -e "${BLUE}📊 Summary:${NC}"
echo -e "  Files created: $(find . -type f -not -path '*/\.*' | wc -l)"
echo -e "  Directories: $(find . -type d -not -path '*/\.*' | wc -l)"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All required files and directories are in place!${NC}"
else
    echo -e "${RED}✗ Missing $ERRORS required file(s) or directory(ies)${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS optional file(s) missing${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Quick Start:${NC}"
echo "  1. Verify Docker is running: docker --version"
echo "  2. Start services: docker-compose up -d"
echo "  3. Wait 2-3 minutes for services to initialize"
echo "  4. Check health: make health"
echo "  5. Access services:"
echo "     • Frontend: http://localhost:3000"
echo "     • API: http://localhost:8000"
echo "     • Docs: http://localhost:8000/docs"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Installation verification passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Installation verification failed!${NC}"
    exit 1
fi
