# Host Metrics Storage

Sistema de captura y análisis de métricas de la **máquina host** (CPU, memoria, GPU, red, WiFi). Los contenedores Docker son solo para desarrollo.

## Estructura
- data/: archivos CSV con métricas capturadas del host
- scripts/: utilidades de ingesta, análisis y reporte
- reports/: reportes generados (HTML/Markdown)
- config.yaml: configuración de fuentes y etiquetas

## Características
- **Captura directa del host**: No depende de contenedores Docker
- **Métricas del sistema**: CPU (top), memoria (free), GPU (nvidia-smi), red (/sys/class/net)
- **WiFi**: SSID y señal via nmcli/iwconfig
- **Formato CSV**: Compatible con análisis y visualización
- **Automatización**: Scripts ejecutables via cron

## Uso rápido
1. Ingesta (guardar una muestra del host):
```bash
./scripts/ingest.sh
```

2. Análisis con umbrales:
```bash
python scripts/analyze.py --input data/metrics.csv --output reports/analysis.md \
  --cpu-threshold 80 --mem-threshold 85 --wifi-threshold 30
```

3. Reporte HTML:
```bash
python scripts/report.py --input data/metrics.csv --output reports/report.html
```

## Captura de métricas
El script `ingest.sh` captura directamente del host:
- **CPU**: Calcula uso desde `top -bn1`
- **Memoria**: Porcentaje desde `free`
- **GPU**: `nvidia-smi` (si disponible)
- **Red**: Bytes enviados/recibidos desde `/sys/class/net/*`
- **WiFi**: SSID y señal desde `nmcli` o `iwconfig`

### Dependencias
- Bash, awk, top, free
- nmcli o iwconfig (para WiFi)
- nvidia-smi (opcional, para GPU)
- Python 3.8+ (para análisis)

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
