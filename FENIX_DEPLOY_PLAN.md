# 🚀 FENIX DEPLOY PLAN — Stack Unificado Sentinel (Rust)

**Última actualización**: 18 de marzo de 2026  
**Estado**: PRODUCCIÓN — Stack Rust operativo en Ring 0

---

## MISIÓN

Desplegar el stack unificado de Sentinel en el servidor **fenix** (Rocky Linux 9, GCloud, Podman). El núcleo del sistema es ahora el binario nativo **sentinel-cortex** (Rust), eliminando la dependencia histórica de FastAPI/Python para la orquestación crítica.

---

## ESTADO DE AUDITORÍA (RESUELTO)

### ✅ Sustitución de FastAPI
El backend legacy en Python ha sido eliminado. Toda la lógica de orquestación, API de telemetría y salud se gestiona ahora a través de **sentinel-cortex** con el servidor **Axum**.

### ✅ Optimización de Infraestructura
- **eBPF Guardian**: Integrado y activo en el kernel.
### 2. Servicios del Ecosistema

| Servicio | Puerto Interno | Dominio Externo |
| :--- | :--- | :--- |
| **Cortex™ (Sentinel)** | 8000 | `sentinel.pinguinoseguro.cl` |
| **Pinguino Web** | 3000 | `pinguinoseguro.cl` |
| **La Espiguita (Web)** | 80 | `laespiguita.pinguinoseguro.cl` |
| **La Espiguita (API)** | 3000 | `api-espiguita.pinguinoseguro.cl` |
| **Grafana** | 3000 | `grafana.pinguinoseguro.cl` |
| **Prometheus** | 9090 | `prometheus.pinguinoseguro.cl` |

### 3. Flujo de Despliegue (CI/CD Local)
- **Traefik**: Labels configuradas para enrutamiento seguro a `sentinel.pinguinoseguro.cl`.
- **Exporters**: Prometheus configurado para monitorizar el Cortex nativo.

---

## 🚀 Despliegue en Fenix

### Paso 1 — Pre-condiciones
- [x] Red `proxy` de Podman existente.
- [x] Volúmenes de datos (`postgres_data`, `redis_data`, etc.) creados.

### 🌍 Topología Seleccionada
- **Nodo Maestro**: Fenix (`10.10.10.8`)
- **Acceso SSH**: `ssh -p 4222 jnovoas@10.10.10.8`
- **Red VPN (wg0)**: `10.100.0.1` (Gateway)
- **Runtime**: Podman rootless (Rocky Linux 9)

### Paso 2 — Levantamiento de Servicios
1. `podman-compose -f docker-compose.fenix.yml up -d postgres redis`
2. `podman-compose -f docker-compose.fenix.yml up -d cortex` (Binario Rust con loop de 17s).
3. `podman-compose -f docker-compose.fenix.yml up -d prometheus grafana n8n`

---

## REGLAS DE OPERACIÓN

- **Podman rootless**: Siempre ejecutar en el contexto del usuario `sentinel`.
- **Protocolo YATRA**: Cero uso de `floats` en el núcleo crítico.
- **Backup**: Respaldar volúmenes antes de cualquier actualización mayor.

---
**YATRA. Truth Resonates.**
