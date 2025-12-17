# 📐 UML DIAGRAM SPECIFICATIONS
**Sentinel Cortex™ - Dual Guardian Architecture Diagrams**

**Fecha:** 17 Diciembre 2025  
**Propósito:** Enabling description para provisional patent  
**Status:** SPECIFICATIONS READY FOR DIAGRAMMING

---

## 🎯 OVERVIEW

Estos 3 diagramas UML son CRÍTICOS para completar la "enabling description" requerida por la provisional patent. Deben mostrar claramente cómo el Dual-Guardian funciona a nivel técnico.

---

## 📊 DIAGRAMA 1: SEQUENCE DIAGRAM - eBPF SYSCALL INTERCEPTION

### Propósito
Demostrar cómo Guardian-Alpha intercepta syscalls ANTES de ejecución (previene race conditions).

### Participantes
```
1. Malicious Application (user space)
2. Linux Kernel (kernel space)
3. eBPF Hook (Guardian-Alpha)
4. Policy Engine (Guardian-Alpha)
5. Audit Log (Guardian-Beta)
6. System State (disk/memory)
```

### Flujo de Secuencia

```
ESCENARIO: Aplicación maliciosa intenta rm -rf /data

┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐  ┌─────────┐
│ Malicious   │  │  Linux   │  │   eBPF   │  │   Policy   │  │   Audit   │  │ System  │
│ Application │  │  Kernel  │  │   Hook   │  │   Engine   │  │    Log    │  │  State  │
└──────┬──────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  └─────┬─────┘  └────┬────┘
       │              │              │              │               │             │
       │ execve("/bin/rm", ["-rf", "/data"])        │               │             │
       │─────────────>│              │              │               │             │
       │              │              │              │               │             │
       │              │ LSM hook triggered          │               │             │
       │              │─────────────>│              │               │             │
       │              │              │              │               │             │
       │              │              │ validate_syscall(execve, args)             │
       │              │              │─────────────>│               │             │
       │              │              │              │               │             │
       │              │              │              │ check_policy("/data")       │
       │              │              │              │<──────────────┤             │
       │              │              │              │               │             │
       │              │              │              │ POLICY: DENY  │             │
       │              │              │              │ (no admin approval)         │
       │              │              │              │               │             │
       │              │              │ DECISION: BLOCK              │             │
       │              │              │<─────────────┤               │             │
       │              │              │              │               │             │
       │              │              │ log_blocked_syscall()        │             │
       │              │              │──────────────────────────────>│             │
       │              │              │              │               │             │
       │              │ return -EPERM (Permission Denied)           │             │
       │              │<─────────────┤              │               │             │
       │              │              │              │               │             │
       │ ERROR: Permission denied    │              │               │             │
       │<─────────────┤              │              │               │             │
       │              │              │              │               │             │
       │              │              │              │               │ /data INTACT│
       │              │              │              │               │<────────────┤
       │              │              │              │               │             │
       
RESULTADO: Syscall bloqueada ANTES de ejecución, datos intactos
```

### Elementos Clave para Patent

1. **PRE-EXECUTION INTERCEPTION**
   - eBPF hook se activa ANTES de que kernel ejecute syscall
   - Timing crítico: <100μs latency

2. **DETERMINISTIC DECISION**
   - Policy Engine (no AI-based)
   - Reglas claras: admin approval, maintenance window, etc.

3. **KERNEL-LEVEL ENFORCEMENT**
   - Return -EPERM (kernel error code)
   - Syscall nunca llega a ejecución física

### Diferenciación vs Prior Art

```
AUDITD (Prior Art):
├─ Timing: POST-execution (alerta después)
├─ Resultado: Datos YA borrados
└─ Vulnerable: Race condition

SENTINEL (Novel):
├─ Timing: PRE-execution (bloquea antes)
├─ Resultado: Datos INTACTOS
└─ Seguro: No race condition
```

---

## 📊 DIAGRAMA 2: COMPONENT DIAGRAM - DUAL-GUARDIAN ARCHITECTURE

### Propósito
Mostrar la arquitectura completa de Dos Nervios™ con mutual surveillance.

### Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SENTINEL CORTEX™                              │
│                     (Cognitive Security System)                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                │                                       │
                ▼                                       ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐
│     GUARDIAN-ALPHA            │◄─────►│     GUARDIAN-BETA             │
│   (Intrusion Detection)       │       │   (Integrity Validation)      │
│                               │       │                               │
│  ┌─────────────────────────┐ │       │  ┌─────────────────────────┐  │
│  │  eBPF Syscall Monitor   │ │       │  │  Config Validator       │  │
│  │  - execve, open, ptrace │ │       │  │  - /etc/sentinel/*      │  │
│  │  - connect, setuid      │ │       │  │  - Immutable backup     │  │
│  └─────────────────────────┘ │       │  └─────────────────────────┘  │
│                               │       │                               │
│  ┌─────────────────────────┐ │       │  ┌─────────────────────────┐  │
│  │  Policy Engine          │ │       │  │  Backup Manager         │  │
│  │  - Admin approval req   │ │       │  │  - Snapshot every 1h    │  │
│  │  - Maintenance window   │ │       │  │  - Restore on tamper    │  │
│  └─────────────────────────┘ │       │  └─────────────────────────┘  │
│                               │       │                               │
│  ┌─────────────────────────┐ │       │  ┌─────────────────────────┐  │
│  │  Mutual Surveillance    │ │       │  │  Mutual Surveillance    │  │
│  │  - Monitors Beta health │ │       │  │  - Monitors Alpha health│  │
│  │  - Heartbeat: 10s       │ │       │  │  - Heartbeat: 10s       │  │
│  └─────────────────────────┘ │       │  └─────────────────────────┘  │
│                               │       │                               │
│  Runtime: Kernel Space (Ring 0)│     │  Runtime: User Space (Ring 3) │
└───────────────┬───────────────┘       └───────────────┬───────────────┘
                │                                       │
                │         ┌─────────────────┐          │
                └────────►│  CORTEX (AI)    │◄─────────┘
                          │  - Ollama       │
                          │  - Phi-3 Mini   │
                          │  - Decision Eng │
                          └─────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │  TELEMETRY      │
                          │  - Loki (logs)  │
                          │  - Mimir (metrics)│
                          │  - Tempo (traces)│
                          └─────────────────┘
```

### Mutual Surveillance Mechanism (ACTUALIZADO con Heartbeat Atómico)

```
SHARED HEARTBEAT (Arc<AtomicU64>):
├─ Storage: Single 64-bit atomic timestamp (Unix epoch)
├─ Location: Shared memory (accessible from kernel + user space)
├─ Synchronization: Lock-free atomic operations
└─ Overhead: < 0.01% CPU utilization

GUARDIAN-ALPHA → HEARTBEAT:
├─ Emission: Every eBPF event cycle (~1000/sec)
├─ Operation: Atomic store of current timestamp
├─ Latency: ~5-10ns per update
└─ Failure mode: Timestamp stops updating if Alpha crashes

GUARDIAN-BETA → HEARTBEAT:
├─ Check frequency: Every 1 second
├─ Verification: (current_time - last_heartbeat) > TIMEOUT?
├─ Timeout threshold: 5 seconds (configurable)
├─ Action on timeout: Trigger auto-regeneration protocol
└─ Recovery time: < 7 seconds total

AUTO-REGENERATION PROTOCOL:
├─ Detection: < 5s (timeout threshold)
├─ Actions (automatic, NO human intervention):
│   ├─ 1. Log critical event (timestamp, delta)
│   ├─ 2. Restart eBPF subsystem
│   ├─ 3. Reload security policies from immutable backup
│   ├─ 4. Reset heartbeat (prevent alert loop)
│   └─ 5. Resume normal monitoring
├─ Regeneration time: < 2s (eBPF reload)
└─ Total downtime: < 7s

BI-DIRECTIONAL SURVEILLANCE:
├─ Alpha emits → Beta verifies (IMPLEMENTED)
├─ Beta emits → Alpha verifies (FUTURE: Phase 2)
├─ Ninguno puede ser deshabilitado sin que el otro lo detecte
└─ Auto-regeneration: Restore from immutable backup
```

**Diagrama Actualizado con Heartbeat:**

```
┌─────────────────────────────────────────────────────────────┐
│              Arc<AtomicU64> (Shared Heartbeat)              │
│                Unix Timestamp (64-bit atomic)               │
│                      ↓                    ↓                  │
│            Guardian-Alpha          Guardian-Beta            │
│            (Kernel/Ring 0)         (User-space/Ring 3)      │
│                      │                    │                  │
│         Emits: ~1000/sec          Checks: Every 1s          │
│         (atomic store)            (timeout: 5s)             │
│                      │                    │                  │
│                      └──── Failure ───────┤                 │
│                         (timeout > 5s)    │                 │
│                                           ↓                  │
│                          Auto-Regeneration Protocol         │
│                          (< 7s recovery, no human)          │
└─────────────────────────────────────────────────────────────┘
```

### Elementos Clave para Patent

1. **SEPARATION OF CONCERNS**
   - Alpha: Intrusion (syscalls)
   - Beta: Integrity (config, backup)

2. **MUTUAL SURVEILLANCE**
   - Bi-directional monitoring
   - Auto-regeneration on failure

3. **KERNEL vs USER SPACE**
   - Alpha: Ring 0 (kernel)
   - Beta: Ring 3 (user)
   - Physical separation

---

## 📊 DIAGRAMA 3: STATE DIAGRAM - GUARDIAN LIFECYCLE

### Propósito
Mostrar estados y transiciones de los Guardians, incluyendo failure recovery.

### Estados del Guardian

```
                    ┌──────────────┐
                    │     INIT     │
                    │  (Startup)   │
                    └──────┬───────┘
                           │
                           │ load_config()
                           │ load_ebpf_program()
                           │
                           ▼
                    ┌──────────────┐
              ┌────►│  MONITORING  │◄────┐
              │     │   (Active)   │     │
              │     └──────┬───────┘     │
              │            │             │
              │            │ threat_detected()
              │            │             │
              │            ▼             │
              │     ┌──────────────┐    │
              │     │    ALERT     │    │
              │     │ (Evaluating) │    │
              │     └──────┬───────┘    │
              │            │             │
              │            │ policy_check()
              │            │             │
              │      ┌─────┴─────┐      │
              │      │           │      │
              │      ▼           ▼      │
              │ ┌─────────┐ ┌─────────┐│
              │ │ ALLOW   │ │  BLOCK  ││
              │ │(Approved)│ │(Denied) ││
              │ └────┬────┘ └────┬────┘│
              │      │           │     │
              │      │           │ log_blocked()
              │      │           │     │
              │      └───────┬───┘     │
              │              │         │
              │              │ continue_monitoring()
              │              │         │
              └──────────────┴─────────┘
                             │
                             │ guardian_failure_detected()
                             │
                             ▼
                      ┌──────────────┐
                      │   FAILURE    │
                      │  (Degraded)  │
                      └──────┬───────┘
                             │
                             │ mutual_surveillance_triggered()
                             │
                             ▼
                      ┌──────────────┐
                      │ REGENERATING │
                      │ (Restoring)  │
                      └──────┬───────┘
                             │
                             │ restore_from_backup()
                             │ reload_ebpf_program()
                             │
                             ▼
                      ┌──────────────┐
                      │   RECOVERED  │
                      │  (Healthy)   │
                      └──────┬───────┘
                             │
                             │ resume_monitoring()
                             │
                             └──────────────┐
                                           │
                                           ▼
                                    (back to MONITORING)
```

### Transiciones Críticas

**1. MONITORING → ALERT**
```
Trigger: threat_detected()
Conditions:
├─ Syscall maliciosa detectada (execve, rm -rf)
├─ Config file modificado sin aprobación
└─ Heartbeat del otro Guardian falla

Time: <100μs (kernel-level)
```

**2. ALERT → BLOCK**
```
Trigger: policy_check() returns DENY
Conditions:
├─ No admin approval
├─ No maintenance window
├─ Confidence < 0.9 (multi-factor)

Action:
├─ Return -EPERM (syscall)
├─ Log blocked action
└─ Alert admin
```

**3. FAILURE → REGENERATING**
```
Trigger: mutual_surveillance_triggered()
Conditions:
├─ Guardian heartbeat timeout (>30s)
├─ Config tampering detected
├─ eBPF program unloaded

Action:
├─ Restore from immutable backup
├─ Reload eBPF program
├─ Notify admin
└─ Resume monitoring
```

### Elementos Clave para Patent

1. **AUTO-REGENERATION**
   - Automatic recovery from failure
   - Immutable backup restoration
   - No human intervention required

2. **MUTUAL SURVEILLANCE TRIGGER**
   - Other Guardian detects failure
   - Initiates regeneration
   - Bi-directional protection

3. **DETERMINISTIC STATES**
   - Clear state transitions
   - Predictable behavior
   - No AI-based state changes

---

## 🎯 IMPLEMENTACIÓN DE DIAGRAMAS

### Herramientas Recomendadas

**Opción 1: PlantUML (Recomendado para Patent)**
```
Pros:
├─ Text-based (version control)
├─ Professional output
├─ Widely accepted by USPTO
└─ Free

Cons:
├─ Curva de aprendizaje
└─ Requiere Java
```

**Opción 2: Draw.io (Más Visual)**
```
Pros:
├─ Interfaz visual
├─ Fácil de usar
├─ Export a PNG/SVG
└─ Free

Cons:
├─ Menos profesional
└─ Más difícil de version control
```

**Opción 3: Lucidchart (Profesional)**
```
Pros:
├─ Templates UML
├─ Colaboración
├─ Professional output
└─ USPTO-ready

Cons:
├─ Paid ($$$)
└─ Overkill para 3 diagramas
```

**RECOMENDACIÓN:** PlantUML para patent filing, Draw.io para investor pitch

---

## 📋 CHECKLIST DE COMPLETITUD

### Diagrama 1: Sequence (eBPF Flow)
- [ ] Muestra PRE-execution interception
- [ ] Timing <100μs especificado
- [ ] Return -EPERM (kernel error)
- [ ] Contraste con auditd (post-fact)
- [ ] Datos intactos demostrado

### Diagrama 2: Component (Dual-Guardian)
- [ ] Guardian-Alpha (kernel space)
- [ ] Guardian-Beta (user space)
- [ ] Mutual surveillance (bi-directional)
- [ ] Auto-regeneration mechanism
- [ ] Separation of concerns clara

### Diagrama 3: State (Lifecycle)
- [ ] Estados: INIT, MONITORING, ALERT, BLOCK, FAILURE, REGENERATING
- [ ] Transiciones con triggers
- [ ] Auto-regeneration flow
- [ ] Mutual surveillance trigger
- [ ] Recovery path clara

---

## 🎯 PRÓXIMOS PASOS

### Esta Semana (Prioridad 1)

1. **Crear Diagramas** (4-6 horas)
   - Diagrama 1: Sequence (2 horas)
   - Diagrama 2: Component (2 horas)
   - Diagrama 3: State (2 horas)

2. **Validar con Equipo** (1 hora)
   - Technical review
   - Clarity check
   - Patent attorney preview

3. **Incluir en Patent Materials** (30 min)
   - Export a PNG/SVG
   - Add to provisional patent draft
   - Send to attorney

### Timeline

```
DÍA 1 (Hoy): Specifications DONE ✅
DÍA 2 (Mañana): Create diagrams
DÍA 3 (Jueves): Review + refine
DÍA 4 (Viernes): Send to attorney
```

---

**Documento:** UML Diagram Specifications  
**Status:** ✅ SPECIFICATIONS COMPLETE  
**Next Action:** Create diagrams (PlantUML or Draw.io)  
**Timeline:** 2-3 días to completion  
**Purpose:** Enabling description for provisional patent
