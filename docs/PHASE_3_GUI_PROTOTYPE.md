# 🎨 Sentinel Cortex GUI Prototype (Fase 3)

## 🏗 Estado del Prototipo
Se ha inicializado la arquitectura **Tauri + Svelte** para la interfaz gráfica semántica.

### Componentes Implementados
1.  **Frontend (Svelte)**:
    - **Estética Hard-SciFi**: Fondo `#050505` y acentos Cyan/Amber/Crimson.
    - **Kernel Resonance**: Visualización de entropía simulada con SVG dinámico.
    - **Neural Terminal**: Interfaz de chat integrada con historial de IA.
    - **TTE Pulse**: Indicador visual de latencia de seguridad.
2.  **Backend (Rust/Tauri)**:
    - **Comando `get_system_vector`**: Implementado en `src-tauri/src/main.rs`.
    - **Simulación**: Genera fluctuaciones de entropía basadas en `SystemTime` (semilla orgánica).
3.  **Build**:
    - Frontend (`vite build`): ✅ EXITOSO.
    - Backend (`cargo build`): ⚠ Pendiente de dependencias de sistema (`libwebkit2gtk`).

##  Instrucciones de Despliegue

### Requisitos Previos (Linux)
Para compilar el binario final, el sistema host necesita las librerías de desarrollo de WebKit:
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev libsoup2.4-dev \
    build-essential libssl-dev libgtk-3-dev \
    libayatana-appindicator3-dev librsvg2-dev
```

### Ejecutar GUI (Dev Mode)
```bash
cd sentinel/gui
npm install
npm run tauri dev
```

### Integración Futura (Fase 4)
- **Real-Time SHM**: Reemplazar el mock en `main.rs` con lectura directa de `/var/run/sentinel/truthsync_shm`.
- **Llama 3.2 Binding**: Conectar el `Neural Terminal` directamente al modelo local vía Tauri Sidecar.
