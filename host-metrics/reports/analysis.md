
# Análisis de Métricas (Host)

- Muestras: 1011
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-15T03:00:00.517Z

## Promedios
- CPU: 34.36%
- Memoria: 51.14%
- GPU: 5.34%
- WiFi (señal): 65.77%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
