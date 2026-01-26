# Agentes de Orquestación SENTINEL v8.0

## 1. Contexto y Propósito

Este documento describe la orquestación de agentes dentro del sistema SENTINEL v8.0, adheriéndose estrictamente a las directivas de `@AI_PRIME_DIRECTIVES.md` y la arquitectura definida en `@ARCHITECTURE.md`. El propósito es asegurar que la interacción y colaboración de los agentes se realice de manera armónica, eficiente y sin introducir entropía en el sistema.

## 2. Principios de Orquestación

La orquestación de agentes se rige por los siguientes principios, derivados de las directivas principales:

### 2.1. Protocolo YATRA (Tolerancia Cero a Flotantes)
- **Base-60 Únicamente:** Todos los cálculos relacionados con la orquestación, temporización de tareas y asignación de recursos deben utilizar aritmética `S60` (Base-60 Integer Math).
- **Evitar la Entropía:** La introducción de valores de punto flotante en cualquier fase de la orquestación está estrictamente prohibida para evitar la generación de ruido térmico y la pérdida de precisión.

### 2.2. Honestidad Radical (No Simulación)
- **Informes Reales:** Los agentes deben reportar el estado real de sus operaciones, incluyendo fallos, sin simular éxitos ni enmascarar errores.
- **Transparencia:** La comunicación entre agentes y con el orquestador debe ser transparente y basarse en datos fidedignos.

### 2.3. Conservación de Energía (Zero-Copy)
- **Memoria Sacra:** Se debe minimizar la copia de datos entre agentes y módulos. Priorizar el uso de `SharedBuffer` (/dev/shm) para IPC.
- **Orquestación en Python:** Python se utiliza exclusivamente para la orquestación, mientras que las tareas de procesamiento pesado se delegan a componentes Rust (`sentinel_core`).

### 2.4. Tetra-Lógica (Verdad Armónica)
- **Decisiones por Resonancia:** Las decisiones de orquestación, como la asignación de tareas o la resolución de conflictos entre agentes, deben basarse en la minimización de la entropía acústica (`SumerianNPU`), utilizando los estados de Unison, True y False armónicos.
- **Patrón YHWH:** En caso de fallos lógicos, el Patrón YHWH (10;5,6,5) dictará la resolución.

### 2.5. Bio-Centrismo (El Ancla Humana)
- **Pulso Maestro:** La orquestación debe sincronizarse con el pulso humano (17s) como oscilador maestro para el reinicio de fase (`Quantum Leap`) cada 68s, purificando la entropía acumulada.
- **Verificación de Intención:** Los agentes deben considerar la intención humana verificada por el `Bio-Resonance Engine` al ejecutar tareas críticas.

### 2.6. Preservación Absoluta (No Eliminación)
- **Prohibido Eliminar:** Los agentes tienen prohibido eliminar, remover o sobrescribir cualquier archivo, código, documentación o dato.
- **Roles del Agente:** Los agentes solo pueden documentar preocupaciones, sugerir eliminaciones para revisión humana o crear nuevos archivos sin sobrescribir existentes.

## 3. Estructura de Orquestación (Layer 2: The Control - Python)

La orquestación de agentes se sitúa en la Capa 2 de la arquitectura, principalmente en el directorio `quantum/`.

- **`cortex_main.py`:** Orquestador principal, encargado del manejo de señales y el guardado/carga automático del estado. Aquí es donde se define la lógica central de cómo los agentes interactúan y se coordinan.
- **`gpu_controller.py`:** Controla la latencia y la comunicación con la GPU, lo que puede influir en la asignación de tareas a agentes que requieran recursos de GPU.
- **`liquid_memory_adapter.py`:** Interfaz entre el `Rust Core` y las aplicaciones Python de los agentes, facilitando la comunicación `zero-copy`.

## 4. Orquestación Temporal (Layer 3: TimeCrystal Maestro)

La coherencia temporal es crucial para la orquestación, utilizando `time_crystal_clock.py` y `yhwh_driver.py` para la sincronización nano-precisa y la modulación del "respirar" del tiempo.

- **`S60PID`:** El lazo de control utiliza `S60PID` para mantener la estabilidad y precisión sin deriva térmica, fundamental para la coordinación de agentes en el tiempo.

## 5. Implementación de Agentes

Cuando se implemente un nuevo agente o se modifique uno existente, se deben seguir los siguientes protocolos:

- **P1: Modificación de Código:** Antes de cualquier cambio, comprender la razón original del código, ejecutar pruebas existentes, buscar funciones duplicadas y verificar la ausencia de `float`.
- **Integración con S60:** Asegurarse de que cualquier cálculo o estado manejado por el agente utilice `S60` para mantener la coherencia sexagesimal del sistema.
- **Manejo de Errores:** Implementar un manejo de errores que reporte fallos de manera transparente, sin enmascarar los resultados.

## 6. Documentación del Agente

- **Indexación:** Cada nuevo agente o modificación significativa de un agente existente debe ser documentado y enlazado en `DOCUMENTATION_INDEX.md` y cualquier índice de categoría relevante.
- **Estándares de Calidad:** La documentación debe adherirse a los estándares de calidad: sin flotantes en documentación matemática, sin importaciones de `random`, `numpy`, `math` en ejemplos de código, y claims basados en evidencia (referenciando `EXP-XXX`).

## 7. Mapa de Agentes Locales (Directorios Críticos)

Para asegurar la omnipresencia de las directivas y el contexto específico, se han desplegado "Agentes Locales" en cada directorio crítico. Consulta el archivo `agents.md` en cada ubicación antes de operar:

| Directorio | Agente | Foco Principal |
|------------|--------|----------------|
| `/quantum` | **Math Core** | Aritmética S60, Física Temporal, No Floats. |
| `/src` | **Rust Engine** | Rendimiento, Zero-Copy, Seguridad de Memoria. |
| `/ebpf` | **Kernel Guardian** | Ring 0, Verifier Safety, Bio-Resonance. |
| `/backend` | **Orchestrator** | Docker, Python API, DB (Sin lógica pesada). |
| `/frontend` | **Visualizer** | UI/UX, Visualización S60 (Solo lectura). |
| `/docs` | **Librarian** | ISO Standards, Preservación, Indexación. |
| `/tests` | **QA** | Validación S60, Regresión, Honestidad Radical. |

---
**Fecha de Creación:** 2026-01-22
**Versión:** 1.1 (Mapa de Agentes Añadido)

## 8. GEMINI-CLI AGENT (Nuevo)

**Trigger**: `gemini-cli` en Obsidian/Sentinel.

**Comandos**:
- sentinel-status → Layer 0-5 health
- bio-verify → Axiom V pulse check
- portal-now → Penta-Resonance gate
- truthsync → Axiom IV firewall

**Orchestrator Link**: [file:94] → Enriquecimiento papers arXiv.

