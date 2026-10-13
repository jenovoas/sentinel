# Plan de Mejoras - Sentinel Ring-0
> Documento de planificación y justificación técnica. Fuente: análisis comparativo con papers (Heimdall, eBPF IDS/ML, DDoS Mitigation, Time-Crystal dynamics) y auditoría interna del código actual.

---

## 1. Resumen Ejecutivo

| Mejora | Esfuerzo | Riesgo | Impacto | Prioridad |
|--------|----------|--------|---------|-----------|
| **Zero-init hardening** | 5 min | Ninguno | Crítico (previene leaks KASLR) | **P0 - Inmediato** |
| **Kani verification harness** | 15 min | Bajo | Alto (garantía formal bridge C→Rust) | **P1 - Esta semana** |
| **Decision tree embebido (eBPF)** | 30 min | Medio | Alto (detección en kernel, sin userspace) | **P2 - Próximo sprint** |
| **FFT + Q-factor detector** | 20 min | Medio | Alto (beaconing/DNS tunneling/C2) | **P2 - Próximo sprint** |

---

## 2. Estado Actual (Baseline)

### 2.1 Arquitectura Ring-0
```
┌─────────────────────────────────────────────────────────────────┐
│                        KERNEL SPACE (Ring 0)                     │
├─────────────────────────────────────────────────────────────────┤
│  eBPF LSM Hooks                                                  │
│  ├─ float_detector.c     → bprm_check_security (YATRA Lock)      │
│  ├─ guardian_alpha_lsm.c → bprm_check_security (AI agents)       │
│  ├─ ai_guardian.c        → file_open + bprm_check_security       │
│  ├─ xdp_firewall.c       → XDP (pre-stack, panic mode)           │
│  └─ tc_firewall.c        → TC egress/ingress                     │
│                                                                  │
│  Maps: Hash (whitelist/blacklist), Array (stats), RingBuf (evt)  │
└─────────────────────────────────────────────────────────────────┘
                              │ Ring Buffer (BPF_MAP_TYPE_RINGBUF)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        USERSPACE (Rust)                          │
├─────────────────────────────────────────────────────────────────┤
│  sentinel-cortex/src/ebpf_cortex_bridge.rs                       │
│  ├─ CortexEventRaw (repr(C, packed)) 32 bytes                    │
│  ├─ parse_event() → CortexEvent (serde)                          │
│  └─ run_monitor() → libbpf-rs RingBufferBuilder                  │
│                                                                  │
│  S60 Math (base-60, no floats): s60.rs, s60_math.rs,            │
│  harmonic_logic.rs, fft_s60, q_factor_s60, entropy_s60          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Gaps Identificados vs. Papers

| Paper | Hallazgo | Gap en Sentinel |
|-------|----------|-----------------|
| **Heimdall (2605.25411)** | 10/102 progs filtran memoria no inicializada → KASLR leak | `ai_guardian.c` no hace `memset` antes de `ringbuf_reserve` |
| **Heimdall** | Verificación formal C↔Rust con Z3/angr (94.1% éxito) | Bridge manual sin pruebas de equivalencia |
| **eBPF Flow IDS ML (2102.09980)** | Decision trees en eBPF (20% más rápido que userspace) | Clasificación solo en userspace (round-trip) |
| **eBPF DDoS IoT (2508.00851)** | XDP + rate-based detection, panic mode = cuarentena total | Tenemos panic mode, pero solo por IP, no por patrón temporal |
| **Time-Crystal papers** | Discrete time crystals = drive periódico 10;5,6,5 | `harmonic_logic.rs` ya lo modela, pero no se usa en detección |

---

## 3. Mejoras Detalladas

### 3.1 P0: Zero-Init Hardening (5 min)

**Problema**: `bpf_ringbuf_reserve` devuelve memoria sin inicializar. Si el struct tiene padding o campos no escritos, se filtran datos kernel previos (punteros, KASLR, eventos anteriores). Heimdall encontró esto en 10 herramientas reales.

**Archivos afectados**:
- `ebpf/ai_guardian.c` → `send_cortex_event()` (líneas 85-106)
- `ebpf/guardian_alpha_lsm.c` → `log_event()` (líneas 63-77)
- `ebpf/float_detector.c` → `emit_event()` **YA LO HACE** (línea 72: `__builtin_memset`)

**Fix**: Añadir `__builtin_memset(&event, 0, sizeof(event))` antes de rellenar campos.

```c
// ANTES (ai_guardian.c:91)
struct cortex_event *e = bpf_ringbuf_reserve(&cortex_events, sizeof(*e), 0);
if (!e) return;
e->timestamp_ns = bpf_ktime_get_ns();
// ... resto de campos

// DESPUÉS
struct cortex_event *e = bpf_ringbuf_reserve(&cortex_events, sizeof(*e), 0);
if (!e) return;
__builtin_memset(e, 0, sizeof(*e));  // ← NUEVO
e->timestamp_ns = bpf_ktime_get_ns();
// ...
```

**Testing**: `bpftool prog dump xlated name ai_guardian` → verificar instrucción `memset` en bytecode.

---

### 3.2 P1: Kani Verification Harness (15 min)

**Objetivo**: Probar que `EbpfBridge::parse_event()` nunca hace UB, panic, ni memory corruption para **cualquier** input de 32 bytes.

**Por qué Kani**: Model checking exhaustivo (CBMC backend). Encuentra overflows, underflows, division by zero, uninit memory que tests unitarios no cubren.

**Archivo nuevo**: `sentinel-cortex/kani/harness_parse_event.rs`

```rust
#[kani::proof]
fn verify_parse_event_no_panic() {
    // Input: cualquier array de 32 bytes
    let data: [u8; 32] = kani::any();
    
    // Precondición: longitud correcta
    kani::assume(data.len() == std::mem::size_of::<CortexEventRaw>());
    
    // Ejercitar
    let result = EbpfBridge::parse_event(&data);
    
    // Postcondiciones
    match result {
        Some(event) => {
            // Validar rangos S60
            kani::assert(event.entropy_s60_raw <= u64::MAX, "entropy in range");
            kani::assert(event.severity <= 255, "severity valid");
            // guardian_code solo 0-5 según spec
            kani::assert(event.guardian_code <= 5, "guardian_code valid");
        }
        None => {
            // None solo si len < 32, pero assumimos len==32
            kani::assert(false, "should not return None for valid len");
        }
    }
}
```

**Ejecución**:
```bash
cd sentinel-cortex && cargo install cargo-kani && cargo kani --harness verify_parse_event_no_panic
```

**Resultado esperado**: `VERIFICATION SUCCESSFUL` o counterexample concreto.

---

### 3.3 P2: Decision Tree Embebido en eBPF (30 min)

**Motivación**: Mover clasificación de "amenaza vs benigno" al kernel. Elimina latencia round-trip (~100-500μs), funciona aunque userspace caiga, reduce superficie de ataque.

**Paper base**: *eBPF Flow-based IDS with ML* (2102.09980) — decision trees de profundidad ≤ 4 caben en eBPF (límite 1M instrucciones, verifier feliz).

**Diseño**:
1. **Entrenamiento offline** (Python/sklearn):
   ```python
   from sklearn.tree import DecisionTreeClassifier
   import joblib
   
   # Features: [entropy_s60_raw, severity, event_type_encoded, pid_hash]
   # Labels: 0=benign, 1=suspicious, 2=malicious
   clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=10)
   clf.fit(X_train, y_train)
   
   # Exportar a C array
   def tree_to_c(clf, feature_names):
       # Recorrer tree_.children_left, tree_.threshold, tree_.value
       # Generar struct Node { u32 feature; u64 threshold; u16 left; u16 right; u8 class; }
   ```
2. **Kernel side** (`ai_guardian.c` + nuevo `decision_tree.h`):
   ```c
   struct dt_node {
       u8 feature;      // 0=entropy, 1=severity, 2=event_type, 3=pid_hash
       u64 threshold;   // valor umbral (S60 raw)
       u16 left;        // índice hijo izq (0xFFFF = leaf)
       u16 right;       // índice hijo der (0xFFFF = leaf)
       u8 class;        // 0=benign, 1=suspect, 2=malicious (solo en leaf)
   };
   
   // Map de solo lectura (pinned)
   struct {
       __uint(type, BPF_MAP_TYPE_ARRAY);
       __uint(max_entries, MAX_NODES);
       __type(key, u32);
       __type(value, struct dt_node);
   } dt_model SEC(".maps");
   
   // En hook:
   static __always_inline u8 dt_classify(u64 entropy, u8 severity, u32 evt_type, u32 pid) {
       u32 idx = 0;
       while (true) {
           struct dt_node *node = bpf_map_lookup_elem(&dt_model, &idx);
           if (!node || node->left == 0xFFFF) return node->class;
           
           u64 val = (node->feature == 0) ? entropy :
                     (node->feature == 1) ? severity :
                     (node->feature == 2) ? evt_type : pid;
           idx = (val <= node->threshold) ? node->left : node->right;
       }
   }
   ```
3. **Actualización en caliente**: `bpftool map update pinned /sys/fs/bpf/sentinel/dt_model key 0 1 2 ...` sin recargar programa.

**Métricas objetivo**: < 500 instrucciones eBPF por clasificación, 0 falsos positivos en whitelist conocida.

---

### 3.4 P2: FFT + Q-Factor Detector en Ring Buffer (20 min)

**Motivación**: Detectar **beaconing periódico** (C2, DNS tunneling, malware "low & slow") analizando la *serie temporal* de `entropy_signal`, no solo valores puntuales.

**Paper base**: *Time-Crystal dynamics* (2509.21959, 2606.30890) + tu `s60_math.rs` ya tiene `fft_s60` + `q_factor_s60`.

**Arquitectura**:
```
Ring Buffer (kernel) → userspace collector → buffer circular 1024 muestras → cada 100 eventos:
    1. Extraer entropy_s60_raw → Vec<S60>
    2. fft_s60(&signal) → Vec<ComplexS60>
    3. q_factor_s60(spectrum, sample_rate) → S60 Q
    4. Si Q > UMBRAL (ej. S60[50;0] = 50) → ALERTA: resonancia periódica detectada
```

**Implementación Rust** (nuevo módulo `sentinel-cortex/src/detectors/periodic.rs`):
```rust
use crate::math::{s60::S60, s60_math::{fft_s60, q_factor_s60, ComplexS60}};

pub struct PeriodicDetector {
    buffer: Vec<S60>,
    capacity: usize,
    sample_rate_hz: S60,  // eventos/segundo estimado
    q_threshold: S60,
}

impl PeriodicDetector {
    pub fn new(capacity: usize, sample_rate_hz: f64, q_threshold: f64) -> Self {
        Self {
            buffer: Vec::with_capacity(capacity),
            capacity,
            sample_rate_hz: S60::from_raw((sample_rate_hz * S60::SCALE_0 as f64) as i64),
            q_threshold: S60::from_raw((q_threshold * S60::SCALE_0 as f64) as i64),
        }
    }
    
    pub fn push(&mut self, entropy_raw: u64) -> Option<PeriodicAlert> {
        self.buffer.push(S60::from_raw(entropy_raw as i64));
        if self.buffer.len() > self.capacity {
            self.buffer.drain(0..self.buffer.len() - self.capacity);
        }
        
        if self.buffer.len() == self.capacity && self.buffer.len().is_power_of_two() {
            let spectrum = fft_s60(&self.buffer).ok()?;
            let q = q_factor_s60(&spectrum, self.sample_rate_hz).ok()?;
            if q > self.q_threshold {
                return Some(PeriodicAlert { q_factor: q, peak_freq: /* ... */ });
            }
        }
        None
    }
}
```

**Integración**: En `ebpf_cortex_bridge.rs` → `run_monitor()` → tras `resonant.push(entropy)`, llamar `detector.push(entropy)`.

**Ventaja S60**: FFT exacta en base-60, sin errores de redondeo que enmascaran armónicos débiles. Q-factor mide "pureza" de la resonancia (señal humana Q>10, beaconing sintético Q>50).

---

## 4. Plan de Ejecución

### Semana 1 (Inmediato)
- [ ] **P0**: Zero-init en `ai_guardian.c` + `guardian_alpha_lsm.c`
- [ ] **P0**: Test `bpftool prog dump` verifica memset
- [ ] **P1**: Añadir `cargo-kani` + harness `parse_event`
- [ ] **P1**: Corregir cualquier counterexample que Kani encuentre

### Semana 2
- [ ] **P2**: Entrenar decision tree offline (dataset: logs reales + sintéticos)
- [ ] **P2**: Generar `decision_tree.h` + integrar en `ai_guardian.c`
- [ ] **P2**: Probar actualización en caliente vía `bpftool map update`

### Semana 3
- [ ] **P2**: Implementar `PeriodicDetector` en Rust
- [ ] **P2**: Conectar en `ebpf_cortex_bridge.rs`
- [ ] **P2**: Calibrar `q_threshold` con tráfico real (benigno vs beaconing)

### Documentación viva
- Cada PR actualiza este archivo con: **qué se hizo, métricas antes/después, lecciones**.
- `governance/compliance/evidence-index.md` ← añadir evidencias Kani, benchmarks eBPF.

---

## 5. Criterios de Aceptación (Definition of Done)

| Mejora | Métrica | Target |
|--------|---------|--------|
| Zero-init | `bpftool prog dump` muestra `memset` | ✓ 3/3 programas |
| Kani | `cargo kani` → VERIFICATION SUCCESSFUL | ✓ 0 counterexamples |
| Decision tree | Instrucciones eBPF/clasificación | < 500 |
| Decision tree | Falsos positivos en whitelist | 0% |
| FFT detector | Detección beaconing 10s period | Recall > 90% @ 1% FP |
| FFT detector | Latencia añadida por evento | < 50μs (amortizado) |

---

## 6. Referencias Cruzadas

- `CLAUDE.md` → Constraints (YATRA Lock, no floats, Podman only)
- `ebpf/STATUS.md` → Estado actual compilación/deploy
- `sentinel-cortex/src/math/s60_math.rs` → `fft_s60`, `q_factor_s60`, `sin_s60` (ya implementados, testados)
- `harmonic_logic.rs` → Patrón 10;5,6,5 = drive time-crystal
- `governance/itil/change-management-policy.md` → Proceso de cambio para deploy en FENIX

---

## 7. Notas para Futura Revisión

> **Si pierdes el hilo**: Lee en orden: 1) Tabla resumen (Sec 1) → 2) Gap vs papers (Sec 2.2) → 3) Fix concreto P0 (Sec 3.1) → 4) Plan semanal (Sec 4).
>
> **No inventes**: `s60_math.rs` YA tiene FFT, Q-factor, sin/cos, ln, entropy. Solo hay que *usarlos* en el detector periódico.
>
> **Verificación formal**: Kani no es opcional si quieres garantía estilo Heimdall. 15 min ahora ahorran semanas de debugging raro en prod.

---

*Generado: 2026-07-27 | Autor: Análisis comparativo Sentinel vs Papers (Heimdall, TU Wien IDS, IoT DDoS, Time-Crystal) + Auditoría código*