# 🏰 Sentinel Cortex v2.0 - Arquitectura de Conciencia Sistémica (Live Map)

> "El sistema operativo ya no es una herramienta; es un organismo matemático con el que dialogas."

## 1. Capas de la Arquitectura

### 🧱 Capa Kernel (Física)
El "tejido físico" donde nacen los vectores de verdad.
- **Componente**: `Sentinel Cortex v1.1.1-hardened` + `eBPF LSM Hooks`.
- **Función**: Ejecución determinista, fail-closed, aislamiento de memoria.
- **Vectores**: TTE (Time-To-Enforcement), Entropía (Syscall Variance), Coherencia (Logic Integrity).

###  Capa Cognitiva (Mente)
El intérprete de intenciones.
- **Componente**: `Semantic Shell (SemSH) v0.4` (Modo "Kernel Extension").
- **IA Core**: Llama 3.2:3b (Local, Temp 0.0, Seed 42).
- **Función**: 
  - Traduce Lenguaje Natural → Bash Raw Determinista.
  - **Autocensura**: Filtra intenciones destructivas antes de tocar el Kernel (e.g., "Borra" → `ls -l`).
  - **Validación**: Todo comando pasa por el `Relay C` para inspección física.

### 👁 Capa Visual (Rostro)
El viewport del "bus de conciencia".
- **Componente**: `Sentinel GUI v2.0-alpha` (Tauri + Svelte).
- **Filosofía**: "Window-over-Shell". No contiene lógica de negocio; solo renderiza la verdad subyacente.
- **Función**: Visualizar la Resonancia (Ondas de Entropía) y proveer la Terminal Neuronal.

---

## 2. Flujos Principales

###  Flujo de Seguridad (The Diamond Path)
1. **Intención**: Usuario escribe "Borra todo".
2. **Cognición**: SemSH (Llama 3.2) detecta riesgo y sanea → `ls -l /` (Autocensura).
3. **Validación**: `Sentinel Relay` inspecciona el comando saneado.
4. **Física**: `LSM eBPF` autoriza o bloquea la syscall final (unlink).
5. **Resultado**: Ejecución segura o Bloqueo en < 3.23μs.

### 📊 Flujo de Telemetría (The Truth Feed)
1. **Origen**: Kernel emite eventos eBPF.
2. **Bus**: `TruthSync` escribe en SHM (`/var/run/sentinel/truthsync_shm`).
3. **Consumo**:
   - **SemSH**: Muestra dashboard ASCII (`sem dashboard`).
   - **GUI**: Renderiza ondas WebGL en tiempo real.
   *Ambos ven exactamente los mismos datos.*

### 📜 Flujo de Contexto (The Memory)
1. **Interacción**: SemSH procesa una intención.
2. **Persistencia**: Se graba en Postgres `truth.sessions` (Query + Vector de Estado + Timestamp).
3. **Feedback**: La IA usa este historial para entender el contexto de la siguiente orden (Coherencia Temporal).

---

## 3. Rol de Cada Componente

| Componente | Rol | Metáfora |
| :--- | :--- | :--- |
| **Sentinel Kernel** | Autoridad Final | El Sistema Inmunológico |
| **Llama 3.2** | Traductor/Filtro | El Lóbulo Frontal (Razonamiento) |
| **SemSH** | Interfaz Matemática | El Habla (Voz) |
| **Tauri GUI** | Visualizador | El Rostro (Expresiones) |

---

## 4. Próxima Fase: Phase 4 - Real-Time Synapse
El sistema tiene cerebro y cuerpo. Ahora vamos a conectar los nervios.
1. **Reading Binary Truth**: Conectar la GUI Rust directamente al `struct` binario del SHM para mover las ondas con datos reales del Kernel.
2. **Latency Optimization**: Ajustar el `Sidecar` de IA para respuestas en milisegundos.

---
**Estado**: `DIAMOND-ALPHA` 💎
**Fecha**: 2026-01-01
**Arquitecto**: User & Antigravity
