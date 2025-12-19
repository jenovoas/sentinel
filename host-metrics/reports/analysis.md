
# Análisis de Métricas (Host)

- Muestras: 5759
- Rango: 2025-12-14T01:30:27.903492Z → 2025-12-19T16:59:00.399Z

## Promedios
- CPU: 257085.37%
- Memoria: 3148475.07%
- GPU: 3.94%
- WiFi (señal): 63.44%

## Alertas
- CPU promedio alto (>= 85.0%)
- Memoria promedio alta (>= 85.0%)

## Observaciones
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
