#!/bin/bash
# Sentinel Auto-Audit Script
# Generates the Traceability Matrix and commits it to Git to maintain a live record of system health.

PROJECT_DIR="/home/jnovoas/sentinel"
cd $PROJECT_DIR

echo "[$(date)] 🛡️ Starting Sentinel Self-Audit..."

# 1. Generate updated matrix with real-time metrics
python3 sentinel_matrix_gen.py

# 2. Add to Git if changes detected
if [[ -n $(git status --porcelain REQUIREMENTS_TRACEABILITY_MATRIX.md) ]]; then
    echo "[$(date)] 📝 Metrics changed. Committing updated health report..."
    git add REQUIREMENTS_TRACEABILITY_MATRIX.md
    git commit -m "auto-audit: Periodic system health update [$(date +%Y-%m-%d)]"
    git push origin main
else
    echo "[$(date)] ✅ System health stable. No documentation update required."
fi

echo "[$(date)] 🏁 Audit complete."
