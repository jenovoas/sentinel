# Host Metrics Storage

Estructura para guardar métricas en el host y generar análisis y reportes automáticos.

## Estructura
- data/: archivos CSV/JSON con métricas crudas
- scripts/: utilidades de ingesta, análisis y reporte
- reports/: reportes generados (HTML/Markdown/CSV)
- config.yaml: configuración de fuentes y etiquetas

## Uso rápido
1. Ingesta (guardar una muestra):
```bash
./scripts/ingest.sh
```

2. Análisis:
```bash
python scripts/analyze.py --input data/metrics.csv --output reports/analysis.md
```

3. Reporte HTML:
```bash
python scripts/report.py --input data/metrics.csv --output reports/report.html
```

## Formato de datos
- metrics.csv: cabeceras
```
timestamp,cpu_percent,mem_percent,gpu_percent,net_bytes_sent,net_bytes_recv,wifi_ssid,wifi_signal
```

## Automatización
- Puedes programar `scripts/ingest.sh` con `cron`.
- Ejemplo de crontab (ver `scripts/cron.example`):

```
# Ingesta cada minuto
* * * * * bash /home/jnovoas/sentinel/host-metrics/scripts/ingest.sh >> /home/jnovoas/sentinel/host-metrics/data/ingest.log 2>&1

# Análisis cada hora
0 * * * * python /home/jnovoas/sentinel/host-metrics/scripts/analyze.py --input /home/jnovoas/sentinel/host-metrics/data/metrics.csv --output /home/jnovoas/sentinel/host-metrics/reports/analysis.md >> /home/jnovoas/sentinel/host-metrics/data/analyze.log 2>&1

# Reporte HTML cada hora
5 * * * * python /home/jnovoas/sentinel/host-metrics/scripts/report.py --input /home/jnovoas/sentinel/host-metrics/data/metrics.csv --output /home/jnovoas/sentinel/host-metrics/reports/report.html >> /home/jnovoas/sentinel/host-metrics/data/report.log 2>&1
```

### Pasos
- Copia el ejemplo: `crontab host-metrics/scripts/cron.example`
- Verifica logs en `host-metrics/data/*.log`
