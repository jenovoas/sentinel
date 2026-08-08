# Implementación Arquitectura Dual-Lane para Sentinel

##  Objetivo

Separar flujos de datos en dos carriles independientes para eliminar riesgos existenciales identificados en análisis forense:

1. **Security & Audit Lane** - Determinista, cero buffering, cero latencia
2. **Observability & Trends Lane** - Buffering permitido, predicción habilitada

---

## ⚠ Problemas Críticos Identificados

### 1. **Inmutabilidad Temporal de Loki** (Talón de Aquiles)
- **Riesgo**: Buffers dinámicos pueden reordenar logs → Loki rechaza con `out-of-order`
- **Consecuencia**: Pérdida de evidencia forense durante ataques
- **Estado actual**: `unordered_writes: true` en Loki (mitigación temporal, -10-15% performance)

### 2. **Ventana de Ceguera** (Latency vs Throughput)
- **Riesgo**: Buffering de 500ms-1s crea ventana donde ataques pasan sin detección
- **Consecuencia**: AIOpsDoom puede ejecutar payload antes de sanitización
- **Estado actual**: AIOpsShield paralelo implementado, pero buffers globales afectan todo

### 3. **Volatilidad de Memoria y Backpressure**
- **Riesgo**: Sin límites duros, DDoS llena RAM → OOM Killer mata proceso
- **Consecuencia**: Pérdida total de datos de auditoría en memoria
- **Estado actual**: No hay WAL (Write-Ahead Log) ni límites de backpressure

### 4. **"Regeneración de Data" = Fabricación de Evidencia**
- **Riesgo**: Imputar datos faltantes en logs de seguridad = encubrir ataques
- **Consecuencia**: Auditoría inválida, evidencia forense comprometida
- **Estado actual**: Implementado en buffers predictivos sin separación de carriles

---

## 💡 Solución: Arquitectura Dual-Lane

### Carril 1: Security & Audit Lane (Determinista)

**Fuentes**:
- `auditd` / eBPF syscalls
- Kernel logs críticos
- AIOpsShield detections
- Dual-Guardian events

**Reglas Estrictas**:
- ❌ **SIN buffering dinámico**
- ❌ **SIN regeneración/imputación**
- ✅ **Prioridad absoluta** (bypass de colas)
- ✅ **WAL obligatorio** (durabilidad)
- ✅ **Timestamp en recolección** (no en envío)
- ✅ **Alerta "IntegrityGap"** si pérdida (nunca imputa)

**Pipeline**:
```
Kernel/auditd → WAL (fsync) → Dual-Guardian (decisión local) → Storage Forense (S3) → Loki (lane=security)
                                    ↓
                            Bloqueo inmediato (<10ms)
```

**Labels Loki**:
```yaml
lane: security
source: auditd|ebpf|shield
priority: critical
host: <hostname>
pid: <process_id>
```

---

### Carril 2: Observability & Trends Lane (Predictivo)

**Fuentes**:
- Métricas de sistema (CPU, RAM, disk)
- Logs no críticos (info, debug)
- Trazas de aplicación
- Network metrics

**Reglas Permitidas**:
- ✅ **Buffering dinámico** (optimización throughput)
- ✅ **Imputación de métricas** (continuidad dashboards)
- ✅ **Batch processing** (eficiencia)
- ✅ **Predictive cache** (ML)

**Restricciones**:
- Límites duros: `max_buffer_bytes`, `max_batch_records`, `max_batch_ms`
- Backpressure: degradar a passthrough si umbral alcanzado
- Etiquetado: `synthetic=true` para datos imputados
- Reordenamiento: por `(stream_labels, timestamp)` antes de flush

**Pipeline**:
```
Promtail → Buffer (ordenado) → WAL → Loki (lane=ops)
                ↓
        Backpressure control
```

**Labels Loki**:
```yaml
lane: ops
source: prometheus|app|network
synthetic: true|false
host: <hostname>
job: <service_name>
```

---

## 📋 Cambios Requeridos

### A. Nuevo Módulo: `data_lanes.py`

**Ubicación**: `backend/app/core/data_lanes.py`

**Componentes**:
1. `DataLane` enum (`SECURITY`, `OBSERVABILITY`)
2. `SecurityLaneCollector` - Sin buffering, WAL, bypass
3. `ObservabilityLaneCollector` - Buffering, reordenamiento, backpressure
4. `DualLaneRouter` - Enruta eventos según origen/tipo

**Características clave**:
- Detección automática de lane por labels/source
- WAL con fsync periódico (cada 100ms para security, 1s para ops)
- Límites de backpressure configurables
- Métricas de integridad (gaps, drops, latency)

---

### B. Modificar `adaptive_buffers.py`

**Cambios**:
1. Agregar campo `lane: DataLane` a `DataFlowType`
2. Separar configuraciones:
   - `TELEMETRY_SECURITY` → lane=SECURITY, buffer=0
   - `TELEMETRY_OPS` → lane=OBSERVABILITY, buffer=dinámico
3. Método `should_bypass_buffer(flow_type)` → True si security lane

**Ejemplo**:
```python
class DataFlowType(Enum):
    # Security Lane (sin buffering)
    AUDIT_SYSCALL = ("audit", DataLane.SECURITY)
    SHIELD_DETECTION = ("shield", DataLane.SECURITY)
    
    # Observability Lane (con buffering)
    LLM_INFERENCE = ("llm", DataLane.OBSERVABILITY)
    DATABASE_QUERY = ("db", DataLane.OBSERVABILITY)
```

---

### C. Actualizar `sentinel_telem_protect.py`

**Cambios**:
1. Eventos de AIOpsShield → Security Lane (bypass buffer)
2. Respuestas LLM → Observability Lane (buffering permitido)
3. Método `_route_to_lane(event)` para clasificación automática

**Pseudocódigo**:
```python
async def _shield_check_parallel(self, mensaje: str):
    result = self.shield.sanitize(mensaje)
    
    if result.threat_level == ThreatLevel.MALICIOUS:
        # SECURITY LANE: Sin buffer, directo a WAL + Dual-Guardian
        await security_lane.emit_immediate(
            event=result,
            labels={"lane": "security", "source": "shield"}
        )
    
    return result
```

---

### D. Configurar Loki para Dual-Lane

**Archivo**: `observability/loki/loki-config.yml`

**Cambios**:
1. Crear streams separados por `lane` label
2. Configurar `out_of_order_time_window` solo para `lane=ops` (1-3s)
3. Mantener `unordered_writes: false` para `lane=security`
4. Retention diferenciado:
   - Security: 2 años (compliance)
   - Ops: 30 días (operaciones)

**Ejemplo**:
```yaml
limits_config:
  # Security lane: orden estricto
  per_stream_rate_limit: 0  # Sin límite para security
  per_stream_rate_limit_burst: 0
  
  # Ops lane: ventana de tolerancia
  out_of_order_time_window: 2s  # Solo para lane=ops
  
  # Retention por stream
  retention_stream:
    - selector: '{lane="security"}'
      priority: 1
      period: 17520h  # 2 años
    - selector: '{lane="ops"}'
      priority: 2
      period: 720h    # 30 días
```

---

### E. Actualizar Promtail

**Archivo**: `observability/promtail/promtail-config.yml`

**Cambios**:
1. Agregar `lane` label a todos los scrape_configs
2. Timestamp en recolección (no en envío)
3. Reordenamiento antes de batch

**Ejemplo**:
```yaml
scrape_configs:
  # Security lane
  - job_name: auditd
    static_configs:
      - labels:
          lane: security
          source: auditd
          priority: critical
    pipeline_stages:
      - timestamp:
          source: extracted_timestamp
          format: RFC3339
          action_on_failure: fudge  # Asignar timestamp NOW si falta
  
  # Observability lane
  - job_name: docker-backend
    static_configs:
      - labels:
          lane: ops
          source: app
    pipeline_stages:
      - timestamp:
          source: timestamp
          format: RFC3339
```

---

### F. Implementar WAL (Write-Ahead Log)

**Ubicación**: `backend/app/core/wal.py`

**Características**:
- Append-only file per lane
- Fsync periódico (100ms security, 1s ops)
- Replay on startup (recuperación de fallos)
- Rotación por tamaño (100MB) o tiempo (1h)
- Compresión LZ4/ZSTD

**API**:
```python
class WAL:
    async def append(self, lane: DataLane, event: dict)
    async def flush(self, lane: DataLane)
    async def replay(self, lane: DataLane) -> AsyncGenerator[dict]
    async def rotate(self, lane: DataLane)
```

---

## 🧪 Tests de Validación

### 1. **Orden Temporal** (Loki out-of-order)
```bash
# Simular jitter 20-200ms entre productores
# Verificar 0 errores out-of-order en lane=security
# Permitir hasta 5% errores en lane=ops (ventana 2s)
```

### 2. **Ventana de Ceguera** (Security bypass)
```bash
# Inyectar evento malicioso
# Medir t(kernel → decision)
# Objetivo: <10ms extremo a extremo
```

### 3. **Backpressure** (OOM prevention)
```bash
# Fuzzear 10-50k eventos/s
# Verificar buffer no supera límite
# WAL absorbe picos sin pérdida
```

### 4. **Fallo y Recuperación** (WAL replay)
```bash
# Matar proceso durante escritura
# Reiniciar y replay desde WAL
# Verificar 0 eventos perdidos en lane=security
```

### 5. **HA y Deduplicación** (Mimir)
```bash
# Dos productores HA con latencia alternada
# Verificar sin duplicados ni gaps
# Medir flapping de líder
```

---

## 📊 Métricas de Éxito

| Métrica | Security Lane | Observability Lane |
|---------|---------------|-------------------|
| **Latencia E2E** | <10ms | <200ms |
| **Pérdida de datos** | 0% (alerta si gap) | <0.1% |
| **Out-of-order** | 0% | <5% (ventana 2s) |
| **Throughput** | Sin límite | 10-50k eventos/s |
| **WAL overhead** | <5ms | <20ms |
| **Backpressure activado** | Nunca (alerta) | <1% del tiempo |

---

## 🚨 User Review Required

> [!CAUTION]
> **Breaking Changes Potenciales**
> 
> 1. **Loki streams separados**: Queries existentes deben agregar `{lane="security"}` o `{lane="ops"}`
> 2. **WAL introduce latencia**: +5-20ms según lane (aceptable para durabilidad)
> 3. **Backpressure puede degradar**: Si carga >50k eventos/s, ops lane pasa a passthrough
> 4. **Retention diferenciado**: Security 2 años (↑ storage), Ops 30 días

> [!IMPORTANT]
> **Decisiones de Diseño Críticas**
> 
> - **¿Permitir `unordered_writes` en Loki?** 
>   - Opción A: Solo para `lane=ops` (performance)
>   - Opción B: Desactivar y garantizar orden en Promtail (integridad)
> 
> - **¿Tamaño de ventana `out_of_order_time_window`?**
>   - Recomendado: 1-3s para `lane=ops`
>   - Trade-off: Mayor ventana = más tolerancia pero más memoria
> 
> - **¿Política de drop en backpressure?**
>   - Security lane: NUNCA drop, solo alerta
>   - Ops lane: Drop logs `level=debug` primero, luego `info`

---

## 📝 Próximos Pasos

### Fase 1: Fundamentos (Hoy)
1. Crear `data_lanes.py` con enums y routers básicos
2. Implementar `WAL` con append + replay
3. Modificar `adaptive_buffers.py` para dual-lane
4. Tests unitarios de WAL y routing

### Fase 2: Integración (Mañana)
1. Actualizar `sentinel_telem_protect.py` con lane routing
2. Configurar Loki con streams separados
3. Actualizar Promtail con labels `lane`
4. Tests de integración E2E

### Fase 3: Validación (2-3 días)
1. Ejecutar 5 tests de validación
2. Benchmark comparativo (antes/después)
3. Stress test con fuzzer AIOpsDoom
4. Documentar resultados

### Fase 4: Producción (1 semana)
1. Migración gradual (feature flag)
2. Monitoreo de métricas de éxito
3. Ajuste de configuraciones
4. Rollback plan si falla

---

## 💰 Impacto en Pitch ANID

### Narrativa Actualizada

**Antes** (Riesgoso):
> "Buffers dinámicos aumentan velocidad 50%"

**Después** (Blindado):
> "Arquitectura Dual-Lane: **Precisión forense de grado kernel** (lane security, cero buffering, WAL) + **Predicción operativa sin gaps** (lane ops, buffering optimizado). Somos los únicos que ofrecen ambos en la misma plataforma."

### Diferenciadores vs Competencia

| Feature | Datadog | Dynatrace | **Sentinel** |
|---------|---------|-----------|--------------|
| **Forensic Integrity** | ❌ | ❌ | ✅ WAL + Security Lane |
| **AIOpsDoom Defense** | ❌ | ❌ | ✅ AIOpsShield |
| **Kernel-Level (Ring 0)** | ⚠ Agent | ⚠ Agent | ✅ eBPF nativo |
| **Dual-Lane Architecture** | ❌ | ❌ | ✅ Patentable |
| **Predictive Buffering** | ⚠ Básico | ⚠ Básico | ✅ ML-driven |

---

## ✅ Conclusión

Esta arquitectura elimina los **3 riesgos existenciales**:

1. ✅ **Out-of-order en Loki**: Orden garantizado en security lane, ventana tolerante en ops lane
2. ✅ **Ventana de ceguera**: Security lane bypass (<10ms), ops lane buffered
3. ✅ **OOM por buffering**: WAL + backpressure + límites duros

**Resultado**: Sistema de seguridad auditable + observabilidad predictiva, sin compromisos.
