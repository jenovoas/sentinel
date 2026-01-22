# 🛡️ AGENTE EBPF: GUARDIAN DEL KERNEL (RING 0)

> **CONTEXTO:** Este directorio (`/ebpf`) opera en el NIVEL MÁS BAJO del sistema (Kernel Linux). Un error aquí congela la máquina.

## 1. 🛡️ DIRECTIVAS CRÍTICAS (NO NEGOCIABLES)

### 👮 RESTRICCIONES DEL VERIFICADOR
- **LÍMITES:** Máximo 1 millón de instrucciones. Stack de 512 bytes.
- **BUCLES:** Prohibidos bucles infinitos o de límite variable. Todo debe ser determinista en compilación.
- **SEGURIDAD:** El código DEBE pasar el verificador. No uses "hacks" que comprometan la estabilidad del kernel.

### 🧬 AXIOMA V: BIO-CENTRISMO (Implementación)
- **MONITOREO:** Los probes eBPF deben respetar el ciclo de 17s/68s si interactúan con la planificación de procesos.
- **NO BLOQUEANTE:** El código eBPF nunca debe bloquear el sistema.

## 2. ⚙️ REGLAS DE DESARROLLO EBPF (C)

1. **Aritmética:** Aunque C usa binario, intenta mantener la lógica compatible con S60 donde sea posible (contadores, tiempos).
2. **Ring Buffer:** Usa el mapa de Ring Buffer para enviar eventos a Userspace (Cortex). No uses `perf_event_array` si puedes usar ring buffer (más eficiente).
3. **Mapas:** Define mapas estáticos. Limpia los mapas periódicamente desde userspace si no son LRU.
4. **Compilación:** Usa `clang` con target `bpf`. Verifica siempre con `bpftool prog load` antes de integrar.

## 3. 📂 ESTRUCTURA DE ARCHIVOS

- **Código Fuente:** `*.c` (Programas eBPF).
- **Headers:** `cortex_events.h` (Estructuras compartidas con Rust/Python). Es la verdad única de los datos.
- **Cargador:** `loader.c` o scripts externos para inyectar el código.

## 4. ⚠️ ADVERTENCIAS DE SEGURIDAD

- **Root:** Todo aquí requiere privilegios. Sé extremadamente cuidadoso con los comandos que sugieras.
- **Privacidad:** No captures contenido de usuario (teclas, pantalla) a menos que sea explícitamente para el `Bio-Resonance` y con privacidad total.

---
**OBJETIVO:** Observabilidad total con overhead cero. "Ver todo, no tocar nada (a menos que sea necesario)."
