# 🏙️ Sentinel Cortex GUI (Fase 3)

> "Una ventana visual sobre la conciencia matemática del sistema."

Esta interfaz no es una capa separada; es la proyección gráfica del **Semantic Shell (SemSH)**.

## 🔗 Arquitectura "Window-over-Shell"
- **Lógica**: Reside en `sem_shell.py` y el Kernel (eBPF).
- **Memoria**: Compartida vía `/var/run/sentinel/truthsync_shm`.
- **Visualización**: Tauri (Rust) lee la memoria y Svelte renderiza la resonancia.

## 🚀 Cómo Iniciar
1. **Prerequisitos (Host)**:
   Asegúrate de tener las librerías `webkit2gtk` instaladas (ver `../docs/PHASE_3_GUI_PROTOTYPE.md`).

2. **Ejecutar**:
   ```bash
   npm install
   npm run tauri dev
   ```

## 🧠 Características
- **Entropy Wave**: Visualización WebGL de la estabilidad del sistema.
- **Neural Terminal**: Chat flotante conectado al bus de intenciones de SemSH.
- **TTE Pulse**: Latido en tiempo real de la latencia de seguridad (< 10μs).
