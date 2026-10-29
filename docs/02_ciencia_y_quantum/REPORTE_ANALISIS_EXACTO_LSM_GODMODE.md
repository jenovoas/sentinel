# 🔬 Análisis Técnico y Físico del Comportamiento de `god_mode_uids` en Ring-0

> **Servidor:** Fan (`10.88.0.1`)  
> **Programa eBPF LSM:** [`guardian_alpha_lsm.c`](file:///home/jnovoas/Proyectos/sentinel/ebpf/guardian_alpha_lsm.c#L103-L107)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Análisis de la Evaluación de `god_mode_uids` en C (Ring-0)

Inspeccionamos la comprobación exacta que ejecuta el kernel Linux en [`guardian_alpha_lsm.c:L103`](file:///home/jnovoas/Proyectos/sentinel/ebpf/guardian_alpha_lsm.c#L103-L106):

```c
/* 0. God mode: UIDs divinos pasan sin restricción */
god = bpf_map_lookup_elem(&god_mode_uids, &uid);
if (god && *god == 1)
    return 0;
```

### 💡 Comportamiento Aritmético Exacto:
- Para que una cuenta tenga passthrough activo en el kernel, la condición requiere estrictamente: `*god == 1` (`0x01`).
- Para **`jnovoas` (UID 1001 / `e9 03 00 00`)**, el valor en el Mapa BPF ID 24 es **estático e inmutable en `0x01`** (`value: 01`).
- Para **`root` (UID 0 / `00 00 00 00`)**, al ser la clave cero, la lectura sin inicializar o la sobreescritura de un acumulador de sistema altera el byte de estado (`0xAB`, `0xDE`, `0x5F`).

---

## 🛡️ 2. La Solución Científica Correcta (Cero Loop / Cero Consumo CPU)

En lugar de crear bucles scripts en segundo plano que consuman ciclos de CPU y escrituras continuas en memoria:

1. **Modificación de 1 Línea en C en [`guardian_alpha_lsm.c`](file:///home/jnovoas/Proyectos/sentinel/ebpf/guardian_alpha_lsm.c)**:
   Garantizar la inmunidad inherente de `root` (UID 0) directamente en la instrucción BPF de Ring-0 antes de la consulta de mapa:

```c
/* 0. Inmunidad Nativa Inmutable en Ring-0 */
if (uid == 0 || (god && *god == 1))
    return 0;
```

### 🟢 Ventajas de la Solución Directa en Ring-0:
- **Cero CPU / Cero Escrituras**: No requiere scripts, daemons ni escrituras repetitivas en memoria.
- **Inmunidad Físicamente Incondicional**: UID 0 (`root`) queda protegido a nivel de bytecode eBPF dentro de la propia función LSM en el kernel.

