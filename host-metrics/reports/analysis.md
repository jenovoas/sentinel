
# Análisis de Métricas (Host)

- Muestras: 830
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-14T23:59:00.636Z

## Promedios
- CPU: 36.07%
- Memoria: 49.89%
- GPU: 5.8%
- WiFi (señal): 66.17%

## Alertas
Sin alertas en los umbrales configurados.

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
