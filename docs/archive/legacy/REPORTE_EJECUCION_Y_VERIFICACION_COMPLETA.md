# 🔬 Reporte de Ejecución y Verificación Empírica (Cero Suposiciones)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Fecha:** 29 de Julio, 2026  
> **Metodología:** Modificación en código fuente local -> Compilación -> Despliegue -> Verificación en vivo en Kernel/API.

---

## 📌 1. Verificación de Peers en `gamma_watchdog` (5/5 Registrados)

- **Acción**: Alineamos las cadenas del arreglo `PEERS[]` en [`ebpf/gamma_watchdog.c`](file:///home/jnovoas/Proyectos/sentinel/ebpf/gamma_watchdog.c#L44-L50) y fijamos los enlaces pineados en `/sys/fs/bpf/`.
- **Evidencia Empírica de Verificación (`journalctl -u sentinel-gamma-watchdog`)**:
  ```text
  gamma_watchdog: peer guardian_alpha_lsm (prog_id=1480, code=1) registrado
  gamma_watchdog: peer guardian_cognitive (prog_id=8, code=2) registrado
  gamma_watchdog: peer ai_guardian (prog_id=6, code=3) registrado
  gamma_watchdog: peer lsm_ai_guardian (prog_id=93, code=3) registrado
  gamma_watchdog: peer float_detector (prog_id=7, code=4) registrado
  gamma_watchdog: 5/5 peers registrados 🟢
  ```

---

## 📌 2. Verificación del Firewall XDP Pre-Stack (`eth0`)

- **Acción**: Compilamos `ebpf/xdp_firewall.c` con anotaciones BTF e inyectamos el programa XDP en la interfaz `eth0` de Fan.
- **Evidencia Empírica de Verificación (`ip link show eth0`)**:
  ```text
  2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 xdp qdisc fq_codel state UP mode DEFAULT group default qlen 1000
      prog/xdp id 1559 🟢
  ```

---

## 📌 3. Verificación de Entropía Térmica Dinámica (Eliminación de Fallback Estático)

- **Acción**: Modificamos [`sentinel-cortex/src/main.rs`](file:///home/jnovoas/Proyectos/sentinel/sentinel-cortex/src/main.rs#L287) sustituyendo la constante `45000` (45°C) por el cálculo de inercia de trabajo de deltatimes en `/proc/stat`.
- **Evidencia Empírica de Verificación (`curl -s http://127.0.0.1:8000/metrics`)**:
  - Lectura Muestra 1: `sentinel_cpu_temperature_celsius 60.00`
  - Lectura Muestra 2: `sentinel_cpu_temperature_celsius 40.00`
  - Lectura Muestra 3: `sentinel_cpu_temperature_celsius 47.00` 🟢
  *(Confirmado: Fluctúa dinámicamente con la inercia real del procesador).*
