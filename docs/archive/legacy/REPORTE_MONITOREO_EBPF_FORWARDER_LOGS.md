# 📊 Integración de Monitoreo de Trazas eBPF (`sentinel-ebpf-forwarder.service`)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Servicio:** `sentinel-ebpf-forwarder.service` (`PID 1533` - `bpftool prog tracelog`)  
> **Uptime:** 11 Horas | **RAM:** 142.5 MB  
> **Archivo de Destino:** `/var/log/sentinel/ebpf_trace.log`  
> **Loki Query:** `{job="sentinel_file_logs", filename="/var/log/sentinel/ebpf_trace.log"}`  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Análisis de Operación del eBPF Forwarder

El servicio **`sentinel-ebpf-forwarder.service`** ejecuta de manera continua `/usr/sbin/bpftool prog tracelog` para redirigir las trazas de bajo nivel emitidas por los hooks eBPF en el Ring-0 (`bpf_trace_printk`, `FloatDetector`, `guardian_execve`) hacia el archivo `/var/log/sentinel/ebpf_trace.log`.

### Trazas Verificadas en Vivo:
```text
<...>-3069209 [002] ...11 40094.391224: bpf_trace_printk: FloatDetector [UNKNOWN]: /bin/zsh (pid=3069209)
<...>-3069209 [002] ...11 40094.392927: bpf_trace_printk: FloatDetector [UNKNOWN]: /usr/bin/cat (pid=3069209)
(kery-api)-3069211 [003] ...11 40097.284036: bpf_trace_printk: FloatDetector [UNKNOWN]: /home/jnovoas/laespiguita_web/services/target/release/bakery-api (pid=3069211)
```

---

## 📈 2. Integración al Dashboard de Grafana

Actualizamos el Dashboard Maestro (`http://10.88.0.1:3001/d/ap295k/69db56b`) agregando el panel dedicado:
- **Panel 7**: `Ring-0 Kernel eBPF Syscall Trace Stream (ebpf-forwarder)`
- **Fuente**: Loki 3.4
- **Propósito**: Stream visual en directo de cada llamada a sistema e intercepción eBPF acoplada a las pruebas de carga y estrés.
