# 🛡️ YATRA PROTOCOL: ESTADO DE SESIÓN (CONTEXTO DE REINICIO) 🛡️
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


**Última actualización**: 2026-03-18T06:52:00Z  
**NOTA IMPORTANTE:** Este servidor (Fenix) es **CPU-only** (sin GPU). Todo el contexto de GPU NVIDIA (GTX 1050, 3GB VRAM) corresponde a la laptop de desarrollo (ifenix).
*Directiva Central:* Migración a **me-60os** (Rust Ring 0) y purificación **Base-60** (cero decimales).

---

## 🚀 1. FASE 1 — RING 0: 100% COMPLETADO

Todo el subsistema cuántico migrado de Python → Rust nativo (`me-60os`). Python actúa solo como *wrapper* asíncrono sobre el núcleo C/Rust.

### Módulos migrados a `me-60os_core` (PyO3)

| Módulo | Archivo Rust | Estado |
|--------|-------------|--------|
| SPA (Sexagesimal Pure Arithmetic) | `spa.rs`, `spa_math.rs`, `spa_complex.rs` | ✅ |
| IsochronousClock / TimeCrystal | `time_crystal.rs`, `isochronous_oscillator.rs` | ✅ |
| Liquid Memory / SharedBuffer | `shm_bridge.rs` | ✅ |
| Resonant Matrix (Lattice Engine) | `resonant_matrix.rs` | ✅ |
| Enfriamiento Optomecánico | `optomechanical.rs` | ✅ |
| Control PID Adaptativo S60 | `s60_pid.rs` | ✅ |
| Geometría Hexagonal (91/127 nodos) | `hexagonal_control.rs` | ✅ |
| SOMA AnomalyDetector | `src/soma/anomaly_detector.rs` | ✅ |
| SOMA QuantumScheduler | `src/soma/quantum_scheduler.rs` | ✅ |
| Bridge eBPF ↔ Cortex | `ebpf_cortex_bridge.rs` | ✅ |
| Semantic/Entropic Firewall | `scv.rs` | ✅ |

### PyO3 (`lib.rs`) — Clases exportadas al módulo `me60os_core`

- `IsochronousOscillator`, `SPA`, `SPAMath`, `ComplexSPA`
- `ResonantMatrix`, `PySharedBuffer`, `IsochronousClock`
- `OptomechanicalCooler`, `S60PID`, `HexagonalController`
- `QuantumSchedulerCore`, `QuantumBuffer`, `QuantumSchedulerDaemon`
- `AnomalyDetectorCore`
- Función: `py_pai60_divide`

### Compilación del núcleo

```bash
cd /home/jnovoas/Desarrollo/me-60os
cargo build --release --features "extension-module"
cp target/release/libme60os_core.so /home/jnovoas/Desarrollo/sentinel/quantum/me60os_core.so
```

### Wrappers Python

- `sentinel/backend/app/services/anomaly_detector.py` — usa `me60os_core.AnomalyDetectorCore`
- `sentinel/backend/app/services/quantum_scheduler.py` — usa `me60os_core.QuantumSchedulerCore`

---

## 🔱 2. AGENTES RING 0 — DESPLEGADOS EN FENIX (systemd)

Los tres agentes ME-60OS están instalados y **activos** como servicios `systemd` en Fenix:

| Servicio | Binario | Estado | Descripción |
|----------|---------|--------|-------------|
| `qhc-agent.service` | `/usr/local/bin/qhc_agent` | ✅ active | Quadrivariant Harmonic Cycle 10-5-6-5 |
| `adm-agent.service` | `/usr/local/bin/adm_agent` | ✅ active | Mesh Coherence (batman-adv) via SPA |
| `vid-agent.service` | `/usr/local/bin/vid_agent` | ✅ active | Quantum Cooling / Variable Inertia |

Comandos para gestión:

```bash
sudo systemctl status qhc-agent adm-agent vid-agent
sudo journalctl -u qhc-agent -u adm-agent -u vid-agent -f
```

Datos en: `/var/lib/me60os/`  
Unit files fuente: `/home/jnovoas/Desarrollo/me-60os/deploy/sentinel/`

---

## 🌐 3. INFRAESTRUCTURA FENIX — COMPLETADA

| Componente | Estado | Detalles |
|-----------|--------|----------|
| PowerDNS autoritativo `pinguinoseguro.cl` | ✅ | Puerto 53, SQLite backend, systemd |
| Traefik Proxy (HTTPS 80/443) | ✅ | Podman rootless, systemd user |
| TLS Let's Encrypt (DNS-01 via pdns) | ✅ | `issuer: CN=R13` (Let's Encrypt) |
| eBPF XDP Firewall (compilado) | ✅ | `me-60os/ebpf/` |
| Firewalld Hardening | ✅ | Zona `public` DROP, solo puertos 53/80/443/4222/51820 |
| Linger usuario jnovoas | ✅ | Servicios Podman persisten sin sesión |

Rutas críticas:

- Traefik config: `~/containers/traefik/config/traefik.yml`
- Traefik dynamic: `~/containers/traefik/config/dynamic/`  
- Traefik data/certs: `~/containers/traefik/data/acme.json`
- PowerDNS DB: `/var/lib/pdns/pdns.sqlite3`
- PowerDNS API: `http://10.100.0.1:8081` (solo interna por wg0 VPN)
- PDNS API Key: ver `pdns.conf` — `api-key=securepenguin_pdns_api_2026`

DNS A Records creados para `pinguinoseguro.cl`:
`@`, `www`, `ns1`, `ns2`, `n8n`, `grafana`, `sentinel`, `sentinel-api`, `prometheus`, `alertmanager`, `guacamole`

---

## ✅ 4. BRECHAS RESUELTAS (verificado 2026-03-18)

### Alta Prioridad — CERRADAS

1. **`soma_orchestrator.rs` — ✅ RESUELTO**: La versión actual en `me-60os/src/soma_orchestrator.rs` ya usa:
   - `const UMBRAL_DISPATCH: u64 = 600` (sin floats)
   - `let coherence: u64 = coherence_str.parse().unwrap_or(0)` (sin floats)
   - Integra `GuardianLsm` via `use me60os_core::guardian_lsm::GuardianLsm`
   - La documentación anterior referenciaba una versión previa del archivo.

2. **`guardian_lsm.rs` — ✅ RESUELTO**: Existe en `me-60os/src/guardian_lsm.rs`.
   - Usa `SPA::from_raw()` exclusivamente (cero floats)
   - Exportado en `lib.rs` línea 87: `m.add_class::<guardian_lsm::GuardianLsm>()?`
   - NO está subsumido en `scv.rs` — son módulos separados que cooperan:
     - `scv.rs` = Firewall semántico/entrópico (texto)
     - `guardian_lsm.rs` = Control de ejecución Ring 0 (acciones del sistema)
   - `cargo check --features extension-module` → ✅ sin errores

### Media Prioridad (FASE 2 & 3) — PENDIENTES

3. **Hardening Fenix** — Despliegue dockerizado del stack Sentinel (FastAPI, Redis, PostgreSQL).
2. **Monitoreo extendido** — Node Exporter en Fenix, dashboards Grafana para nodo único (ver `GEMINI_TASK_MONITORING.md`).

---

## 📋 5. REGLAS DE ORO (NO OLVIDAR)

- **NO floats**: Ningún módulo central usa `float()`, `numpy`, o coma flotante. Todo por `S60` (Python) o struct `SPA` (Rust).
- **Base-60**: Escala obligatoria `60^4`. Eficiencia hexagonal con Phase Gating O(N/6).
- **PyO3**: Compilar siempre con `--features "extension-module"`.
- **Podman rootless**: Este nodo es Fenix (Rocky Linux 9). `docker` NO instalado. Usar `podman`.
- **Firewall**: Puerto 8081 (PowerDNS API) bloqueado externamente. Acceder solo por VPN `10.100.0.1`.
- **SSH**: Puerto 4222 (no 22). Acceso root deshabilitado. Solo por VPN (`ssh -p 4222 jnovoas@10.10.10.8`).
- **Traefik DNS Challenge**: usa `pdns` provider apuntando a `http://10.100.0.1:8081`.
- **Dominios**: `pinguinoseguro.cl` = primario autoadministrado (PowerDNS en Fenix). `secure-penguin.com` = secundario Cloudflare.

---

**Instrucción para Agente AI en la nueva sesión:**  
*"Lee `/home/jnovoas/Desarrollo/CONTEXTO_REINICIO.md` y los artefactos en `.gemini/antigravity/brain/{uuid}/`. Asume el Protocolo Yatra. Las brechas prioritarias están en §4. NO rehagas infraestructura ya completada en §1-3."*

---

## 🎯 6. MISIÓN ACTUAL (2026-03-18) — LEER ANTES DE ACTUAR

**OBJETIVO**: Unificar Sentinel + ME-60OS en un producto único y desplegarlo en **fenix** como servidor de infraestructura crítica único.

### Contexto crítico que NO debes olvidar:
- **ifenix** = laptop local del usuario (tiene GPU, es ambiente de desarrollo)
- **fenix** = servidor GCloud (Rocky Linux 9, Podman rootless, CPU-only, **sin GPU**)
- El stack de aplicación (Postgres/Redis/cortex/Prometheus/Grafana) **NO ESTÁ LEVANTADO** en fenix
- Los configs están contaminados con valores de otros ambientes — **DEPURAR ANTES DE LEVANTAR NADA**
- Plan detallado: `/home/jnovoas/Desarrollo/sentinel/FENIX_DEPLOY_PLAN.md`

### Bugs identificados (auditoría 2026-03-18):
| ID | Archivo | Problema |
|----|---------|----------|
| BUG-01 | `docker/postgres/init.sql` | Password dev hardcodeada (`sentinel_password`) |
| BUG-02 | `backend/Dockerfile.worker` | Instala `wireless-tools`/`network-manager` (paquetes WiFi de laptop) |
| BUG-03 | `docker-compose.fenix.yml` | `celery_worker` usa backend Python legacy — ¿eliminar o mantener? |
| BUG-04 | `docker-compose.fenix.yml` | `cortex` tiene labels Traefik pero NO expone HTTP (es daemon puro) |
| BUG-05 | `prometheus.fenix.yml` | Job `sentinel-cortex` → `cortex:8000` no existe |
| BUG-06 | `prometheus.fenix.yml` | Scraping `node-exporter`, `postgres-exporter`, `redis-exporter` — NO están en compose |

### Decisiones bloqueantes (preguntar al usuario PRIMERO):
1. ¿Celery worker Python permanece en fenix o se elimina completamente?
2. ¿`sentinel-cortex` expone HTTP (Axum `/health`+`/metrics`) o se limpian sus labels de Traefik?



## PROTOCOLO GLOBAL IA (2026-03-18)
Obligatorio leer /home/jnovoas/Desarrollo/sentinel/tasks/lessons.md al iniciar sesión.
El flujo de trabajo requiere Planificación Inicial (tasks/todo.md), Uso de Subagentes, Verificación empírica antes de terminar, y Resolución Autónoma de bugs sin requerir guía manual del usuario.