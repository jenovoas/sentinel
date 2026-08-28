# ⚡ Registro de God Mode de Sistema (Exención de Filtros eBPF LSM)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 ACTIVO — Exención Cero-Bloqueo de Kernel

---

## 🏛️ Configuración de Inmunidad de Sistema (God Mode)

Para evitar que las reglas del LSM (`guardian_alpha_lsm.c`) o los filtros de seguridad de Sentinel boten, bloqueen o cierren conexiones de pruebas legítimas realizadas por el administrador:

### UIDs Privilegiados (Divinos):
1. **`UID 0` (`root`)**: Exento de veto o intercepción LSM (`god_mode_uids = 1`).
2. **`UID 1001` (`jnovoas`)**: Exento de veto o intercepción LSM (`god_mode_uids = 1`).

---

## ⚡ Funcionamiento en Kernel Ring-0

En el código fuente de eBPF LSM ([`guardian_alpha_lsm.c:L103-L106`](file:///home/jnovoas/Proyectos/sentinel/ebpf/guardian_alpha_lsm.c#L103-L106)):

```c
/* 0. God mode: UIDs divinos pasan sin restricción */
god = bpf_map_lookup_elem(&god_mode_uids, &uid);
if (god && *god == 1)
    return 0; // Passthrough inmediato sin evaluación de whitelist
```

### Script de Mantención de Inmunidad:
Se instaló `/usr/local/bin/sentinel-godmode` en el servidor **Fan** para mantener estos dos UIDs fijados en el mapa eBPF `/sys/fs/bpf/sentinel/god_mode_uids`.
