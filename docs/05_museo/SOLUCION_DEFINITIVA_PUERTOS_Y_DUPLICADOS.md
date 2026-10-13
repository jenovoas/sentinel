# 🧹 Diagnóstico y Solución Definitiva: Limpieza de Duplicados y Arquitectura de Puertos

> **Servidor:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 **LIMPIEZA Y ALINEACIÓN 100% COMPLETADA**

---

## 🔬 1. Diagnóstico de los Problemas Encontrados

1. **Duplicación de Contenedores (Rootless vs Root)**:
   - Existían dos entornos Podman paralelos: contenedores de usuario (`jnovoas`) antiguos e inactivos intentando colisionar con la pila oficial de producción administrada por `root`.
   - **Solución Aplicada**: Eliminación total y purga de los contenedores de usuario duplicados (`podman rm -f`). La pila oficial es administrada de forma única por `root` (`sentinel-grafana`, `sentinel-loki`, `sentinel-mimir`, `sentinel-redis`, `node_exporter`, `promtail`).

2. **Alineación Definitiva de Puertos sin Parches**:
   - `sentinel-grafana` en la pila oficial tiene fijada explícitamente la variable de entorno nativa **`GF_SERVER_HTTP_PORT=3001`**. Por este motivo, el puerto estándar donde escucha la instancia de producción es **`:3001`** (y no 3000 ni 3005).

---

## 🌐 2. Mapeo Oficial Unificado de Puertos en Producción

Todos los puertos han sido abiertos de manera permanente en el cortafuegos (`firewalld`) de **Fan**:

| Servicio / Componente | Contenedor / PID | Puerto Escuchando | Regla Firewall (`firewalld`) | Estado |
|-----------------------|-------------------|-------------------|------------------------------|--------|
| **Sentinel Grafana** | `sentinel-grafana` | **`:3001`** | `3001/tcp` (ALLOW) | 🟢 `Up 2+ Hours` |
| **Sentinel Loki** | `sentinel-loki` | **`:3100`** | `3100/tcp` (ALLOW) | 🟢 `Up 2+ Hours` |
| **Sentinel Cortex API** | `sentinel-cortex` (PID 3059519) | **`:8000`** | `8000/tcp` (ALLOW) | 🟢 `Active (running)` |
| **Sentinel Mimir** | `sentinel-mimir` | **`:8080`** | `8080/tcp` (ALLOW) | 🟢 `Up 2+ Hours` |
| **Node Exporter** | `node_exporter` | **`:9100`** | `9100/tcp` (ALLOW) | 🟢 `Up 2+ Hours` |
| **Sentinel Redis** | `sentinel-redis` | **`:6379`** | Inter-container | 🟢 `Up 2+ Hours` |

