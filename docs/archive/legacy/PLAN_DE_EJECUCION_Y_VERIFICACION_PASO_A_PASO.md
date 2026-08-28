# 🗺️ Plan Maestro de Ejecución, Integración y Validación Empírica paso a paso
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Workspace Fuente:** `/home/jnovoas/Proyectos/sentinel`  
> **Fecha:** 29 de Julio, 2026  
> **Directiva:** Cero suposiciones. Inspección y prueba empírica antes de reportar éxito.

---

## 📌 Fase 1: Corrección de Nombres de Pins eBPF en `gamma-watchdog`

- **Acción**:
  - Modificar [`ebpf/gamma_watchdog.c`](file:///home/jnovoas/Proyectos/sentinel/ebpf/gamma_watchdog.c#L44-L50) para alinear las cadenas de búsqueda `PEERS[]` con los nombres exactos de los archivos pineados en `/sys/fs/bpf/` (`guardian_alpha` y `ai_guardian`).
  - Compilar `gamma_watchdog` nativamente y reemplazar el ejecutable en Fan.
- **Verificación**:
  - Interrogar el log / mapa de heartbeats de `gamma_watchdog` para confirmar que reporta **5/5 peers activos**.

---

## 📌 Fase 2: Inyección de Entropía Dinámica Real (Inercia de CPU $S60$)

- **Acción**:
  - Eliminar el fallback constante `unwrap_or(45000)` en [`sentinel-cortex/src/main.rs`](file:///home/jnovoas/Proyectos/sentinel/sentinel-cortex/src/main.rs#L184).
  - Implementar la extracción de inercia computacional dinámica basada en el consumo real de deltatime de procesador (`/proc/stat` varianza de nanosegundos en Base-60 $S60$).
- **Verificación**:
  - Consultar `/metrics` en `sentinel-cortex` y verificar que la métrica `sentinel_cpu_temperature_celsius` o `sentinel_lattice_total_energy` fluctúa con la carga real de CPU y no permanece estática.

---

## 📌 Fase 3: Despliegue del Firewall XDP Pre-Stack (`ebpf/xdp_firewall.c`)

- **Acción**:
  - Compilar `ebpf/xdp_firewall.c` con `-target bpf` preservando BTF.
  - Adjuntar el bytecode a la interfaz de red `eth0` de Fan (`ip link set dev eth0 xdp obj xdp_firewall.o sec xdp`).
- **Verificación**:
  - Ejecutar `ip link show eth0` en Fan y confirmar la presencia de `prog/xdp id <ID>`.

---

## 📌 Fase 4: Enrutamiento Dual-Lane & Sanitización `AIOpsShield`

- **Acción**:
  - Activar la escritura directa append-only del **Security Lane** en `/var/log/sentinel/security_wal.log`.
  - Integrar la validación y sanitización de esquemas en `POST /api/v1/truth_claim` para bloquear inyecciones de `AIOpsDoom`.
- **Verificación**:
  - Enviar un claim de prueba malformado con inyección de prompt/comando y comprobar su bloqueo por el filtro `AIOpsShield` con registro directo en el WAL.

---

## 📌 Fase 5: Validación Batería de Carga e Inspección de Grafana

- **Acción**:
  - Ejecutar prueba de tráfico concurrente con las defensas activadas.
  - Monitorear `LiquidLattice` en Grafana y registrar el valor de `retention_score`.
