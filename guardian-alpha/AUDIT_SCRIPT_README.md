# Sentinel Audit Script - Quick Start

## 🚀 Ejecución Rápida

```bash
cd /home/jnovoas/sentinel/guardian-alpha
sudo bash sentinel_audit.sh
```

## 📊 Output

El script genera un directorio timestamped en `/tmp/` con:

```
/tmp/sentinel_audit_20260101_091234/
├── audit_matrix.md      # ← Reporte principal (leer este)
├── bpf_progs.txt        # Lista de programas eBPF
├── bpf_maps.txt         # Lista de mapas eBPF
└── trace_sample.txt     # Muestra de eventos
```

## ✅ Exit Codes

| Code | Significado |
|------|-------------|
| 0 | ✅ Todo OK |
| 1 | ❌ Kernel < 6.1 |
| 2 | ❌ BPF LSM no habilitado |
| 4 | ❌ eBPF program no cargado |
| 8 | ❌ Trace events ausentes |
| 16 | ❌ Python bridge error |

**Nota**: Los códigos son bit flags, pueden combinarse (ej: 5 = kernel + eBPF)

## 📋 Qué Valida

- [x] Kernel version (>= 6.1)
- [x] EEVDF scheduler availability (>= 6.6)
- [x] BPF LSM enabled
- [x] Debugfs mounted
- [x] eBPF programs loaded
- [x] eBPF maps created
- [x] Trace events generating
- [x] Timestamp extraction
- [x] Ingestion lag (< 5s)
- [x] Python bridge imports
- [x] CVE hallucination checks
- [x] Scheduler param validation

## 🔧 Troubleshooting

### "bpftool: Not installed"
```bash
sudo apt install linux-tools-common linux-tools-$(uname -r)
```

### "Debugfs: Not mounted"
```bash
sudo mount -t debugfs none /sys/kernel/debug
```

### "BPF LSM: Not enabled"
Requiere recompilar kernel con `CONFIG_BPF_LSM=y` y boot param `lsm=...,bpf`

### "eBPF program: Not loaded"
```bash
sudo bash run_demo.sh
```

## 📈 Hallucination Rate

El script genera métricas automáticas:

```
| Fuente | Claims | Hallucinaciones | Tasa |
|--------|--------|-----------------|------|
| Kernel facts | 6 | 0 | 0% ✅ |
| Observability | 4 | 0 | 0% ✅ |
| Security terms | 1 | 1 | 100% ⚠️ |
| Scheduler params | 2 | 1 | 50% ⚠️ |
```

## 🎯 Uso en CI/CD

```bash
#!/bin/bash
# ci-audit.sh

cd /path/to/sentinel/guardian-alpha
sudo bash sentinel_audit.sh

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Audit passed"
    exit 0
else
    echo "❌ Audit failed with code: $EXIT_CODE"
    
    # Decode failures
    [ $((EXIT_CODE & 1)) -ne 0 ] && echo "  - Kernel version"
    [ $((EXIT_CODE & 2)) -ne 0 ] && echo "  - BPF LSM"
    [ $((EXIT_CODE & 4)) -ne 0 ] && echo "  - eBPF program"
    [ $((EXIT_CODE & 8)) -ne 0 ] && echo "  - Trace events"
    [ $((EXIT_CODE & 16)) -ne 0 ] && echo "  - Python bridge"
    
    exit $EXIT_CODE
fi
```

## 📚 Documentación Completa

- `AUDIT_PLAN.md` - Plan de auditoría completo
- `ANTI_HALLUCINATION_LOG.md` - Log de hallucinations detectadas
- `AUDIT_AUTOMATION_SUMMARY.md` - Resumen ejecutivo

---

**Versión**: 2.0.0  
**Última actualización**: 2026-01-01
