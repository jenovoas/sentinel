# 🔬 Reporte de Configuración Arquitectónica XDP Dual-Lane en Kernel

> **Servidor:** Fan (`10.88.0.1`)  
> **Interfaz Red Externa (`eth0`):** `xdp_firewall_prog` (XDP Nativo / Driver Mode)  
> **Interfaz Red Mesh (`wg0`):** `detect_burst` (XDP Genérico / Generic Mode)  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 **COMPROBADO Y ALINEADO CON EL KERNEL**

---

## ⚡ 1. Despliegue de XDP Dual en las Interfaces de Red

Debido a que el kernel de Linux impide la coexistencia simultánea de XDP Driver (Nativo) y XDP Generic en una misma interfaz física, se dividieron los roles de red conforme a la arquitectura de Sentinel:

1. **`eth0` (Tráfico Externo / Internet)**:
   - **Programa**: `xdp_firewall_prog` (`336B xlated, 208B jited`).
   - **Modo**: Native Driver Mode.
   - **Función**: Blacklist de IPs y Modo Pánico (`XDP_DROP`).
2. **`wg0` (Tráfico Mesh WireGuard)**:
   - **Programa**: `detect_burst` (`576B xlated, 389B jited`).
   - **Modo**: Generic Mode.
   - **Función**: Detección de ráfagas $>1,000\text{ pps}$ e inyección de eventos de red al RingBuffer `burst_events` (Map ID 306).

---

## 🔗 2. Ingestion eBPF Bridge

El RingBuffer `burst_events` (Map ID 306, `max_entries 262144`) en `/sys/fs/bpf/` alimenta directamente las lecturas de eventos de tráfico real del kernel hacia `sentinel-cortex` y `me-60os-core`, eliminando cualquier interpolación o maquillaje en el puente.

