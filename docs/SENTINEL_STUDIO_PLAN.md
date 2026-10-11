#  Sentinel Studio: The Sovereign IDE Architecture

## 1. Visión
Sentinel Studio es un fork optimizado de **VSCodium** diseñado específicamente para la ingeniería de defensa de Sentinel Cortex. Su objetivo es eliminar la fricción entre el desarrollo de código (C/Python/eBPF) y la validación en tiempo real (VMs/Appliance/Hardware).

---

## 2. Componentes Críticos (Fases de Implementación)

### Fase 1: Observabilidad de Infraestructura (The "No-More-Blindness" Phase)
- [ ] **Sentinel VNC Bridge**: Un panel lateral que se conecta automáticamente a los puertos VNC dinámicos de Packer (`5900-6000`).
- [x] **Provisioning Tracker**: Sistema de monitoreo de logs (`packer_build.log`) y RAM activo.
- [x] **Sctl Unified Observability**: Terminal integrada con soporte para vectores semánticos (Entropy, Coherence, Truth Score).

### Fase 2: Desarrollo eBPF & AI (The "Cortex" Phase)
- [ ] **LSM Policy Visualizer**: Gráfico de nodos que muestra qué binarios están siendo bloqueados y por qué reglas.
- [ ] **eBPF Bytecode Inspector**: Ver el código ensamblador de los programas cargados en el kernel.
- [x] **Cognitive Loop Debugger**: Debugger para la lógica de IA que permite ver los vectores de amenaza en tiempo real (Integrado en `sctl status`).

### Fase 3: Interfaz & UX (The "Qualia" Phase)
- [ ] **Sentinel Theme**: Paleta de colores optimizada para largas sesiones de monitoreo (Deep Black, Neon Cyan, Emergency Amber).
- [ ] **Audio Feedback Integration**: Sonidos sutiles para indicar "Build Success" o "Threat Detected" (vinculado a la BCI).

---

## 3. Roadmap de Desarrollo

### Iteración 0 (Próxima semana)
- Crear el repositorio `sentinel-studio`.
- Configurar el `vscode-pack` básico con extensiones imprescindibles (C/C++, Python, HCL).

### Iteración 1 (Build Focus)
- Script de bootstrapping para instalar Sentinel Studio en Debian Trixie con todas las dependencias de QEMU/KVM.

---

## 4. Por qué un Fork y no solo una Extensión?
Sentinel requiere acceso a bajo nivel (puntos de montaje, `/dev/ttyS1`, sockets de Docker, eBPF maps). Un fork nos permite pre-otorgar estas capacidades de forma segura y optimizar el consumo de recursos para que el IDE no compita con las VMs de prueba.

---

> "Build the tools that defend the code." — Sentinel Manifesto
