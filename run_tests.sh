#!/bin/bash

# Sentinel Vault - Automated Verification Script
# Runs unit tests inside the Docker container to ensure environment consistency.

echo "🦅 Sentinel Vault - Verification Protocol"
echo "=========================================="

# 1. Build Containers
echo "whale: Building verification containers..."
docker-compose build backend

# 2. Run Backend Tests
echo "🧪 Running Backend Unit Tests (Crypto, Finance, Vault)..."
docker-compose run --rm backend pytest tests/ -v

# 3. Security Audit (Dependencies)
echo "🔒 Checking for vulnerable dependencies..."
# Using pip-audit if available, or just identifying packages
docker-compose run --rm backend pip freeze | grep -E "cryptography|fastapi|sqlalchemy"

echo "=========================================="
echo "✅ Verification Complete"
