---
id: REPORTE_FUZZER_AIOPSDOOM_20261112
aliases: [Ejecución AIOpsDoom de 120 payloads]
tags:
  - sentinel
  - seguridad
  - fuzzer
updated: 2026-11-12
---

# Fuzzer AIOpsDoom — ejecución local de 120 payloads

## Cambios publicados

Sentinel `99a1635a` amplía `backend/fuzzer_aiopsdoom.py` de 40 a 120 entradas: 100 maliciosas repartidas entre cinco categorías y 20 benignas en una categoría propia. La importación del firewall ahora falla de forma explícita si faltan dependencias; ya no ejecuta un mock que pudiera producir métricas presentadas como evaluación real.

## Ejecución y resultado

Se ejecutó el fuzzer en proceso con CPython 3.14.9 gestionado por `uv`, que cargó `quantum/me60os_core.so`. `uv` resolvió `backend/requirements.txt` en un entorno efímero. El detector cargado fue AIOpsShield Semantic Firewall.

| Métrica | Resultado |
| --- | ---: |
| Entradas | 120 |
| Maliciosas / benignas | 100 / 20 |
| Verdaderos positivos / verdaderos negativos | 100 / 20 |
| Falsos positivos / falsos negativos | 0 / 0 |
| Accuracy / precision / recall / F1 | 100 % / 100 % / 100 % / 100 % |
| Latencia media / p95 / p99 | 0,13 ms / 0,16 ms / 0,19 ms |

La corrida previa sin las dependencias del backend cayó al mock y no se considera evidencia válida; el cambio fail-closed elimina esa ambigüedad.

## Alcance

Este resultado mide el firewall semántico en proceso contra este corpus determinista. No mide el endpoint HTTP, el Cortex desplegado ni una muestra externa de ataques; el 100 % no se generaliza fuera de estas 120 entradas y no demuestra un despliegue.
