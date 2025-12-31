#!/bin/bash
# Setup Observability Authentication
# Generates .htpasswd files for Prometheus and Loki

set -e

echo "🔐 Setting up observability authentication..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, using defaults"
    echo "   Please update passwords in .env before production!"
fi

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Default passwords (CHANGE IN PRODUCTION!)
METRICS_PASSWORD="${OBSERVABILITY_METRICS_PASSWORD:-changeme123}"
LOGS_PASSWORD="${OBSERVABILITY_LOGS_PASSWORD:-changeme456}"

# Create directory if it doesn't exist
mkdir -p docker/nginx

# Generate .htpasswd files
echo "  Creating metrics authentication file..."
htpasswd -bc docker/nginx/.htpasswd_metrics sentinel_metrics "$METRICS_PASSWORD"

echo "  Creating logs authentication file..."
htpasswd -bc docker/nginx/.htpasswd_logs sentinel_logs "$LOGS_PASSWORD"

echo ""
echo "✅ Authentication files created:"
echo "   - docker/nginx/.htpasswd_metrics"
echo "   - docker/nginx/.htpasswd_logs"
echo ""
echo "📋 Credentials:"
echo "   Prometheus: sentinel_metrics / $METRICS_PASSWORD"
echo "   Loki:       sentinel_logs / $LOGS_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: Update passwords in .env before production deployment!"
echo "   Add these lines to .env:"
echo "   OBSERVABILITY_METRICS_PASSWORD=<strong-password>"
echo "   OBSERVABILITY_LOGS_PASSWORD=<strong-password>"
