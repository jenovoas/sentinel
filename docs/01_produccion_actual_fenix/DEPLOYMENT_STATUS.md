# DEPLOYMENT STATUS — Sentinel Infrastructure

> **Última actualización:** 2026-07-28
> **Despliegue integral:** Laptop (jnovoas) ↔ Fan (servidor remoto)
> **Arquitectura:** Red mesh batman-adv sobre WireGuard + VXLAN

---

## 1. 🟢 Estado General

| Capa | Componente | Estado | Notas |
|------|-----------|--------|-------|
| Red Mesh | WireGuard (wg0) | ✅ Activo | 10.88.0.2/24 (laptop) ↔ 10.88.0.1/24 (Fan) |
| Red Mesh | VXLAN (vxlan0) | ✅ Activo | VNI 42, MTU 1370 |
| Red Mesh | batman-adv (bat0) | ✅ Activo | 10.10.0.11/24 (laptop) ↔ 10.10.0.12/24 (Fan) |
| Red Mesh | mycnetd | ✅ Activo | Puerto 7474, local + SSH a Fan |
| eBPF Ring-0 | guardian_alpha_lsm | ✅ Cargado | LSM bprm_check_security, modo dios + whitelist |
| eBPF Ring-0 | ai_guardian | ✅ Cargado | LSM file_open + bprm_check_security |
| eBPF Ring-0 | float_detector | ✅ Cargado | LSM bprm_check_security, YATRA Lock |
| eBPF Ring-0 | guardian_cognitive | ✅ Cargado | LSM bprm_check_security, semántica |
| eBPF Ring-0 | burst_sensor (XDP) | ✅ Cargado | XDP, detección de ráfagas |
| eBPF Ring-0 | xdp_firewall_prog | ✅ Cargado | XDP firewall pre-stack |
| Cortex | sentinel-cortex API | ⚪ No activo | Binario compilado, systemd no instalado en laptop |
| Daemons | qhc_agent | ⚪ No activo | Binario compilado en me-60os |
| Daemons | adm_agent | ⚪ No activo | Binario compilado en me-60os |
| Daemons | pai_neural_daemon | ⚪ No activo | Binario compilado en me-60os |
| Daemons | vid_agent | ⚪ No activo | Binario compilado en me-60os |
| Observabilidad | node_exporter | 🔵 En Fan | Puerto 9100 |
| Observabilidad | Loki | 🔵 En Fan | Puerto 3100 |
| Observabilidad | Mimir | 🔵 En Fan | Puerto 8080/prometheus |
| Observabilidad | Grafana | 🔵 En Fan | Puerto 3001, admin/admin |
| Observabilidad | promtail | 🔵 En Fan | Shipping logs a Loki |
| Servicios Fan | PostgreSQL | ✅ En Fan | DB sentinel_db |
| Servicios Fan | Redis | ✅ Contenedor | Puerto 6379 |
| Servicios Fan | pinguinoseguro-web | 🔵 En Fan | Next.js, puerto 3000 |
| Systemd Fan | sentinel-cortex.service | 🔵 En Fan | API Cortex vía systemd |
| Systemd Fan | sentinel-ebpf-forwarder.service | 🔵 En Fan | eBPF tracelog → Loki |

**Leyenda:** ✅ Activo local | 🔵 Activo en remoto (Fan) | ⚪ Compilado/no activo | ❌ Error

---

## 2. 🌐 Infraestructura de Red (Mesh)

### 2.1 WireGuard (Capa 3)

| Nodo | Interfaz | IP | Ruta |
|------|---------|-----|------|
| Laptop | wg0 | 10.88.0.2/24 | MTU 1420 |
| Fan | wg0 | 10.88.0.1/24 | Punto remoto |

### 2.2 VXLAN (Capa 2 sobre WG)

| Propiedad | Valor |
|-----------|-------|
| Interfaz | vxlan0 |
| VNI | 42 |
| MTU | 1370 |
| Master | bat0 |

### 2.3 batman-adv (Capa 2 Mesh)

| Nodo | IP Mesh | MAC |
|------|---------|-----|
| Laptop | 10.10.0.11/24 | 32:ce:50:f7:f3:c1 |
| Fan | 10.10.0.12/24 | — |

### 2.4 MycNet Daemon

- **Binario:** `/home/jnovoas/Proyectos/mycnet/target/release/mycnetd`
- **API:** `http://0.0.0.0:7474`
- **Procesos activos:**
  - Local: PID `456483`, escuchando en :7474
  - Remoto (Fan): via SSH `ssh fan ... /home/jnovoas/.local/bin/mycnetd` con `MYCNET_BAT_IP=10.10.0.12`
- **Config Prometheus:** `config/prometheus.yml` scrape target `host.docker.internal:7474`

---

## 3. ⚛️ eBPF Ring-0

### 3.1 Programas Cargados

| # | Nombre | Tipo | PID | Tamaño (xlated) | Mapas | Cargado |
|---|--------|------|-----|-----------------|-------|---------|
| 335 | `guardian_execve` | LSM | bprm_check_security | 13,488B | 38,37,39,41 | 03:47 |
| 344 | `ai_guardian_open` | LSM | file_open | 752B | 44,45,46,48 | 03:47 |
| 354 | `me60os_ai_guardian_open` | LSM | file_open | 1,696B | 51,52,53,56,54 | 03:47 |
| 364 | `guardian_cognitive` | LSM | bprm_check_security | 33,376B | 60,59,63 | 03:47 |
| 373 | `float_detector` | LSM | bprm_check_security | 2,208B | 67,68,70,66 | 03:47 |
| 380 | `xdp_firewall_prog` | XDP | — | — | — | 03:47 |
| 868 | `detect_burst` | XDP | — | 576B | 237,238,239 | 19:53 |

### 3.2 Mapas Pineados en `/sys/fs/bpf/`

```
/sys/fs/bpf/
├── ai_guardian               # Mapas de ai_guardian
├── ai_guardian_link          # Enlace del programa
├── burst_sensor              # Mapas del burst sensor
├── crun/                     # Container runtime
├── float_detector            # Mapas de float_detector
├── float_detector_link
├── gamma_heartbeat           # Heartbeat de gamma
├── guardian_alpha_lsm        # Mapas de guardian_alpha
├── guardian_cognitive        # Mapas de cognitive
├── guardian_cognitive_link
├── guardian_link
├── ip -> /sys/fs/bpf/tc/     # Enlace simbólico a tc
├── known_peer_prog_ids
├── lsm_ai_guardian           # Mapas LSM
├── lsm_ai_guardian_link
├── sentinel/                 # Subdirectorio Sentinel
│   └── gamma/                # Mapas gamma
├── tc/                       # Traffic control
└── xdp -> /sys/fs/bpf/tc/    # Enlace simbólico
```

### 3.3 Modo Dios y Whitelists

| Mapa | Tipo | Capacidad | Propósito |
|------|------|-----------|-----------|
| `god_mode_uids` | HASH | 32 | UID 1000 (jnovoas) exento |
| `whitelist_map` | HASH | 10,000 | ~39 bins whitelisteados |
| `ai_whitelist_map` | HASH | 10,000 | ~28 bins AI whitelist |
| `ai_agents_map` | HASH | 1,024 | PIDs de AI agents |
| `alpha_ai_agents` | HASH | 1,024 | PIDs de AI agents (Alpha) |
| `cognitive_ai_agents` | HASH | 1,024 | PIDs (Cognitive) |
| `events` | RINGBUF | 256KB | Eventos → userspace |
| `burst_events` | RINGBUF | 256KB | Eventos burst → userspace |

---

## 4. 🧠 Sentinel Cortex API

- **Puerto:** 8000 (Axum)
- **Rutas:**
  - `GET /health` — Health check + resonancia
  - `GET /api/v1/telemetry` — WebSocket, stream de eventos eBPF
  - `GET /api/v1/sentinel_status` — Estado del ring
  - `POST /api/v1/truth_claim` — Verificación de claims de AI
- **Estado:** Binario compilado (`/home/jnovoas/Proyectos/sentinel/target/release/sentinel-cortex`)
- **Echo Bridge:** eBPF events → `broadcast::channel` → LatticeProcessor (64 nodos)
- **ResonantLatticeBridge:** 64 nodos acoplados, inyección de entropía por PID

### 4.1 Systemd (Fuente, no instalado en laptop)

| Servicio | Archivo | Destino |
|----------|---------|---------|
| sentinel-cortex.service | `systemd/sentinel-cortex.service` | Fan |
| sentinel-ebpf-forwarder.service | `systemd/sentinel-ebpf-forwarder.service` | Fan |
| sentinel-qhc-agent.service | `systemd/sentinel-qhc-agent.service` | Fan |

---

## 5. 🔧 Daemons me-60os

| Daemon | Binario | Propósito |
|--------|---------|-----------|
| `qhc_agent` | `me-60os/target/release/qhc_agent` | Phase Harmonic Driver, patrón YHWH 10-5-6-5 |
| `adm_agent` | `me-60os/target/release/adm_agent` | Axial Diffusion Model, lectura batctl, coherencia mesh |
| `pai_neural_daemon` | `me-60os/target/release/pai_neural_daemon` | Neural Memory, lee ring buffer de guardian |
| `vid_agent` | `me-60os/target/release/vid_agent` | Cooling Agent |

**Estado:** Binarios compilados. No ejecutándose en laptop (systemd no instalado).

---

## 6. 📊 Observabilidad

### 6.1 Stack en Fan

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| node_exporter | 9100 | Métricas de sistema |
| Loki | 3100 | Agregación de logs |
| Mimir | 8080 | Almacenamiento métricas (compatible Prometheus) |
| Grafana | 3001 | Dashboards (admin/admin) |
| promtail | — | Forwarder de logs → Loki |

### 6.2 Grafana Dashboard

- **Nombre:** "SecurePenguin — Monitoreo" (creado)
- **Datasources:** Loki (logs) + Mimir (métricas)
- **Swarm Dashboard:** `docs/swarm_dashboard_grafana.json`
  - Tareas pendientes/en ejecución/completadas
- **Coherencia del Cristal:** Gauge 0-1
- **Fase del Cristal:** YOD/HE/VAV/HE_2
- **Tick del Cristal:** Serie temporal

---

## 7. 📁 Rutas Clave

| Ruta | Propósito |
|------|-----------|
| `/home/jnovoas/Proyectos/sentinel/` | Proyecto principal |
| `/home/jnovoas/Proyectos/sentinel/ebpf/` | Código fuente eBPF (C) |
| `/home/jnovoas/Proyectos/sentinel/sentinel-cortex/` | Cortex API (Rust/Axum) |
| `/home/jnovoas/Proyectos/sentinel/systemd/` | Archivos .service |
| `/home/jnovoas/Proyectos/sentinel/scripts/` | Scripts de mantenimiento |
| `/home/jnovoas/Proyectos/me-60os/` | Core me-60os + daemons |
| `/home/jnovoas/Proyectos/mycnet/` | MycNet daemon |
| `/sys/fs/bpf/` | Mapas eBPF pineados |
| `/var/log/sentinel/` | Logs (Fan) |
| `/home/jnovoas/.local/bin/` | Binarios desplegados (Fan) |

---

## 8. ⚠️ Observaciones

1. **Cortex API no corre en laptop** — el systemd no está instalado. El binario existe pero no se ejecuta.
2. **Daemons me-60os compilados pero no activos** — qhc_agent, adm_agent, pai_neural_daemon, vid_agent necesitan systemd enable + start.
3. **Observabilidad solo en Fan** — Loki, Mimir, Grafana, promtail no están en laptop.
4. **eBPF forwarder no activo en laptop** — el servicio systemd existe pero no está instalado.
5. Esta sección refleja un inventario histórico de Laptop/Fan fechado en el encabezado; no describe el estado operativo actual de Fenix.

---

## 9. Incidente Firewalld / backend en Fenix — 2026-10-30

### Causa

Al iniciar Firewalld en Fenix, el backend de Sentinel dejó de alcanzar PostgreSQL por TCP en la red Docker interna. PostgreSQL y Redis estaban saludables; el backend respondía, pero `/api/v1/health` devolvía HTTP 503 porque fallaba el chequeo de PostgreSQL. La red `sentinel_internal` usaba el bridge `br-cbd16f207701`, que no tenía zona Firewalld asignada; la política de forwarding lo bloqueaba.

### Cambio aplicado

Se creó y persistió la zona dedicada `sentinel-bridge`, asociada únicamente a `br-cbd16f207701`, con `target=DROP`, `forward=yes` y sin servicios ni puertos. No se modificó Compose ni el código del backend, no se reiniciaron contenedores y no se tocaron las políticas nftables DMZ de Hercules/Ocean.

### Verificación y estado

- `firewall-cmd --check-config` pasó y Firewalld se recargó correctamente.
- El backend volvió a conectar por TCP con PostgreSQL; `/api/v1/health` respondió HTTP 200, PostgreSQL y Redis reportaron healthy, y Redis devolvió `PONG`.
- `sentinel-backend` quedó `running/healthy`; Docker permaneció activo con 12 contenedores.
- Se abrió una nueva sesión SSH a Fenix por TCP 4222 tras la recarga.
- El bridge observado es `br-cbd16f207701`; si Docker recrea la red con otro nombre de interfaz, habrá que revisar que la asignación de zona siga cubriendo el bridge real.

### Nota sobre Marte

Los errores `No route to host` observados en intentos del wrapper `clip-ssh` describen esos intentos, no el acceso del usuario. Jaime indicó que estaba conectado a Marte y que el nodo usa Firewalld. No se debe inferir falta de acceso del usuario a partir de los errores del wrapper; la configuración actual de Marte queda pendiente de verificación directa en una sesión válida.

## Cierre de TCP 22 por nodo — 2026-10-30

La instrucción operativa es cerrar TCP 22 únicamente en nodos cuyo SSH efectivo y listener hayan confirmado TCP 4222; la Laptop no debe bloquear cambios por nodo en otros equipos. Verificación en vivo desde esta sesión: Fenix, Kingu, Hercules y Ocean usan `sshd`/listener 4222 y no escuchan en 22. Fenix Firewalld y las políticas Firewalld de Hercules, además del nftables activo de Ocean, no permiten TCP 22; no se modificaron. En Kingu, `wg0` estaba en zona `trusted` con aceptación general, así que se añadió una regla Firewalld `drop` para TCP 22 en runtime y permanente; comprobado `RUNTIME=yes`, `PERMANENT=yes`, SSH 4222 sigue escuchando. No se reinició el nodo ni se cargó nftables manualmente.

La Laptop `ifenix` inicialmente confirmó SSH efectivo y listener solo en 22, así que no se cambió entonces. Jaime informó después que migró los puertos; por `10.88.0.3:4222` se confirmó kernel 7.3, `sshd` y listener únicamente en 4222, Firewalld activo y `wg0` en zona `trusted`. Se agregó una regla Firewalld `drop` de TCP 22 en runtime y permanente; ambas consultas devolvieron `yes` y 4222 siguió escuchando. No hubo reinicio. Jaime confirma acceso a Marte y pidió usar sus IP WireGuard; los intentos de esta sesión a `10.88.0.6:4222` desde Fenix, Kingu, Hercules y Ocean no llegaron (`No route to host`). Ese resultado es límite de esos intentos, no evidencia de falta de acceso de Jaime. No se cambió Marte; el estado actual de sus puertos y firewall queda sin verificación directa en esta sesión.

## Alias SSH VPN en los nodos — 2026-10-30

Se verificó la resolución efectiva (`ssh -G`) de `marte` (`10.88.0.6:4222`) y `laptop`/`ifenix` (`10.88.0.3:4222`) en la configuración local de Laptop y remotamente en Fenix, Kingu, Hercules y Ocean. Fenix y Kingu ya tenían esos alias; se agregaron los bloques faltantes a `~/.ssh/config` de Hercules y Ocean. Se comprobó conexión real desde Fenix al alias `laptop`: respondió `ifenix`, kernel `7.3.0-ifenix`, listener en 4222 y ninguno en 22. Firewalld confirmó la regla TCP 22 `drop` tanto runtime como permanente. Una ejecución de `sshd -T` sin privilegios reportó que no había host keys disponibles; no se usa como evidencia de configuración efectiva. Marte no se pudo modificar ni verificar desde esta sesión: `10.88.0.6:4222` respondió `No route to host`. No se cambiaron firewalls ni se reinició ningún nodo.
