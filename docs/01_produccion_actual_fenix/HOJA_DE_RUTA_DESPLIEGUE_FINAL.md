# 🗺️ Hoja de Ruta Final de Despliegue y Validación (Sentinel Master Plan v3.0)

> **Servidor Target:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026

---

## 📋 1. Despliegue del Nuevo Objeto eBPF `ARRAY` en Fan

Reemplazar los objetos eBPF compilados con el nuevo mapa de tipo `ARRAY` para `god_mode_uids` en Fan:
- Copiar `ebpf/guardian_alpha_lsm.o` y `ebpf/ai_guardian.o` hacia Fan.
- Volver a cargar el programa LSM en Ring-0 usando el objeto con `BPF_MAP_TYPE_ARRAY` corregido.
- Confirmar por `bpftool map dump` que `key 0` (`root`) y `key 1001` (`jnovoas`) permanecen fijos en `0x01` sin fluctuaciones ni colisiones.

---

## 🛡️ 2. Validación de Enforzamiento del LSM (Prueba de Bloqueo Controlado)

Probar el enforzamiento de Ring-0 en un entorno 100% aislado:
1. Crear un proceso/PID de prueba en userspace.
2. Registrar su PID en `alpha_ai_agents` (ID 28).
3. Intentar ejecutar un binario no presente en `whitelist_map` (ID 25) desde ese PID.
4. Confirmar que el kernel eBPF LSM retorna `-EACCES` (Permission denied) y registra la traza de bloqueo en `/var/log/sentinel/ebpf_trace.log` y Loki.

---

## 📊 3. Pruebas de Estrés y Telemetría Completa

Con la capa de seguridad eBPF cargada y enforzando:
1. Inyectar tráfico sobre los 7 servicios systemd.
2. Medir latencia de verficación (p95/p99) en `/api/v1/truth_claim`.
3. Observar la curva de retención de `LiquidLattice 3x3` (EXP-009) y el consumo de CPU/RAM en Grafana (`http://10.88.0.1:3001`).

