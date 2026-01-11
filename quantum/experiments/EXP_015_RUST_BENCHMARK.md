# 🔬 REPORTE EXPERIMENTAL: EXP-015 RUST BENCHMARK
**Fecha:** 2026-01-10
**Estado:** ✅ ÉXITO (HYPER-SCALE ACHIEVED)

---

## 1. Objetivo
Validar la eficiencia de la implementación en **Rust** (`sentinel_core`) frente a la versión optimizada en **Python**.

## 2. Resultados

| Métrica | Python (Sparse) | Rust (Native) | Mejora |
| :--- | :--- | :--- | :--- |
| **Memoria por Nodo** | ~377 Bytes | **16.00 Bytes** | **23.6x** 📉 |
| **Throughput** | ~0.04 M Nodos/s | **~120 M Nodos/s** | **~3000x** 🚀 |
| **Capacidad en 11GB** | ~0.4 GB | **~10 GB** | **25x** |

## 3. Análisis
- La estructura `packed` en Rust alinea perfectamente a 16 bytes.
- La ausencia de Garbage Collection y Overhead de Objetos permite usar la RAM casi exclusivamente para carga útil.
- La velocidad de inyección permite reconstruir la red completa (10GB) en segundos, facilitando estrategias de Paging agresivas.

## 4. Conclusión
El núcleo Rust está listo para producción. La siguiente etapa es implementar el sistema de Paging para superar el límite físico de la RAM.
