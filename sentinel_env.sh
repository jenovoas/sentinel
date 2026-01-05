#!/bin/bash
# Sentinel Environment Configuration
# Source this file before running the TUI: source sentinel_env.sh

# AI Provider: "ollama" or "antigravity" (Gemini)
# Using Ollama due to Google API rate limits
export SENTINEL_AI_PROVIDER="ollama"

# Antigravity/Gemini Model (2.0-flash-001 is stable GA version)
export ANTIGRAVITY_MODEL="gemini-2.0-flash-001"

# Google AI API Key (get from https://aistudio.google.com/apikey)
export GOOGLE_AI_API_KEY="AIzaSyCUf3hoaiPIpjxrVwKh2Q9N_gEifgI1eR0"

# Backend URLs
export BACKEND_URL="http://127.0.0.1:8000"
export DATABASE_URL="postgresql+asyncpg://sentinel_user:2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4@127.0.0.1:5432/sentinel_db"
export REDIS_URL="redis://127.0.0.1:6379/0"
export OLLAMA_URL="http://127.0.0.1:11434"
export N8N_URL="http://127.0.0.1:5678/webhook/learning"
export TRUTHSYNC_N8N_URL="http://127.0.0.1:5678/webhook/truthsync-audit"

# Cortex
export CORTEX_URL="http://localhost:3005"
