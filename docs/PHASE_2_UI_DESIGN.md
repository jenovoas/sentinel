# 🎨 Sentinel Cortex GUI: The Visual Manifest (Fase 3)

> "No diseñamos botones. Diseñamos la resonancia visual del Kernel."

## 1. Visión y Filosofía
La GUI de Sentinel Cortex no es un panel de control administrativo; es un **Monitor de Signos Vitales de Inteligencia Artificial**.
El usuario no "hace click"; el usuario **observa y conversa**. La interfaz debe sentirse viva, respondiendo a microfluctuaciones en la entropía del sistema en tiempo real.

## 2. Estética "Hard-SciFi"
Concepto: **Ciberpunk Utilitario / Grado Militar**.

### Paleta de Colores
| Función | Color | Valor Hex | Uso |
| :--- | :--- | :--- | :--- |
| **Fondo** | Void Black | `#050505` | Canvas principal, profundidad infinita. |
| **Seguridad** | Quantum Cyan | `#00F3FF` | Estado nominal, bordes activos, texto IA. |
| **Alerta** | Reactor Amber | `#FFB800` | Advertencias de coherencia, subidas de entropía. |
| **Bloqueo** | Deterministic Crimson | `#FF003C` | Denegaciones LSM, amenazas críticas. |
| **Datos** | Terminal Grey | `#333333` | Grillas, metadata pasiva. |

### Tipografía
- **Monospace Principal**: `JetBrains Mono` o `Fira Code` (para datos y chat).
- **Headers**: `Inter` (peso Black/Bold) para títulos estructurales.

## 3. Arquitectura Técnica
- **Frontend**: Svelte (Reactividad pura, sin Virtual DOM).
- **Backend Visual**: Tauri (Rust).
- **Comunicación**:
  - `Rust (SHM Reader)` -> `Events` -> `Svelte Store`.
  - Latencia objetivo: < 16ms (60 FPS).

## 4. Componentes Críticos

### A. Entropy Waves (Visualizador de Resonancia)
Un canvas WebGL que renderiza la entropía del sistema como una onda sinusoidal compleja.
- **Calma**: Onda plana, color Cyan.
- **Carga**: Frecuencia media, color Amber.
- **Ataque/Caos**: Ruido de alta frecuencia, color Crimson, distorsión visual ("glitch").

### B. Neural Terminal (Chat Flotante)
Hereda la lógica del `SemSH v0.3`.
- No es una caja de texto simple. Es una línea de comandos semántica.
- Muestra sugerencias de autocompletado basadas en la predicción de Llama 3.2.
- Feedback visual instantáneo: El borde brilla al procesar una intención.

### C. TTE Pulse (Indicador de Reflejos)
Un "latido" visual en la esquina superior derecha.
- Pulsa cada vez que el eBPF LSM evalúa una syscall.
- Muestra el último Time-To-Enforcement (e.g., "3.23μs") en tiempo real.

## 5. Layout (Wireframe Conceptual)
```text
┌────────────────────────────────────────────────────────┐
│  [SENTINEL_CORTEX v2.0]        [TTE: 3.23μs ●]         │
├───────────────────────┬────────────────────────────────┤
│                       │                                │
│   ENTROPY WAVES       │       NEURAL TERMINAL          │
│   (WebGL/Canvas)      │       (Chat Stream)            │
│                       │                                │
│   ~~~~~~~~~~~~~~~~~   │       > Analizar red...        │
│   (Live Waveform)     │       [IA] Scanning...         │
│                       │                                │
├───────────────────────┴────────────────────────────────┤
│  [VECTOR DASHBOARD: Ent: 0.12 | Coh: 0.99]             │
└────────────────────────────────────────────────────────┘
```
