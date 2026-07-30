# 📋 Registro de Tareas Pendientes para Completar la Fase de Despliegue y Pruebas

> **Servidor Target:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026

---

## 🎯 1. Desplegar los Nuevos Objetos eBPF Recompilados con `BPF_MAP_TYPE_ARRAY` en Fan
- **Tarea**: Copiar el binario recién compilado `ebpf/guardian_alpha_lsm.o` (que contiene el mapa `ARRAY` corregido para `god_mode_uids`) hacia Fan y recargar el hook LSM en el kernel.
- **Objetivo**: Que el kernel utilice de forma permanente la estructura de arreglo contiguo $O(1)$ donde `UID 0` (`root`) y `UID 1001` (`jnovoas`) están inmutablemente protegidos sin basuras de memoria.

---

## 🛡️ 2. Ejecutar la Prueba de Enforzamiento del LSM en Ring-0 (Bloqueo Controlado)
- **Tarea**: Realizar la prueba de bloqueo 100% aislada:
  1. Registrar un PID de prueba en `alpha_ai_agents` (ID 28).
  2. Intentar ejecutar un binario no autorizado.
  3. Confirmar la denegación en el kernel (`-EACCES`) y la captura de la traza en Loki/Grafana.

---

## ⚡ 3. Ejecución de la Batería de Estrés y Rendimiento (Carga Concurrente)
- **Tarea**: Inyectar volumen de tráfico concurrente sobre `/api/v1/truth_claim` y `/metrics`.
- **Objetivo**:
  1. Registrar latencias de verificación (p95 y p99).
  2. Evaluar el comportamiento de difusión y estabilidad de la rejilla `LiquidLattice 3x3` (EXP-009) en Grafana (`http://10.88.0.1:3001`).
  3. Medir el consumo de RAM/CPU bajo carga pesada.

