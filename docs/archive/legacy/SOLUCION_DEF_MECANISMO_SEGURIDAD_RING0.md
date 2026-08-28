# 🔬 Solución Definitiva y Diseño del Mecanismo de Seguridad Ring-0
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Componentes:** `guardian_alpha_lsm.c`, `ai_guardian.c`, `god_mode_uids` (Map ID 24)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Análisis Técnico de la Arquitectura de Seguridad (C/eBPF)

Al inspeccionar el código C nativo de los programas eBPF LSM ([`guardian_alpha_lsm.c:L103`](file:///home/jnovoas/Proyectos/sentinel/ebpf/guardian_alpha_lsm.c#L103-L112) y [`ai_guardian.c:L141`](file:///home/jnovoas/Proyectos/sentinel/ebpf/ai_guardian.c#L141-L150)):

```c
/* 0. God mode: UIDs divinos pasan sin restricción */
god = bpf_map_lookup_elem(&god_mode_uids, &uid);
if (god && *god == 1)
    return 0;

/* 1. Passthrough para procesos no-AI */
is_ai = bpf_map_lookup_elem(&alpha_ai_agents, &pid);
if (!is_ai || *is_ai == 0)
    return 0;
```

### 💡 Hallazgo Clave del Diseño LSM:
El hook LSM eBPF implementa un **Doble Filtro de Seguridad Exento por Defecto**:
1. **Comprobación 0 (`God Mode`)**: Si el UID está registrado en `god_mode_uids` con el valor `1` (`root` o `jnovoas`), el kernel autoriza el passthrough inmediato (`return 0`).
2. **Comprobación 1 (`AI Agent Filter`)**: Si el proceso **NO está explícitamente registrado** en el mapa `alpha_ai_agents` (ID 28) o `ai_agents_map` (ID 34), el kernel **autoriza el passthrough inmediato (`return 0`)**.

El LSM **ÚNICAMENTE evalúa y aplica restricciones o bloqueos contra un PID si dicho PID ha sido marcado activamente como un agente AI en `alpha_ai_agents`**. Los procesos normales de sistema (`sshd`, `bash`, `python3`, `bakery-api`, `systemd`) operan con passthrough nativo por no ser PIDs declarados como AI.

---

## 🛡️ 2. Propuesta de Solución Definitiva para la Estabilidad de `god_mode_uids`

Para garantizar que el mapa `god_mode_uids` se mantenga invulnerable y libre de cualquier rotación de tokens que realice `gamma_watchdog`:

1. **Inmunidad Fija en `god_mode_uids` vía Daemon Systemd de Mantenimiento**:
   - Crear `/usr/local/bin/sentinel-godmode-daemon.sh` corriendo en un bucle ligero de baja prioridad que reaplique `bpftool map update pinned /sys/fs/bpf/sentinel/god_mode_uids key hex 00 00 00 00 value hex 01` (UID 0) y `key hex e9 03 00 00 value hex 01` (UID 1001) para asegurar que el Passthrough esté forzado en un 100% del tiempo.
2. **Habilitación Segura del Enforzamiento AI**:
   - Registrar explícitamente solo los PIDs/procesos AI de prueba en `alpha_ai_agents` para validar el bloqueo eBPF de Ring-0 sin poner en riesgo ningún binario de administración o de clientes web.
