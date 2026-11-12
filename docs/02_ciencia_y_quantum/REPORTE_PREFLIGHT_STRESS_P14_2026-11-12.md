---
id: REPORTE_PREFLIGHT_STRESS_P14_20261112
aliases: [Preflight P1.4 del Cortex en Fénix]
tags:
  - sentinel
  - rendimiento
  - preflight
updated: 2026-11-12
---

# P1.4 — Preparación segura del estrés HTTP en Fénix

## Estado observado

El preflight de solo lectura del 2026-11-12 encontró el Cortex en `10.88.0.1:8001`; `127.0.0.1:8000` respondió HTTP 404 a `GET /health`. El Cortex respondió `OK` en `:8001`, pero informó `scheduler_emergency_shutdown=true`, cola de 8269 y 471 tareas críticas. Una captura puntual de `docker stats` marcó 73,63 % CPU y 174,3 MiB de 512 MiB; no es una medida bajo carga. El entorno no tenía `CORTEX_AUTH_TOKEN`.

No se envió ningún POST ni se ejecutó la batería. El reporte histórico de Fan no representa este runtime en Fénix.

## Preparación publicada

- Sentinel `384f5624` cambia el destino por defecto de `scripts/stress_test_sentinel.py` a `http://10.88.0.1:8001`; `CORTEX_URL` permite otro destino.
- Sentinel `19df8fe0` agrega un preflight antes de la carga: exige un Bearer, verifica que `/health` esté `OK`, requiere que el campo `scheduler_emergency_shutdown` exista y esté inactivo, y valida el Bearer con un `GET /api/v1/sentinel_status` autenticado. Ese handler solo lee disponibilidad de mapas eBPF y energía del lattice. Los errores abortan antes de crear las peticiones de carga.
- No se han fijado umbrales para `scheduler_queue_len` ni `tasks_critical`; el preflight los informa, pero solo bloquea por el dead-man. El estado observado sí activa el bloqueo.

## Pendiente y límites

La batería sigue pendiente. Para ejecutarla se requiere un Bearer válido y que el preflight acepte el estado del Cortex; luego deben medirse p95/p99, estabilidad LiquidLattice y CPU/RAM. No se desplegó nada ni se probó el script tras estos cambios. El resultado futuro será del runtime de Fénix y no debe confundirse con la corrida histórica de Fan.
