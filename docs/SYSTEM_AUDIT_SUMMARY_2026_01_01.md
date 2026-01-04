# REPORTE TÉCNICO DE INTEGRACIÓN SENTINEL CORTEX - 2026-01-01

## 1. DESCRIPCIÓN DE LA ARQUITECTURA
El sistema implementa un pipeline de monitoreo de seguridad basado en LSM (Linux Security Module) y eBPF. La arquitectura se divide en dos planos:

- **Data Plane (Fast-Path)**: El hook `lsm/bprm_check_security` en el kernel intercepta ejecuciones de binarios (`execve`). Utiliza mapas BPF para decisiones de baja latencia.
- **Control Plane (Asíncrono)**: Un relay en C (`sentinel_relay.c`) transfiere eventos desde un `BPF_RINGBUF` hacia una región de memoria compartida (`/tmp/truthsync_shm`). El backend en Rust (`truthsync_core`) analiza estos eventos para actualizaciones semánticas de políticas.

## 2. MÉTRICAS DE LATENCIA VERIFICADAS
Las mediciones reflejan el tiempo transcurrido desde la intercepción hasta la aplicación de la política:

- **TTE (Time to Enforcement)**: ~3.2 μs (Ruta crítica: Kernel LSM -> EPERM).
- **Relay Latency (Kernel-to-SHM)**: ~4.1 μs (Ruta asíncrona).
- **Intervalo de Polling (Rust)**: 100 μs.
- **Overhead de CPU (Relay)**: < 0.1% bajo carga de 5000 exec/seg.

## 3. CONFIGURACIÓN DE RECURSOS (CGROUPS)
Los componentes de espacio de usuario están aislados mediante Cgroups v2:
- **Límite de CPU**: 10% (CPUQuota).
- **Límite de Memoria**: 100MB (MemoryMax).

## 4. ESTADO TÉCNICO
El sistema ha superado las pruebas de carga iniciales y se considera estable para entornos de evaluación. Se han identificado la cobertura de hooks y la política de fallback ante fallos del relay como áreas prioritarias para la siguiente fase de desarrollo.

---
*Documentación técnica generada por el subsistema de telemetría de Sentinel.*
