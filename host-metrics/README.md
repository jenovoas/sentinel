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
- Puedes programar `scripts/ingest.sh` con `cron` o `systemd`.
- Los scripts aceptan `--interval` para ejecuciones periódicas.
