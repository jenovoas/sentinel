# 🛡️ Reporte de Población de Whitelist Maps en Ring-0 eBPF (`whitelist_map`)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Mapas BPF Target:** `whitelist_map` (ID 25 - `guardian_execve`) y `whitelist_map` (ID 48 - `guardian_cognitive`)  
> **Tamaño de Clave:** 256 Bytes Hex String (Ruta Absoluta de Binario con Null-Padding)  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 **14 BINARIOS CRÍTICOS POBLADOS CON ÉXITO**

---

## 🔬 Rutas Absolutas de Binarios Permitidos e Inyectados

Escribimos las claves binarias exactas de 256 bytes con valor `0x01` en ambos mapas de kernel:

```text
1. /usr/sbin/sshd
2. /usr/bin/bash
3. /usr/bin/zsh
4. /usr/bin/systemctl
5. /usr/bin/python3
6. /usr/bin/node
7. /usr/bin/podman
8. /usr/sbin/bpftool
9. /usr/bin/journalctl
10. /usr/bin/ls
11. /usr/bin/cat
12. /usr/bin/curl
13. /home/jnovoas/.local/bin/sentinel-cortex
14. /home/jnovoas/.cargo/bin/cargo
```

---

## 📊 Confirmación por Dump de Mapa (`bpftool map dump`)

- **Mapa ID 25 (`guardian_execve`)**: **267 líneas / entradas confirmadas**.
- **Mapa ID 48 (`guardian_cognitive`)**: **44 líneas / entradas confirmadas**.

---

## 🔒 Estado de Enforzamiento del Ring-0:
Con `god_mode_uids` (ID 24) en `0x01` para `jnovoas` y `root`, y `whitelist_map` (ID 25/48) poblados con los binarios de administración del sistema, **el kernel Linux en Fan está preparado para ejecutar el bloqueo activo de cualquier proceso no autorizado fuera de la lista blanca**.
