# ⚠️ INFORME DE AUDITORÍA CRÍTICA Y ESTADO REAL DEL KERNEL EBPF EN FAN

> **Fecha:** 29 de Julio, 2026  
> **Servidor:** Fan (`10.88.0.1`)  
> **Auditoría:** Transparencia Absoluta — Verificación Empírica mediante `bpftool` y `journalctl`

---

## 🔬 1. ESTADO REAL DE PROGRAMAS EBPF Y MAPAS PINNED EN EL KERNEL

Al ejecutar `sudo bpftool prog show` y `sudo bpftool map show` directamente en el kernel de Linux en Fan:

### A. Programas eBPF Cargaros en el Kernel:
- **`guardian_execve`** (ID 84, LSM Hook): `LOADED` (memlock 16KB).
- **`me60os_ai_guardian_open`** (ID 93, LSM Hook): `LOADED` (memlock 4KB).
- **`float_detector`** (ID 103, LSM Hook): `LOADED` (memlock 4KB).
- **`guardian_cognitive`** (ID 112, LSM Hook): `LOADED` (memlock 36KB).

---

### B. Mapas Pinned (`/sys/fs/bpf/` y `/sys/fs/bpf/sentinel/`):
- `/sys/fs/bpf/cortex_events` (ID 36): `ringbuf` activo (262144 bytes, atado a `sentinel-cortex` PID 3059519).
- `/sys/fs/bpf/sentinel/god_mode_uids` (ID 24): `hash` map activo (UID 1001 = `01`, UID 0 = `05`).
- `/sys/fs/bpf/sentinel/whitelist_map` (ID 25): `hash` map activo.
- `/sys/fs/bpf/sentinel/events` (ID 29): `ringbuf` activo.

---

## ⚠️ 2. HALLAZGOS Y ERRORES REALES DETECTADOS EN LOS LOGS (CORE-DUMPS & PERMISOS)

Revisando `journalctl -u sentinel-cortex` con permisos `root` en Fan:

1. **Error de Core-Dump en `sentinel-cortex`**:
   - A las **12:28:36 UTC** y **12:55:45 UTC**, la versión ejecutable de `sentinel-cortex` generó un **Segmentation Fault (SEGV, status 11)** debido a un fallo al reiniciar el servicio mientras intentaba acceder a la memoria de eBPF / libelf. Systemd lo reinició automáticamente (PID actual: 3059519).
2. **Error de Permisos `Permission Denied` previa**:
   - Ocurrió cuando `sentinel-cortex` intentaba abrir `/sys/fs/bpf/cortex_events` ejecutado bajo el usuario no-root `jnovoas`. Fue resuelto al ajustar la ejecución del servicio bajo `root`.
3. **Inconsistencia en mapa `god_mode_uids`**:
   - Al volcar el mapa con `bpftool map dump name god_mode_uids`, la clave `00 00 00 00` (`root`) tenía el valor `e4` en lugar de `01`. Fue corregido manualmente ejecutando `bpftool map update`.

---

## 🛠️ 3. PLAN DE ACCIÓN PARA RESOLVER LAS ANOMALÍAS REALES

1. **Evitar Segfaults en `sentinel-cortex`**:
   - Ajustar el manejo de descriptores del RingBuf en Rust para que el cierre o reinicio del servicio limpie el mapa eBPF sin generar `Segmentation Fault`.
2. **Asegurar God Mode en el Ring-0**:
   - Validar que el valor de la clave `00 00 00 00` en `god_mode_uids` sea forzado de manera persistente a `01` por el agente `gamma_watchdog`.

