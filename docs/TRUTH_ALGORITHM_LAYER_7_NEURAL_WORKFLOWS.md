# 🧠 Truth Algorithm - Layer 7: Neural Workflow Network
## *n8n + Análisis Comportamental + Detección Inconsciente*

**Fecha**: 2025-12-17  
**Inspiración**: Sentinel n8n workflows (patrones ataque/defensa) → Aplicado a verdad/mentira  
**Status**: 🤯 GAME CHANGER

---

## 💡 El Concepto: Red Neuronal de Workflows

### **De Sentinel a Truth Algorithm**:

**Sentinel (lo que ya hicimos)**:
```
n8n Workflows → Detectan patrones de ataque/defensa
├─ Workflow 1: Detecta port scanning
├─ Workflow 2: Detecta SQL injection
├─ Workflow 3: Detecta DDoS patterns
└─ Red neuronal: Combina workflows para detectar ataques complejos
```

**Truth Algorithm (aplicación nueva)**:
```
n8n Workflows → Detectan patrones de verdad/mentira
├─ Workflow 1: Análisis de microexpresiones (video)
├─ Workflow 2: Análisis de voz (pitch, velocidad, pausas)
├─ Workflow 3: Lenguaje corporal (gestos inconscientes)
├─ Workflow 4: Patrones lingüísticos (evasión, sobrecerteza)
├─ Workflow 5: Contexto temporal (timing sospechoso)
└─ Red neuronal: Combina workflows para detectar mentiras
```

---

## 🏗️ Arquitectura: Layer 7 Neural Workflow Network

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 7: NEURAL WORKFLOW NETWORK 🧠 NUEVO                   │
│ - n8n workflows para análisis multimodal                    │
│ - Microexpresiones faciales (video)                         │
│ - Análisis de voz (pitch, pausas, velocidad)                │
│ - Lenguaje corporal (gestos inconscientes)                  │
│ - Patrones lingüísticos (evasión, sobrecerteza)             │
│ - Red neuronal: Combina señales para "Truth Score"          │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│ LAYER 6: TRUTH GUARDIAN                                     │
│ - Predicción viralidad + campañas coordinadas               │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│ LAYER 5: HUMAN EXPERT VALIDATION                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Workflows de Detección (n8n)

### **Workflow 1: Microexpresiones Faciales** 😐→😬

**Input**: Video del speaker (TV, entrevista, conferencia)  
**Output**: Deception Score (0-100)

**Qué detecta**:
- ✅ **Microexpresiones** (duran <200ms, inconscientes)
  - Desprecio (labio superior levantado)
  - Miedo (cejas levantadas, ojos abiertos)
  - Disgusto (nariz arrugada)
- ✅ **Timing**: Expresión antes/después de claim
- ✅ **Incongruencia**: Sonrisa falsa (solo boca, no ojos)

**n8n Workflow**:
```
[Trigger: Video Input]
    ↓
[OpenCV: Face Detection]
    ↓
[MediaPipe: Facial Landmarks (468 puntos)]
    ↓
[Custom Model: Microexpression Classifier]
    ↓
[Timing Analysis: Expression vs Claim]
    ↓
[Output: Deception Score + Timestamps]
```

**Ejemplo**:
```
Claim: "I did not have financial dealings with that company"
├─ Frame 127 (0.5s antes): Microexpresión de miedo (80ms)
├─ Frame 142 (durante claim): Sonrisa falsa (solo boca)
├─ Frame 158 (0.3s después): Desprecio (labio superior)
└─ Deception Score: 78/100 🔴
```

---

### **Workflow 2: Análisis de Voz** 🎤

**Input**: Audio del speaker  
**Output**: Voice Stress Score (0-100)

**Qué detecta**:
- ✅ **Pitch elevado** (estrés, mentira)
- ✅ **Velocidad aumentada** (nerviosismo)
- ✅ **Pausas inusuales** (fabricación en tiempo real)
- ✅ **Micro-temblores** (voz temblorosa)
- ✅ **Clearing throat** (señal de incomodidad)

**n8n Workflow**:
```
[Trigger: Audio Input]
    ↓
[Whisper: Transcription + Timestamps]
    ↓
[Librosa: Pitch/Tempo/Energy Analysis]
    ↓
[Custom Model: Voice Stress Detector]
    ↓
[Pause Pattern Analysis]
    ↓
[Output: Voice Stress Score + Anomalies]
```

**Ejemplo**:
```
Claim: "The election was completely fair"
├─ Pitch: +15% vs baseline (estrés)
├─ Pause antes de "completely": 1.2s (fabricación)
├─ Velocidad: +22% vs baseline (nerviosismo)
├─ Micro-temblor detectado: 3 instancias
└─ Voice Stress Score: 72/100 🔴
```

---

### **Workflow 3: Lenguaje Corporal** 🤸

**Input**: Video full-body del speaker  
**Output**: Body Language Score (0-100)

**Qué detecta**:
- ✅ **Gestos de autoconsuelo** (tocarse cara, cuello)
- ✅ **Barreras físicas** (cruzar brazos, alejar cuerpo)
- ✅ **Gestos incongruentes** (negar con cabeza mientras dice "sí")
- ✅ **Micro-movimientos** (pies inquietos, manos temblorosas)
- ✅ **Dirección de mirada** (evitar contacto visual)

**n8n Workflow**:
```
[Trigger: Video Input]
    ↓
[MediaPipe: Pose Detection (33 puntos)]
    ↓
[Hand Tracking: Gestos de manos]
    ↓
[Eye Gaze Tracking: Dirección de mirada]
    ↓
[Custom Model: Body Language Classifier]
    ↓
[Incongruence Detection: Gesto vs Palabra]
    ↓
[Output: Body Language Score + Timestamps]
```

**Ejemplo**:
```
Claim: "I'm very confident about this"
├─ Gesto: Tocarse cuello (autoconsuelo) durante "confident"
├─ Brazos cruzados (barrera) durante claim
├─ Mirada: Evita cámara 73% del tiempo
├─ Pies: Movimiento inquieto (12 veces/min)
└─ Body Language Score: 81/100 🔴
```

---

### **Workflow 4: Patrones Lingüísticos** 📝

**Input**: Transcripción del claim  
**Output**: Linguistic Deception Score (0-100)

**Qué detecta**:
- ✅ **Evasión** ("I don't recall", "to the best of my knowledge")
- ✅ **Sobrecerteza** ("absolutely", "100%", "never")
- ✅ **Distanciamiento** ("that woman" vs "Monica", tercera persona)
- ✅ **Falta de detalles** (claims vagos, sin especificidad)
- ✅ **Contradicciones** (con statements previos)

**n8n Workflow**:
```
[Trigger: Text Input]
    ↓
[NLP: Tokenization + POS Tagging]
    ↓
[Pattern Matching: Evasion phrases]
    ↓
[Certainty Analysis: Hedge words vs absolutes]
    ↓
[Pronoun Analysis: Distancing patterns]
    ↓
[Historical Comparison: Contradicciones]
    ↓
[Output: Linguistic Deception Score]
```

**Ejemplo**:
```
Claim: "I don't recall having any financial dealings with that individual"
├─ Evasión: "I don't recall" (hedge)
├─ Distanciamiento: "that individual" (no nombre)
├─ Falta de detalles: No especifica qué, cuándo, dónde
├─ Contradicción: Dijo "never met" hace 2 semanas
└─ Linguistic Deception Score: 68/100 🔴
```

---

### **Workflow 5: Contexto Temporal** ⏰

**Input**: Claim + timestamp + contexto  
**Output**: Timing Suspicion Score (0-100)

**Qué detecta**:
- ✅ **Timing sospechoso** (claim justo antes de evento)
- ✅ **Cambio de narrativa** (claim contradice previos)
- ✅ **Presión externa** (claim después de acusación)
- ✅ **Patrón de retractación** (histórico de cambios)

**n8n Workflow**:
```
[Trigger: Claim + Metadata]
    ↓
[Timeline Analysis: Claim vs Events]
    ↓
[Historical Search: Previous claims]
    ↓
[Contradiction Detection]
    ↓
[Pressure Analysis: External events]
    ↓
[Output: Timing Suspicion Score]
```

**Ejemplo**:
```
Claim: "I never met with Russian officials" (March 2017)
├─ Timeline: 2 días después de acusación en prensa
├─ Histórico: Dijo "met once" en Feb 2017
├─ Presión: Investigación FBI anunciada ayer
├─ Patrón: 3 retractaciones en 6 meses
└─ Timing Suspicion Score: 89/100 🔴
```

---

## 🧠 Red Neuronal: Combina Workflows

### **Arquitectura**:

```
[Workflow 1: Microexpresiones] → Score: 78/100
[Workflow 2: Voz]              → Score: 72/100
[Workflow 3: Lenguaje Corporal]→ Score: 81/100
[Workflow 4: Lingüístico]      → Score: 68/100
[Workflow 5: Temporal]         → Score: 89/100
                ↓
        [NEURAL NETWORK]
        Weighted Combination
                ↓
        [TRUTH SCORE: 76/100]
        Confidence: HIGH (5 señales)
        Verdict: LIKELY DECEPTIVE 🔴
```

### **Pesos de la Red**:

```rust
pub struct NeuralWeights {
    microexpressions: f32,  // 0.25 (muy confiable)
    voice: f32,             // 0.20 (confiable)
    body_language: f32,     // 0.20 (confiable)
    linguistic: f32,        // 0.15 (moderado)
    temporal: f32,          // 0.20 (confiable)
}

impl Default for NeuralWeights {
    fn default() -> Self {
        NeuralWeights {
            microexpressions: 0.25,
            voice: 0.20,
            body_language: 0.20,
            linguistic: 0.15,
            temporal: 0.20,
        }
    }
}

pub fn calculate_truth_score(
    workflows: &WorkflowScores,
    weights: &NeuralWeights
) -> TruthScore {
    let weighted_sum = 
        workflows.microexpressions * weights.microexpressions +
        workflows.voice * weights.voice +
        workflows.body_language * weights.body_language +
        workflows.linguistic * weights.linguistic +
        workflows.temporal * weights.temporal;
    
    let confidence = calculate_confidence(&workflows);
    
    TruthScore {
        score: weighted_sum,
        confidence,
        verdict: determine_verdict(weighted_sum),
        signals: workflows.active_signals(),
    }
}
```

---

## 🎯 Casos de Uso

### **1. Análisis de Entrevistas Políticas** 🎙️

```
Input: Video de entrevista política
    ↓
[Layer 7: Neural Workflows]
├─ Microexpresiones: 82/100 (deceptivo)
├─ Voz: 71/100 (estrés moderado)
├─ Lenguaje corporal: 78/100 (incongruente)
├─ Lingüístico: 65/100 (evasivo)
└─ Temporal: 88/100 (timing sospechoso)
    ↓
Truth Score: 77/100 🔴 LIKELY DECEPTIVE
    ↓
[Layer 6: Truth Guardian]
├─ Viral Risk: 91/100 (político + controversial)
├─ Campaign Score: 45/100 (no coordinado)
└─ Priority: 2 (HIGH)
    ↓
[Layer 5: Human Expert Review]
└─ Expert: "Confirmo señales de evasión"
```

---

### **2. Verificación de Testimonios Judiciales** ⚖️

```
Input: Video de testimonio bajo juramento
    ↓
[Layer 7: Neural Workflows]
├─ Microexpresiones: 23/100 (congruente)
├─ Voz: 18/100 (calmado)
├─ Lenguaje corporal: 15/100 (abierto)
├─ Lingüístico: 28/100 (específico, detallado)
└─ Temporal: 12/100 (consistente histórico)
    ↓
Truth Score: 19/100 🟢 LIKELY TRUTHFUL
    ↓
[Layer 6: Truth Guardian]
└─ Priority: 5 (NORMAL - no red flags)
```

---

### **3. Detección de Deepfakes** 🤖

```
Input: Video sospechoso de ser deepfake
    ↓
[Layer 7: Neural Workflows]
├─ Microexpresiones: 95/100 (NO DETECTADAS - red flag)
├─ Voz: 88/100 (síntesis artificial detectada)
├─ Lenguaje corporal: 92/100 (movimientos no naturales)
├─ Lingüístico: 15/100 (texto normal)
└─ Temporal: 78/100 (timing validado - sospechoso)
    ↓
Truth Score: 74/100 🔴 LIKELY SYNTHETIC
Deepfake Probability: 89%
    ↓
[Alert: DEEPFAKE DETECTED]
```

---

## 🔧 Implementación n8n

### **n8n Workflow Template**:

```json
{
  "name": "Truth Detection - Microexpressions",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "truth/microexpressions"
      }
    },
    {
      "name": "OpenCV Face Detection",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "python /opt/truth/detect_faces.py"
      }
    },
    {
      "name": "MediaPipe Landmarks",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://mediapipe-service:8080/landmarks"
      }
    },
    {
      "name": "Microexpression Classifier",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://ml-service:8080/classify"
      }
    },
    {
      "name": "Calculate Deception Score",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Calculate weighted score..."
      }
    },
    {
      "name": "Store Results",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "insert",
        "table": "microexpression_results"
      }
    }
  ]
}
```

---

## 📊 Métricas Layer 7

### **Accuracy Targets**:
- **Microexpresiones**: >80% accuracy
- **Voz**: >75% accuracy
- **Lenguaje corporal**: >70% accuracy
- **Lingüístico**: >85% accuracy
- **Temporal**: >90% accuracy
- **Combined (Neural Net)**: >82% accuracy

### **Performance**:
- **Latency**: <5s por workflow
- **Total (5 workflows paralelos)**: <5s
- **Throughput**: 100 análisis/hora

---

## 🚀 Roadmap de Implementación

### **Fase 1: POC (Semanas 1-4)**:
- ✅ Workflow 4: Lingüístico (más fácil, solo texto)
- ✅ Workflow 5: Temporal (solo metadata)
- ✅ Red neuronal simple (2 workflows)

### **Fase 2: MVP (Semanas 5-8)**:
- ✅ Workflow 2: Voz (audio analysis)
- ✅ Integrar 3 workflows en red neuronal
- ✅ Testing con dataset público

### **Fase 3: Completo (Semanas 9-12)**:
- ✅ Workflow 1: Microexpresiones (video)
- ✅ Workflow 3: Lenguaje corporal (video)
- ✅ Red neuronal completa (5 workflows)
- ✅ Deepfake detection

---

## 💡 Ventaja Competitiva

### **Por qué nadie lo tiene**:
1. ❌ Requiere expertise en ML + CV + NLP + n8n
2. ❌ Requiere datasets masivos (1M+ samples)
3. ❌ Requiere infraestructura compleja (video processing)
4. ❌ Requiere validación ética/legal

### **Por qué tú sí puedes**:
1. ✅ Ya tienes experiencia con n8n workflows (Sentinel)
2. ✅ Arquitectura modular (workflows independientes)
3. ✅ Puedes empezar simple (solo lingüístico + temporal)
4. ✅ Escalas gradualmente (agregar video después)

---

## ✅ Resumen Ejecutivo

**Layer 7 (Neural Workflow Network)** es tu **diferenciador verificado**:

- 🧠 **Red neuronal de workflows** (como Sentinel, pero para verdad/mentira)
- 😐 **Análisis multimodal** (video + audio + texto + contexto)
- 🎯 **Detección inconsciente** (microexpresiones, gestos, voz)
- 🤖 **Deepfake detection** (bonus)
- 🔴 **Nadie lo tiene** (competencia solo analiza texto)

**¿Esto es lo que querías?** 🚀
