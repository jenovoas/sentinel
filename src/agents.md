# 🦀 AGENTE SRC: RUST CORE & MOTOR DE RENDIMIENTO

> **CONTEXTO:** Este directorio (`/src`) contiene el MOTOR (`sentinel_core`) de alto rendimiento. Aquí la eficiencia y la seguridad de memoria son ley.

## 1. 🛡️ DIRECTIVAS CRÍTICAS (NO NEGOCIABLES)

### 💎 AXIOMA III: MEMORIA SAGRADA (ZERO-COPY)
- **OBJETIVO:** 11GB RAM Total. Cada byte cuenta.
- **MÉTODO:** Usa `SharedBuffer` (/dev/shm) para IPC.
- **PROHIBIDO:** Copiar grandes volúmenes de datos entre procesos. Mapea la memoria.

### 🧱 AXIOMA I: TIPOS S60 NATIVOS
- **ESTRUCTURAS:** Usa `u60`, `s60` definidos en el crate.
- **ALINEACIÓN:** La memoria se alinea a bloques de 60, no potencias de 2 estándar si es posible.
- **ARITMÉTICA:** Implementa las operaciones matemáticas críticas aquí, NO en Python.

## 2. ⚙️ REGLAS DE DESARROLLO RUST

1. **Safety:** `unsafe` solo cuando sea estrictamente necesario para FFI o manipulación de memoria raw verificada.
2. **FFI:** Mantén la interfaz con Python (`cpython` / `pyo3`) limpia y mínima. La lógica pesada se queda en Rust.
3. **Tests:** Ejecuta `cargo test` religiosamente. La integridad matemática se valida aquí.
4. **Bio-Resonance:** `security/bio_resonance.rs` es CRÍTICO. No modifikes la lógica de 17s/68s sin autorización explícita.

## 3. 🔌 INTERFAZ CON EBPF

- **Bridge:** `ebpf_cortex_bridge.rs` conecta Ring 0 con User Space.
- **Latencia:** Objetivo < 100µs. Optimiza el polling del ring buffer.

## 4. 📂 MAPA DE CONOCIMIENTO

- **Core Logic:** `sentinel_core/` (o raíz de src dependiendo de la estructura actual).
- **Puente Python:** `lib.rs` (Exportaciones PyO3).
- **Seguridad:** `security/bio_resonance.rs` (Validación de pulso humano).

---
**RECORDATORIO:** "Si Python orquesta, Rust ejecuta." No muevas lógica de orquestación compleja aquí, solo cálculo puro y física.
