# 📊 Ajuste Fino de la Consulta Loki en Grafana para Trazas eBPF
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Loki Query Anterior:** `{job="sentinel_file_logs", filename=~"/var/log/sentinel/ebpf_trace.log"}`  
> **Loki Query Nueva (Alineada):** `{job="sentinel_file_logs"}`  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 Diagnóstico y Solución

1. **Causa del `No Data` en el Panel de Logs**:
   Promtail etiqueta los logs de `/var/log/sentinel/ebpf_trace.log` con el label estricto `job="sentinel_file_logs"`. El filtro redundante de nombre de archivo hacía que la expresión LogQL fallara si la ruta difería ligeramente en la sintaxis de regex de Grafana.
2. **Solución Implementada**:
   Simplificamos la expresión LogQL del Panel 7 a `{job="sentinel_file_logs"}`.

---

## 🟢 Verificación de Ingesta en Tiempo Real:
Al ejecutar la consulta desde la API de Loki:
```json
{"status":"success","data":{"resultType":"streams","result":[{"stream":{"filename":"/var/log/sentinel/ebpf_trace.log","job":"sentinel_file_logs"},"values":[["1785346931963270923","bpf_trace_printk: FloatDetector..."]]}]}}
```

El stream de trazas del kernel eBPF `ebpf-forwarder` se renderiza de inmediato en el Panel 7 de Grafana.
