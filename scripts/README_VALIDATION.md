# Validation Scripts - Sentinel Cortex™

## Overview

Scripts para validar el rendimiento y la independencia de la arquitectura Dual-Guardian en Debian 13 "Trixie" con Kernel 6.12 EEVDF.

---

## Scripts Disponibles

### 1. `validate_eevdf_performance.sh`

**Propósito**: Medir la latencia de Guardian-Alpha con el scheduler EEVDF del Kernel 6.12.

**Requisitos**:
- `bpftrace` instalado
- Permisos `sudo`
- Kernel 6.12+

**Uso**:
```bash
sudo ./scripts/validate_eevdf_performance.sh
```

**Métricas**:
- Latencia LSM hook: Target <100μs
- Latencia bajo carga: Target <200μs
- Distribución de latencias (histograma)

**Interpretación**:
- ✅ <50μs: Excelente (idle)
- ✅ <100μs: Bueno (normal load)
- ⚠️ <200μs: Aceptable (high load)
- ❌ >200μs: Problema (investigar)

---

### 2. `test_dual_lane_stress.sh`

**Propósito**: Validar que Security Lane es independiente de Observability Lane bajo carga extrema.

**Requisitos**:
- Backend corriendo (`docker-compose up -d backend`)
- Python 3 con `requests`

**Uso**:
```bash
./scripts/test_dual_lane_stress.sh
```

**Escenario**:
1. **Baseline**: Medir latencia Security Lane sin carga
2. **Saturation**: Saturar Observability Lane (1000 eventos/sec)
3. **Validation**: Inyectar eventos críticos en Security Lane
4. **Analysis**: Comparar latencias

**Métricas de Éxito**:
- ✅ Latencia promedio <10ms
- ✅ Latencia máxima <20ms
- ✅ Degradación <50%

---

### 3. `audit_x86_hardening.sh`

**Propósito**: Auditar configuración de seguridad x86 en Debian 13.

**Uso**:
```bash
./scripts/audit_x86_hardening.sh
```

**Verifica**:
- Arquitectura (x86_64)
- Intel CET / AMD Shadow Stack
- Hardware Watchdog
- `perf_event_paranoid`

---

## Workflow de Validación

### Paso 1: Auditar Hardware
```bash
./scripts/audit_x86_hardening.sh
```

### Paso 2: Validar EEVDF Performance
```bash
sudo ./scripts/validate_eevdf_performance.sh
```

### Paso 3: Stress Test Dual-Lane
```bash
# Iniciar backend
docker-compose up -d backend

# Ejecutar stress test
./scripts/test_dual_lane_stress.sh
```

### Paso 4: Revisar Resultados

**EEVDF Performance**:
- Revisar histograma de latencias
- Confirmar <100μs en condiciones normales

**Dual-Lane Stress**:
- Confirmar Security Lane <10ms promedio
- Confirmar degradación <50%

---

## Troubleshooting

### Error: "bpftrace not installed"
```bash
sudo apt-get install bpftrace
```

### Error: "Backend not running"
```bash
docker-compose up -d backend
# Esperar 10s para healthcheck
curl http://localhost:8000/health
```

### Error: "Permission denied"
```bash
chmod +x scripts/*.sh
```

### Latencia Alta (>200μs)
**Posibles causas**:
1. CPU saturado → Reducir carga
2. Scheduler no es EEVDF → Verificar kernel
3. eBPF program overhead → Optimizar Guardian-Alpha

---

## Métricas de Referencia

### Kernel 6.12 EEVDF (Expected)
- Idle: 20-50μs
- Normal: 50-100μs
- High Load: 100-200μs

### Kernel <6.12 CFS (Baseline)
- Idle: 50-100μs
- Normal: 100-200μs
- High Load: 200-500μs

**Mejora esperada**: ~50% reducción en latencia

---

## Integración Continua

Para CI/CD, agregar a pipeline:

```yaml
# .github/workflows/performance.yml
- name: Validate EEVDF Performance
  run: |
    sudo ./scripts/validate_eevdf_performance.sh
    
- name: Dual-Lane Stress Test
  run: |
    docker-compose up -d backend
    ./scripts/test_dual_lane_stress.sh
```

---

## Referencias

- [Kernel 6.12 EEVDF Scheduler](https://lwn.net/Articles/925371/)
- [eBPF Performance Guide](https://ebpf.io/what-is-ebpf/)
- [Debian 13 Trixie Release Notes](https://www.debian.org/releases/trixie/)
