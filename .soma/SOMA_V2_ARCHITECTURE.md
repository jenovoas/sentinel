# SOMA v2.0 - Arquitectura Rediseñada

## Premisa Correcta

**SOMA no es un motor Base-60** — es una capa de orquestación. Sentinel consume implementaciones concretas; algunas proceden del proyecto independiente ME-60OS.

**SOMA es el orquestador de Sentinel**; no convierte a ME-60OS en el mismo proyecto ni requiere importar su sistema completo.

## Stack Integrado (No Duplicado)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOMA (Orquestador)                      │
│  • Contratos entre fases                                   │
│  • Handoffs                                      │
│  • Coordinación de tareas                                  │
│  • Validación de artefactos                                 │
└───────────────┬─────────────────────────────────────────────┘
                │ usa
┌───────────────▼─────────────────────────────────────────────┐
│     Componentes Base-60 seleccionados de ME-60OS           │
│  • qhc-agent: Driver YHWH 10-5-6-5 (1Hz) ✅            │
│  • adm-agent: Métricas mesh TQ→SPA (0.858) ✅            │
│  • vid-agent: Quantum cooling (10Hz) ✅                    │
│  • audit-cortex-bridge: Puente audit→Cortex ✅             │
└───────────────┬─────────────────────────────────────────────┘
                │ sobre
┌───────────────▼─────────────────────────────────────────────┐
│              MycNet (Red Hexagonal)                         │
│  • batman-adv mesh con TQ (Transmitter Quality)            │
│  • Auto-descubrimiento de nodos                           │
│  • Coherencia S60 calculada por adm-agent                  │
└─────────────────────────────────────────────────────────────┘
```

## Arquitectura SOMA v2.0

### Componentes SOMA (sin duplicar los componentes importados de ME-60OS)

1. **Contract Engine**
   - Define contratos entre fases
   - Valida inputs/outputs
   - Genera artefactos

2. **Handoff Manager**
   - Handoffs atómicos entre agentes
   - Validación antes de transferencia
   - Rollback automático

3. **Task Scheduler**
   - Asigna tareas a agentes
   - Balancea carga según coherencia mesh
   - Prioriza por fase QHC

4. **State Tracker**
   - Estado compartido en `.soma/state.yaml`
   - Timestamps en formato SPA (de qhc-agent)
   - Eventos auditados

5. **MycNet Bridge**
   - Conecta con batman-adv
   - Consulta coherencia via adm-agent
   - Descubre nodos/agentes

### Integración con ME-60OS

| SOMA Componente | ME-60OS Servicio | Protocolo |
|-----------------|------------------|-----------|
| QHC Cycle | qhc-agent (1Hz) | gRPC/Unix Socket |
| Mesh Coherence | adm-agent | gRPC/Unix Socket |
| Quantum Cooling | vid-agent | gRPC/Unix Socket |
| Events | audit-cortex-bridge | eBPF Ring Buffer |
| Timestamps | qhc-agent SPA format | S60 string |

### Fases Sentinel (SOMA coordina, ME-60OS ejecuta)

| Fase | SOMA | ME-60OS | Estado |
|-------|-------|----------|--------|
| 0-6 | COMPLETO | COMPLETO | ✅ |
| 7 | **COORDINA** | **EJECUTA** | ⏳ |

## Flujo de Trabajo SOMA v2.0

### 1. Tarea Solicitada
```bash
# Agente o usuario solicita iniciar Fase 7
soma start-phase 7 --agent=claude-glm
```

### 2. SOMA Planifica
```yaml
# SOMA lee state.yaml
phase: 7
status: pending
assignee: null

# Consulta qhc-agent para fase actual
# → QHC: VAV (exhalación) - momento óptimo para flujo
```

### 3. SOMA Consulta ME-60OS
```bash
# Consultar coherencia mesh via adm-agent
adm-client get-coherence
# → 0.858 (S60[000;51,00,00,00])

# Consultar ciclo QHC via qhc-agent
qhc-client get-phase
# → VAV (6) - óptimo para procesar datos
```

### 4. SOMA Asigna Agente
```yaml
agent: claude-glm
node: sentinel (mejor TQ)
handoff:
  from: claude-opus
  phase: 6→7
```

### 5. Handoff Atómico
```yaml
handoff:
  id: "HO-S60[20260226;07,00,00,00]-6-7"
  timestamp_s60: "S60[2026; 02, 26, 07, 00]"
  status: "validating"
  artifacts:
    - containers-status.txt
    - s60-coherence: "S60[000;51,00,00,00]"
```

### 6. Agente Ejecuta
```bash
# Agente usa ME-60OS APIs
qhc-client wait-phase VAV  # Esperar fase óptima
adm-client check-node      # Verificar coherencia
# ... ejecuta tarea
```

### 7. SOMA Valida y Completa
```yaml
phase: 7
status: completed
completed_at_s60: "S60[2026; 02, 26, 08, 30]"
event: "phase_completed"
```

## APIs SOMA → ME-60OS

### gRPC Services (propuesto)

```protobuf
// qhc.proto
service QHC {
    rpc GetPhase(Empty) returns (PhaseResponse);
    rpc GetCoherence(Empty) returns (CoherenceResponse);
    rpc WaitPhase(WaitPhaseRequest) returns (Empty);
}

message PhaseResponse {
    string name = 1;      // "YOD" | "HE_FIRST" | "VAV" | "HE_SECOND"
    uint8 value = 2;      // 10 | 5 | 6 | 5
    float progress = 3;    // 0.0 - 1.0 within phase
    string timestamp_s60 = 4;
}

message CoherenceResponse {
    float value = 1;           // 0.0 - 1.0
    string s60 = 2;            // "S60[000;51,00,00,00]"
    uint8 tq = 3;             // 0 - 255
}
```

## Implementación Plan

### Paso 1: APIs gRPC en ME-60OS
- Modificar qhc-agent para exponer gRPC
- Modificar adm-agent para exponer coherencia TQ
- Crear librería cliente Rust para SOMA

### Paso 2: SOMA Core (Python/Rust)
- Contract Engine (YAML-based)
- Handoff Manager
- Task Scheduler (coherencia-aware)
- State Tracker (SPA timestamps)

### Paso 3: MycNet Bridge
- Conectar con batman-adv
- Descubrir agentes vía mesh
- Balancear carga según TQ

### Paso 4: Integración
- SOMA consume ME-60OS APIs
- Handoffs coordinan con ciclo QHC
- Estado compartido con timestamps S60

## Archivos SOMA v2.0

```
.soma/
├── state.yaml                 # Estado compartido (SPA timestamps)
├── contracts/                # Definiciones de contratos
│   ├── phase6_phase7.yaml
│   └── ...
├── handoffs/                 # Handoffs activos
│   ├── HO-S60[...].yaml
│   └── README.md
├── tasks/                    # Tareas con validación
│   └── dns-001.yaml
├── soma_bridge/              # Puente gRPC → ME-60OS
│   ├── Cargo.toml
│   ├── src/qhc_client.rs
│   ├── src/adm_client.rs
│   └── src/vid_client.rs
└── docs/
    ├── ARCHITECTURE.md        # Este archivo
    └── API_REFERENCE.md
```

## Notas Críticas

1. **No duplicar componentes S60 ya integrados** — verificar su origen y usar solo los componentes seleccionados de ME-60OS.
2. **No duplicar QHC ya integrado** — usar `qhc-agent` solo si forma parte de la integración vigente.
3. **NO reimplementar MycNet** — usar scripts existentes
4. SOMA es SOLO orquestación, no infraestructura
5. La lógica Base-60 pertenece al módulo que la implementa; algunos componentes usados por Sentinel proceden de ME-60OS.
6. SOMA agrega: contratos, handoffs, coordinación

## Diferencia SOMA v1 vs v2

| Aspecto | SOMA v1 (MALO) | SOMA v2 (CORRECTO) |
|---------|-----------------|-------------------|
| S60 | Implementado en soma_core | Componentes seleccionados importados de ME-60OS |
| QHC | Implementado en qhc.rs | Usado desde qhc-agent |
| MycNet | Implementado en mycnet.rs | Usado desde scripts existentes |
| Responsabilidad | Todo en SOMA | Orquestación solo |
| Duplicación | Alta | Cero |

---

**Conclusión**: esta propuesta describe SOMA como capa de orquestación de Sentinel, que integra componentes seleccionados del proyecto independiente ME-60OS; no representa la importación del sistema completo ni evidencia de despliegue.
