
# Análisis de Métricas (Host)

- Muestras: 1885
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-16T00:59:00.725Z

## Promedios
- CPU: 30.04%
- Memoria: 55.32%
- GPU: 4.32%
- WiFi (señal): 64.33%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
