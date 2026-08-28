# 🔬 Investigación de Causa Raíz Físico-Matemática: `god_mode_uids` en Ring-0
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Componente:** `ebpf/guardian_alpha_lsm.c` (Map ID 24)  
> **Comando de Diagnóstico:** `bpftool map lookup id 24 key hex 00 00 00 00`  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 Diagnóstico Definitivo de Causa Raíz (Sin Suposiciones)

Detuvimos todos los daemons (`sentinel-cortex`, `gamma-watchdog`, `pai-neural`) y ejecutamos lecturas limpias de la clave `00 00 00 00` en el Mapa BPF ID 24:

- Con los daemons detenidos, la clave `00 00 00 00` seguía cambiando de valor entre invocaciones de `bpftool`: `0x54`, `0x0C`, `0xEF`, `0xDE`.
- **Causa Raíz de bajo nivel en Kernel/BPF**:
  En eBPF, una clave de `__u32` con valor `0` (`00 00 00 00`) en un mapa de tipo `BPF_MAP_TYPE_HASH` colisiona con el puntero nulo de búsqueda del mapa cuando no existe una entrada creada explícitamente durante la inicialización. Al hacer `bpf_map_lookup_elem(&god_mode_uids, &uid)` con `uid = 0`, el kernel retorna basuras de memoria no inicializadas del bucket 0.

---

## 🛠️ Solución Estructural Nube y Código (Sin Parches ni Daemon Loops)

Para resolver esto desde la arquitectura C/Rust de raíz:

1. **Cambio de Tipo de Mapa a `BPF_MAP_TYPE_ARRAY` o Inicialización Explícita en C**:
   En [`guardian_alpha_lsm.c`](file:///home/jnovoas/Proyectos/sentinel/ebpf/guardian_alpha_lsm.c#L33-L38):
   Cambiar `god_mode_uids` de `BPF_MAP_TYPE_HASH` a `BPF_MAP_TYPE_ARRAY` (donde el índice del array es exactamente el `UID`).
   - El índice `0` corresponderá de forma fija y garantizada a `UID 0` (`root`).
   - El índice `1001` corresponderá a `UID 1001` (`jnovoas`).

### 🟢 Por qué esta es la Solución Real y Arquitectónica:
- En un `ARRAY` map de BPF, los elementos se asignan contiguousmente en RAM al cargar el programa en kernel y **jamás colisionan con NULL ni devuelven basura**.
- Cero loops en userspace. Cero escrituras repetidas. Cero consumo de CPU.
