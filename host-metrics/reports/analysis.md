
# Análisis de Métricas (Host)

- Muestras: 2125
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-16T04:59:00.627Z

## Promedios
- CPU: 29.95%
- Memoria: 55.82%
- GPU: 4.08%
- WiFi (señal): 64.18%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
