# 🔬 Auditoría en Vivo de Ring-0 eBPF & LSM en Fan (`10.88.0.1`)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Comando de Verificación:** `bpftool prog show`, `bpftool map show`, `bpftool map dump`  
> **Fecha:** 29 de Julio, 2026

---

## 📊 1. Programas eBPF Cargas en Ring-0 (`bpftool prog show`)

Auditamos el kernel Linux de Fan y se constata la presencia activa de **4 programas eBPF LSM**:

| Prog ID | Tipo | Nombre | BTF ID | Memory Lock | Uptime / Carga |
|---------|------|--------|--------|-------------|----------------|
| **ID 84** | `lsm` | `guardian_execve` | 106 | 16,384 B | Cargado `2026-07-29T03:07:47Z` |
| **ID 93** | `lsm` | `me60os_ai_guardian_open` | 117 | 4,096 B | Cargado `2026-07-29T03:07:47Z` |
| **ID 103** | `lsm` | `float_detector` | 128 | 4,096 B | Cargado `2026-07-29T03:07:47Z` |
| **ID 112** | `lsm` | `guardian_cognitive` | 139 | 36,864 B | Cargado `2026-07-29T03:07:47Z` |

---

## 🗺️ 2. Mapas eBPF Pinned en BPF Filesystem (`/sys/fs/bpf/`)

Inspeccionamos `/sys/fs/bpf/` y `/sys/fs/bpf/sentinel/`:

- `/sys/fs/bpf/cortex_events` (ID 36): RingBuffer activo conectado a `sentinel-cortex` (PID 3066968) y `pai_neural_daemon` (PID 979342).
- `/sys/fs/bpf/sentinel/god_mode_uids` (ID 24): HASH Map con UIDs privilegiados.
- `/sys/fs/bpf/sentinel/whitelist_map` (ID 25): HASH Map de ejecuciones permitidas.

---

## 🚨 3. Hallazgo Crítico en la Populación de `god_mode_uids` (ID 24)

Al ejecutar `bpftool map dump id 24`, los datos reales leídos del kernel son:

```text
key: e9 03 00 00  value: 01   <-- UID 1001 (jnovoas) = 01 (PASSTHROUGH / GOD MODE OK)
key: 00 00 00 00  value: ef   <-- UID 0 (root) = 0xEF (¡NO ES 0x01 PASSTHROUGH!)
```

### 🛑 Diagnóstico de Seguridad Critical:
1. **UID 1001 (`jnovoas`)**: Está correctamente registrado como `0x01` (Modo Dios activo).
2. **UID 0 (`root`)**: Tiene el valor `0xEF` en lugar de `0x01`. Si activamos la lógica de enforzamiento estricto de bloqueo en Ring-0 con `root` en `0xEF`, **las tareas del sistema ejecutadas por root serían interceptadas y denegadas**, pudiendo bloquear procesos críticos o conexiones SSH administrativas.

---

## 🛠️ Plan de Alineación Obligatorio (Paso a Paso)

1. **Reparar la entrada de UID 0 (`root`) en `god_mode_uids`**: Actualizar la clave `00 00 00 00` con el valor exacto `01 00 00 00` (Passthrough / Dios).
2. **Poblar la Whitelist de Ejecución (`whitelist_map`)**: Cargar las rutas absolutas de binarios administrativos (`/usr/bin/sshd`, `/usr/bin/systemctl`, `/usr/bin/bash`, `/usr/bin/python3`, `/home/jnovoas/.local/bin/sentinel-cortex`) antes de conmutar el LSM a modo enforzamiento.
3. **Re-conectar y graficar la tasa de intercepción LSM en Grafana**: Agregar la métrica eBPF real al dashboard.
