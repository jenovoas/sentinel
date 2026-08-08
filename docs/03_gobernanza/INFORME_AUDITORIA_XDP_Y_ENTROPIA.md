# 🔬 Informe de Auditoría Crítica: Programa XDP y Fuente de Entropía Térmica en Fan

> **Servidor:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🚨 **2 INCONSISTENCIAS CRÍTICAS DETECTADAS**

---

## 🚨 1. Maquillaje de Entropía Térmica Identificado en `sentinel-cortex`

En [`sentinel-cortex/src/main.rs:L181-L184`](file:///home/jnovoas/Proyectos/sentinel/sentinel-cortex/src/main.rs#L181-L184):

```rust
let temp_millicelsius: i64 = std::fs::read_to_string("/sys/class/thermal/thermal_zone0/temp")
    .ok()
    .and_then(|s| s.trim().parse::<i64>().ok())
    .unwrap_or(45000); // fallback a 45C si la zona térmica no está expuesta
```

### 🔬 Evidencia Empírica en Fan:
- Ejecutamos `cat /sys/class/thermal/thermal_zone0/temp` en Fan y la ruta **NO EXISTE** (los VPS virtuales o instancias KVM no exponen `/sys/class/thermal`).
- **Consecuencia**: El código caía silenciosamente en el fallback estático `45000` (45°C). Por eso la métrica `sentinel_cpu_temperature_celsius` marcaba siempre **45.00 °C fijas y constantes**, falsificando la inyección de ruido térmico a la Lattice.

---

## 🚨 2. Programa eBPF XDP Inexistente en Ring-0 (`xdp_firewall.c`)

- La arquitectura global del proyecto define `xdp_firewall.c` / `burst_sensor.c` para filtrado pre-stack a nivel de interfaz de red (`eth0`).
- **Auditamos los hooks activos en la interfaz `eth0` de Fan (`ip link show eth0`)**:
  - `eth0` tiene únicamente el qdisc `fq_codel` sin ningún programa XDP adjunto (`xdp_firewall` NO está cargado).

---

## 🛠️ Plan de Reparación Obligatorio (Sin Maquillajes)

1. **Reparar la Fuente Real de Entropía en Fan**:
   - Reemplazar la lectura estática por una fuente de entropía real de kernel/CPU disponible en Fan (como la varianza de Jitter en microsegundos de `/proc/stat` o el generador de entropía de hardware del kernel `/proc/sys/kernel/random/entropy_avail` acoplado al tiempo exacto en nanosegundos).
2. **Compilar e Inyectar el Programa XDP Real (`ebpf/xdp_firewall.c`)**:
   - Compilar `xdp_firewall.c` y vincularlo directamente a la interfaz `eth0` mediante `ip link set dev eth0 xdp obj xdp_firewall.o sec xdp`.

