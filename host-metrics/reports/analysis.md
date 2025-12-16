
# Análisis de Métricas (Host)

- Muestras: 2185
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-16T05:59:01.032Z

## Promedios
- CPU: 29.75%
- Memoria: 55.5%
- GPU: 3.98%
- WiFi (señal): 64.16%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
