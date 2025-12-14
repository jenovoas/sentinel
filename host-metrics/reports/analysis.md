
# Análisis de Métricas (Host)

- Muestras: 12
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-14T01:59:00.250Z

## Promedios
- CPU: 14.75%
- Memoria: 61.36%
- GPU: 0.0%
- WiFi (señal): 58.5%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
