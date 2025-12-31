#!/usr/bin/env bash
set -euo pipefail

# Auto-configure crontab entries for host-metrics
# Detect absolute project path and inject tasks

PROJECT_DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/host-metrics/scripts"
DATA_DIR="$PROJECT_DIR/host-metrics/data"
REPORTS_DIR="$PROJECT_DIR/host-metrics/reports"

if ! command -v crontab >/dev/null 2>&1; then
  echo "Error: crontab no está instalado. Instala cron (e.g., cronie en Arch)." >&2
  exit 1
fi

mkdir -p "$DATA_DIR" "$REPORTS_DIR"

TMP_CRON="$(mktemp)"

# Preserve existing entries
crontab -l 2>/dev/null > "$TMP_CRON" || true

# Remove previous sentinel entries
sed -i '/# SENTINEL-HOST-METRICS START/,/# SENTINEL-HOST-METRICS END/d' "$TMP_CRON"

cat >> "$TMP_CRON" <<EOF
# SENTINEL-HOST-METRICS START
# Generated at: $(date -Iseconds)
# Paths:
# PROJECT_DIR=$PROJECT_DIR
# SCRIPTS_DIR=$SCRIPTS_DIR
# DATA_DIR=$DATA_DIR
# REPORTS_DIR=$REPORTS_DIR

# PATH for tools
PATH=/usr/local/bin:/usr/bin:/bin

# Ingesta cada minuto
* * * * * bash $SCRIPTS_DIR/ingest.sh >> $DATA_DIR/ingest.log 2>&1

# Análisis cada hora
0 * * * * python $SCRIPTS_DIR/analyze.py --input $DATA_DIR/metrics.csv --output $REPORTS_DIR/analysis.md >> $DATA_DIR/analyze.log 2>&1

# Reporte HTML cada hora
5 * * * * python $SCRIPTS_DIR/report.py --input $DATA_DIR/metrics.csv --output $REPORTS_DIR/report.html >> $DATA_DIR/report.log 2>&1

# SENTINEL-HOST-METRICS END
EOF

# Install new crontab
crontab "$TMP_CRON"
rm -f "$TMP_CRON"

echo "✓ Crontab instalado para host-metrics"
echo "- Ver logs en: $DATA_DIR/{ingest,analyze,report}.log"
echo "- Desinstalar: crontab -l | sed '/# SENTINEL-HOST-METRICS START/,/# SENTINEL-HOST-METRICS END/d' | crontab -"
