# 🧰 Sentinel Cortex Tooling Kit

Este directorio contiene las herramientas de operación y mantenimiento para **Sentinel Cortex**.

## 1. CLI de Control (`sentinel`)
Script maestro para gestionar el ciclo de vida del sistema.
**Instalación**: `sudo ln -sf $(pwd)/tools/sentinel_ctl /usr/local/bin/sentinel`

**Uso**:
```bash
sudo sentinel start    # Carga eBPF, inicia Relay y Pulso
sudo sentinel stop     # Detiene todo y descarga BPF
sudo sentinel status   # Muestra estado de componentes
sudo sentinel logs     # Tail de logs
sudo sentinel bench    # Ejecuta benchmark de sistema
```

## 2. Automatización de Mantenimiento
Script para rotación de logs y backup de la Memoria Compartida (SHM).
**Script**: `tools/sentinel_maintenance.sh`

**Configuración Cron (Sugerncia)**:
Editar crontab root (`sudo crontab -e`):
```cron
# Ejecutar mantenimiento diario a las 03:00 AM
0 3 * * * /home/jnovoas/sentinel/tools/sentinel_maintenance.sh >> /var/log/sentinel/maintenance.log 2>&1
```

## 3. Observabilidad (Exporter)
Script ligero para extraer métricas del SHM en formato JSON.
**Script**: `tools/sentinel_exporter.py`

**Uso**:
```bash
./tools/sentinel_exporter.py
# Salida:
# {
#   "timestamp": 1704123456,
#   "metrics": {
#     "entropy": 0.12,
#     "coherence": 0.99,
#     "tte_us": 3.23
#   }
# }
```
Útil para integración con Prometheus/Grafana (vía script exporter) o diagnósticos rápidos.
