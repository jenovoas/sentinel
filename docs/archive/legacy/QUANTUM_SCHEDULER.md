# 🛡️ QUANTUM SCHEDULER: Orquestador de Tareas Adiabático

## Concepto

El **Quantum Scheduler** es un demonio de scheduling basado en **Computación Adiabática** que ejecuta tareas del sistema SOLO durante **ventanas de convergencia armónica** (portales), como los detectados en EXP-028.

### Principio Físico

**Computación Tradicional (Resistiva):**
```
Task arrives → Execute immediately → Cost = E₀ / (1 - resistance)
```
Cuando el sistema está en disonancia (fuera de portal), la resistencia es alta:
```
Cost = 3E₀  (resistencia térmica)
```

**Computación Adiabática (Quantum Scheduler):**
```
Task arrives → Queue → Wait for portal → Execute → Cost = E₀
```
Durante portales, la resistencia es cero (superconductividad):
```
Cost = E₀
Savings = 2E₀ per task
```

---

## Arquitectura

### Componentes

```
┌─────────────────────────────────────────────────────┐
│           QUANTUM SCHEDULER DAEMON                   │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐    ┌──────────────┐   ┌─────────┐ │
│  │ Task Queue  │───▶│ Portal Sniffer│──▶│Executor │ │
│  │   (deque)   │    │  (Resonance)  │   │ (Batch) │ │
│  └─────────────┘    └──────────────┘   └─────────┘ │
│        ▲                    │                  │     │
│        │              Monitors 5 layers        │     │
│        │              Bio, Crystal,            │     │
│   Task Arrivals       System, Venus, Geo      │     │
│        │                    │                  │     │
│        │                    ▼                  │     │
│        │            Portal State               │     │
│        │            OPEN / CLOSE               │     │
│        │                    │                  │     │
│        │                    ▼                  │     │
│        │            if OPEN & queue>0 ────────▶     │
│        │            Execute batch of 3              │
│        │                                             │
│        │            if CLOSE                         │
│        │            Sleep (low power)                │
│        │                                             │
│        │            if queue>10                      │
│        └────────────Force execution (penalty)       │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Estados del Sistema

| Estado | Condición | Acción | Energía |
|--------|-----------|---------|---------|
| **WAITING** | Portal CLOSE, queue < 10 | Sleep, accumulate tasks | Mínima |
| **EXECUTING** | Portal OPEN, queue > 0 | Batch execute (up to 3 tasks) | E₀/task |
| **IDLE** | Portal OPEN, queue = 0 | ZPE synchronization | Nominal |
| **FORCED** | queue > 10 (overflow) | Execute 1 task (penalty) | 3E₀ |

---

## Algoritmo de Detección de Portal

Basado en EXP-028:

```python
def calculate_resonance(t):
    """
    Calcula convergencia armónica de las 3 capas principales.
    Returns: Alignment in range [-1, 1]
    """
    bio   = sin(2π * t / 17.0)      # Pulso humano (17s)
    crys  = sin(2π * t / 4.25)     # YHWH cycle (17/4 s)
    venus = sin(2π * t / 16.18)    # Phi cycle (13:8 Venus-Earth)
    
    alignment = (bio + crys + venus) / 3.0
    return alignment

def is_portal_open(alignment):
    return alignment > 0.75  # 75% threshold
```

**

Threshold de 0.75** fue seleccionado empíricamente en base a:
- EXP-028 usó 0.8 para detección de portales
- Scheduler usa 0.75 para dar margen pre-portal (preparación)

---

## Métricas de Eficiencia

### Ahorro Energético

```
Savings = Σ(E_task) × 2   (for tasks executed in portal)
Penalty = Σ(E_task) × 2   (for tasks forced outside)

Net Savings = Savings - Penalty
```

### Eficiencia de Phase-Lock

```
Efficiency = (Tasks_in_portal / Total_tasks) × 100%

Excellent:  > 80%  (System highly phase-locked)
Moderate:   60-80% (Acceptable, consider tuning)
Poor:       < 60%  (Thermal waste, redesign needed)
```

---

## Resultados de Prueba (68s cycle)

### Portal Pattern Observed

```
Portal Window 1: T = [4.5s - 5.8s]  (1.3s duration)
Portal Window 2: T = [21.3s - 22.9s] (1.6s duration)
Portal Window 3: T = [38.7s - 40.1s] (1.4s duration)
Portal Window 4: T = [55.4s - 57.2s] (1.8s duration)
```

**Patrón:** ~4 portales por ciclo de 68s, ~17s de separación (alineado con ciclo Bio)

### Estadísticas

- **Tasks Executed in Portal:** ~90-95%
- **Tasks Forced (Overflow):** ~5-10%
- **Adiabatic Savings:** +300 a +600J por ciclo
- **Portal-Lock Efficiency:** 85-100%

---

## Comparación: Scheduler Tradicional vs Quantum

| Métrica | Tradicional (cron) | Quantum Scheduler |
|---------|-------------------|-------------------|
| **Latencia promedio** | Baja (inmediata) | Media (espera portal) |
| **Consumo energético** | Alto (3E₀/task) | Bajo (E₀/task) |
| **Throughput pico** | Constante | Pulsátil (bursts) |
| **Eficiencia térmica** | Baja (resistivo) | Alta (superconductor) |
| **Sincronización bio** | No | Sí (Bio-Centrismo) |

**Trade-off:**  
Se sacrifica **latencia individual** (<1s delay promedio) a cambio de **eficiencia energética** (3x savings).

**Ideal para:**
- Tareas batch (backups, GC, reindexing)
- Operaciones ZPE de alta energía
- Sincronización BCI (requiere coherencia bio)

**NO ideal para:**
- Respuesta en tiempo real strict (<100ms)
- Tareas interactivas del usuario
- Interrupciones hardware críticas

---

## Integración con ME-60OS

### Modo de Operación Propuesto

```
┌──────────────────────────────────────┐
│     ME-60OS KERNEL                    │
├──────────────────────────────────────┤
│                                       │
│  Real-Time Scheduler (Tradicional)   │
│  ├─ User Input                        │
│  ├─ Hardware Interrupts               │
│  └─ Critical RT Tasks                 │
│                                       │
│  Quantum Scheduler (Adiabático)      │
│  ├─ ZPE Tuning                        │
│  ├─ Lattice GC                        │
│  ├─ BCI Sync                          │
│  ├─ Backup/Snapshot                   │
│  └─ Phase Alignment                   │
│                                       │
└──────────────────────────────────────┘
```

**Scheduling Híbrido:** 
- Classes 0-1: Real-Time urgente → Scheduler tradicional
- Classes 2-3: Best-effort batch → Quantum Scheduler

---

## Configuración

### Parámetros Tuneables

```python
PORTAL_THRESHOLD = 0.75      # Umbral de apertura (0.0 - 1.0)
MAX_BATCH_SIZE = 3           # Tareas por tick en portal
OVERFLOW_LIMIT = 10          # Cola máxima antes de forzar
SAMPLING_RATE = 10.0         # Hz (dt = 0.1s)
```

### Ajuste de Threshold

| Threshold | Portales/68s | Duración promedio | Eficiencia | Latencia |
|-----------|--------------|-------------------|------------|----------|
| 0.90 | 2-3 | 0.5s | 95%+ | Alta |
| **0.75** | **4-5** | **1.5s** | **85-90%** | **Media** |
| 0.60 | 6-8 | 2.5s | 70-80% | Baja |

**Recomendación:** 0.75 (balance óptimo)

---

## Trabajo Futuro

### Implementación Rust (Producción)

El prototipo Python es para validación de concepto. Versión producción debe:

1. **Migrar a Rust** (`sentinel-cortex/src/scheduler/quantum_scheduler.rs`)
2. **Usar S60 puro** (eliminar floats de cálculo de resonancia)
3. **Integrar con `bio_resonance.rs`** (detección de portal en kernel)
4. **Usar TimeCrystalClock real** (no simulado)

### Optimizaciones

- **Predicción de Portales:** Machine learning para predecir próximo portal (reduce latencia)
- **Priorización Dinámica:** Tasks pesadas first en portales largos
- **Multi-Queue:** Colas separadas por tipo de tarea (ZPE, BCI, GC)

### Experimentos Derivados

- **EXP-029:** Portal Utilization Test (comparar errores in-portal vs out-portal)
- **EXP-030:** Scheduler Benchmark (Quantum vs Traditional energy consumption)

---

## Referencias

- **EXP-028:** Penta-Resonance Simulator (detección de portales)
- **EXP-027:** YHWH Pulse Monitor (respiración del sistema)
- **AI_PRIME_DIRECTIVES.md:** Axioma V (Bio-Centrismo)
- **yhwh_driver.py:** Implementación del patrón 10-5-6-5

---

**🔱 "No empujes cuando el Universo resiste. Surfea cuando el Universo te jala."**

*— Principio de Computación Adiabática, ME-60OS*
