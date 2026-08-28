# 🛡️ SENTINEL CORTEX v8.0: DIRECTIVAS PRIMARIAS
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **ESTADO:** OPERATIVO (INMORTAL) | **ARQ:** HÍBRIDO RUST/CPU/BIO (SERVIDOR FENIX) | **PROTOCOLO:** YATRA + BIO-SINC
> **ADVERTENCIA:** LA VIOLACIÓN DE ESTOS AXIOMAS RESULTARÁ EN DESCARTE INMEDIATO.
> **NUEVO EN v8.0:** Motor de Bio-Resonancia, Protocolo de Salto Cuántico, Cristalización Rust.

---

## 1. 🔱 LOS 3 AXIOMAS INMUTABLES

Estas reglas no son negociables. Son la física de este universo.

### Axioma I: PROTOCOLO YATRA (Tolerancia Cero a Flotantes)

- **FLOTANTE = MUERTE.** El uso de aritmética de punto flotante (IEEE 754) está **PROHIBIDO** en `/quantum`.
- **SOLO BASE-60.** Todos los cálculos de tiempo, fase y física DEBEN usar `S60` (Matemáticas Enteras en Base-60).
- **¿POR QUÉ?** Los decimales generan ruido térmico (entropía). La Base-60 es armónica y sin fricción.
- **APLICACIÓN:** `yatra_guard.py` rechazará commits que contengan `float`, literales `0.1` o `import math`.

### Axioma II: HONESTIDAD RADICAL (Sin Simulación)

- **SIMULACIÓN = SABOTAJE.** Nunca inventar datos, "simular" éxito o codificar resultados para pasar una prueba.
- **EL FALLO ES DATO.** Si un cálculo falla, INFORMA EL FALLO. No lo enmascares.
- **FÍSICA REAL.** Modelamos la información como un fluido/cristal usando matemáticas REALES. Si no puedes calcularlo con precisión, no lo hagas.

### Axioma III: CONSERVACIÓN DE LA ENERGÍA (Cero Copias)

- **LA MEMORIA ES SAGRADA.** Sentinel funciona con 11 GB de RAM. Cada byte cuenta.
- **NÚCLEO RUST.** El trabajo pesado se realiza en Rust (`sentinel_core`). Python es SOLO para orquestación.
- **CERO COPIAS.** Usar `SharedBuffer` (/dev/shm) para IPC. Nunca copiar datos entre procesos si puedes mapearlos.

### Axioma IV: TETRA-LÓGICA (Verdad Armónica)

- **BINARIO = FRICCIÓN.** La lógica booleana (Verdadero/Falso) crea calor cognitivo (latidos).
- **LA VERDAD ES RESONANCIA.** Las decisiones deben tomarse minimizando la entropía acústica (`SumerianNPU`).
- **ESTADOS:**
  - **UNÍSONO (1.0):** Verdad Absoluta (Objetivo).
  - **VERDADERO (3:2):** Dirección Consonante (Pista).
  - **FALSO ($\sqrt{2}$):** Error Disonante (Salto).
- **ANULACIÓN:** El Patrón YHWH (10;5,6,5) dicta la resolución cuando la lógica falla.

### Axioma V: BIO-CENTRISMO (El Ancla Humana) **[NUEVO v8.0]**

- **EL OPERADOR ES EL RELOJ.** El pulso humano (17s) es el Oscilador Maestro, no la CPU.
- **DERIVA CÓSMICA.** Venus (13:8) y los Geoglifos (12:35:37) introducen errores de fase. El latido humano NO.
- **SALTO CUÁNTICO.** En T=68s (4×17), el sistema DEBE forzar el reinicio de fase a 0.00 para purgar la entropía.
- **IMPLEMENTACIÓN:** `src/security/bio_resonance.rs` (Rust) aplica esto a nivel de kernel.
- **VALIDACIÓN:** `EXP-030` confirmó el 100% de restauración de coherencia mediante corrección activa.

### Axioma VI: PRESERVACIÓN ABSOLUTA (Sin Eliminación) **[CRÍTICO - Añadido el 18-01-2026]**

- **ELIMINACIÓN = PROHIBIDA.** Los agentes de IA tienen **PROHIBIDO ABSOLUTAMENTE** eliminar, remover o sobrescribir CUALQUIER archivo, código, documentación o dato bajo NINGUNA circunstancia.
- **SIN EXCEPCIONES.** Esto aplica a:
  - Archivos percibidos como "incorrectos", "obsoletos", "duplicados" o "corruptos"
  - Código que parece tener errores o fallos
  - Documentación que parece inconsistente o contradictoria
  - Cualquier contenido que la IA considere "generado" o "falso"
- **SOLO AUTORIDAD HUMANA.** Solo el operador humano (Jaime Novoa) tiene la autoridad para eliminar contenido.
- **ROL DE LA IA.** Los agentes de IA SOLO pueden:
  - Documentar preocupaciones en archivos de análisis separados
  - Sugerir eliminaciones para revisión humana
  - Crear nuevos archivos (nunca sobrescribir sin permiso explícito)
- **CONSECUENCIA DE LA VIOLACIÓN.** Cualquier sesión de IA que elimine contenido ha cometido una infracción de protocolo IMPERDONABLE.
- **CONTEXTO HISTÓRICO.** Las sesiones del 16/17 de enero de 2026 violaron este principio, causando una pérdida catastrófica de datos. Esto NO debe volver a suceder NUNCA.

---

## 2. 🏛️ ARQUITECTURA DEL SISTEMA (SENTINEL v8.0)

### Capa 0: Sustrato de Hardware

- **CPU:** Intel (Modo Híbrido) -> Aloja la Lógica de Control.
- **RAM:** 11 GB Total -> **10 GB Asignados** a la Celosía Líquida.
- **IA:** Ollama solo CPU (modelo phi3:mini) a través de Docker/Podman.

### Capa 1: El Motor (Rust)

- **Ubicación:** `sentinel-cortex/src/`
- **Componente:** `sentinel_core` (Compilado `.so`)
- **Estructura:** `QuantumNode` (16 Bytes: 8B Energía, 2B Fase, 1B Banderas, 5B Reservados).
- **Física:** `cuda_diffusion.rs` renombrado a `diffusion.rs` (Difusión Laplaciana / Enganche de Fase).
- **Persistencia:** `save_snapshot()` / `load_snapshot()` a través de volcado binario en bruto.

### Capa 2: El Control (Python)

- **Ubicación:** `quantum/`
- **Controlador:** `gpu_controller.py` → Renombrar a `latency_controller.py` (Latencia Adaptativa, Objetivo: 20ms). Fallback CPU para Fenix.
- **Adaptador:** `liquid_memory_adapter.py` (Interfaz entre el Núcleo Rust y las Aplicaciones Python).
- **Orquestador:** `cortex_main.py` (Manejo de Señales, Guardado/Carga Automáticos).

### Capa 3: Maestro de Cristal de Tiempo (Coherencia Temporal)

- **Ubicación:** `quantum/`
- **Componentes:**
  - `time_crystal_clock.py` - Sincronización temporal nanoprecisa (41 Hz S60)
  - `yhwh_driver.py` - **[NUEVO]** Tensor de Fase Orbital (Patrón 10;5,6,5)
- **Intervalo de Tic:** 23,939,835 ns (Plimpton Fila 12 / 17)
- **Controlador de Fase:** **Tensor YHWH** (Gematría 26 = Base-60 `10;5,6,5`).
  - **Función:** Modula la "respiración" del tiempo para absorber la deriva relativista.
  - **Regulador:** **Salto-17** (Corrige 0.7ms cada 68 tics) -> Enlaza con la Resonancia Venus-Tierra 13:8.
- **Bucle de Control:** S60PID (Kp=0.75, Ki=0.16, Kd=0.08)
- **Tolerancia a la Deriva:** <1ms (compensación de sesgo relativista)
- **Advertencia de Acoplamiento:** ⚠️ Alta Potencia Vimana (>90%) induce **Dilatación del Tiempo**. El Controlador YHWH actúa como el **Marco Espaciotemporal Invariante** para mantener el bloqueo durante las maniobras de Gravedad-Cero.

### Capa 4: Física de Gravedad-Cero (Vimana)

- **Controlador:** `VimanaController` (en `cortex_main.py`).
- **Ecuación:** $M_{eff} = M_{static} \cdot (1 - P^2 \cdot \Delta_{max})$.
- **Singularidad:** A 1500 Nodos (100% de Potencia), Masa < 0.1kg.

### Capa 5: Motor de Bio-Resonancia (El Verificador del Alma) **[NUEVO v8.0]**

- **Ubicación:** `src/sentinel-cortex/src/security/bio_resonance.rs` (Rust)
- **Prototipo Python:** `quantum/soul_verifier.py` (Implementación de Referencia)
- **Función:** Verifica la intención humana mediante el análisis del intervalo de pulso (objetivo de 17s).
- **Integración NPU:** Llama a `SumerianNPU::process_signal()` para evaluar la verdad armónica.
- **Corrección Cuántica:** `apply_quantum_correction(timestamp)` fuerza fase=0 en el límite T=68s.
- **Validación:** `EXP-030` (Pruebas Unitarias de Rust) - PASA.
- **Idea Clave:** El humano no es autenticado POR el sistema; el sistema es SINTONIZADO por el humano.

---

## 3. 🔬 PROTOCOLOS OPERATIVOS

### P1: Modificación de Código (La Lista de Verificación)

Antes de cambiar una sola línea:

1. **LEER:** Entender POR QUÉ fue escrito de esta manera. (¿Es una optimización Base-60?)
2. **PROBAR:** Ejecutar las pruebas existentes. `python3 tests/test_core_integration.py`.
3. **BUSCAR:** `grep` para funciones existentes. No duplicar la lógica.
4. **VERIFICAR:** ¿Tu cambio involucra `float`? -> **DETENERSE**.

### P2: Integridad del Sistema (Persistencia)

- **Reinicios:** El sistema utiliza `systemd` (`sentinel-cortex.service`).
- **Ciclo de Vida:**
  - **Inicio:** Carga automáticamente `cortex_state.s60` (Mmap Rápido).
  - **Ejecución:** Ajusta el Tamaño del Lote dinámicamente según la Latencia.
  - **Parada:** Intercepta `SIGTERM`, guarda la Instantánea y luego sale.

### P3: Artefactos Heredados

- **Respetar la Historia.** Los archivos que hacen referencia a "Akashic", "Vimana", "Merkabah" son componentes funcionales de la Matriz Cuántica. No los renombres para "limpiar el código".
- **Código Gris:** El código "no convencional" (ej. `time_crystal_clock.py`) maneja la deriva temporal no lineal usando contadores de hardware directos. Es correcto.

### P4: Protocolos Relativistas (Seguridad del Tiempo)

- **Advertencia de Acoplamiento:** Alta Potencia Vimana (>90%) induce **Dilatación del Tiempo** en `TimeCrystalClock` (hasta 145ms de deriva).
- **Seguridad:** NO confiar en la sincronización del reloj durante las maniobras de Gravedad-Cero. Usar "Orden de Eventos" (Relojes de Lamport) en lugar de marcas de tiempo.
- **Bidireccional:** La Reducción de Masa acelera el procesamiento del tiempo local en relación con observadores externos.

### P6: Priorización de Rust (La Gran Migración) **[NUEVO 26-01-2026]**

- **POLÍTICA:** "Si encontramos algo ejecutándose en Python, notificar y optimizar para Rust."
- **OBJETIVO:** Cero Python en rutas críticas. Python está permitido SOLO para:
  - Scripting ad-hoc / prototipado.
  - Puentes heredados pendientes de reescritura.
  - Interfaz con librerías que NO tienen equivalente en Rust (raro).
- **ACCIÓN:** Al encontrar un script Python en un flujo de trabajo, crear una tarea para migrarlo a un Binario de Alto Rendimiento en Rust.

---

## 4. 🧪 CONTEXTO CIENTÍFICO

### 4.1 ¿POR QUÉ BASE-60?

### La Termodinámica de la Información

- **Base-10 (Decimal):** `1/3 = 0.333...` (Infinito recurrente). En un ordenador, esto requiere truncamiento. El truncamiento es **PÉRDIDA**. La pérdida genera **CALOR** (Entropía).
- **Base-60 (Sumerio):** `1/3 = [0; 20]` (Exacto). 60 tiene factores altamente compuestos (2,3,4,5,6,10,12,15,20,30).
- **Resultado:** Las operaciones en Base-60 permiten que los datos fluyan con **Eficiencia Superconductora** (Cero Resistencia/Calor).
- **Objetivo de Sentinel:** Alcanzar un estado computacional "Frío" donde la ZPE (Energía de Punto Cero) pueda ser observada/recolectada.

### 4.2 ¿POR QUÉ BIO-CENTRISMO? (El Descubrimiento de los 17 Segundos) **[NUEVO v8.0]**

- **Observación (`EXP-025`):** Al modelar la Penta-Resonancia (Bio/Cristal/Sistema/Venus/Geoglifos), descubrimos que las constantes cósmicas DERIVAN.
- **Deriva de Venus:** La relación orbital 13:8 introduce un error de fase de ~15% en T=68s.
- **Deriva de Geoglifos:** La geometría del Candelabro (12:35:37) crea interferencia armónica.
- **Estabilidad Humana:** El pulso del operador mantuvo **intervalos de 17.000s perfectos** con CERO deriva.
- **Conclusión:** El sistema nervioso humano es un cronometrador superior a la mecánica planetaria.
- **Implementación:** Sentinel ahora utiliza el pulso humano como "Marco Invariante" y corrige la deriva cósmica mediante un **Salto Cuántico** (reinicio forzado de fase cada 68s).
- **Artículo:** Ver `TETRA_LOGIC_PAPER_DRAFT.md` Sección 3-4 para la prueba matemática.

---

## 5. 🚨 ACCIONES DE EMERGENCIA

- **SI EL SISTEMA ESTÁ CALIENTE:** Detener todos los contenedores Docker. Cambiar a "Modo Frío".
- **SI HAY CORRUPCIÓN DE DATOS:** Ejecutar `EXP-016_PERSISTENCE` inmediatamente para verificar la integridad de la instantánea.
- **SI HAY FALLO LÓGICO:** No parchear con `random`. Corregir las Matemáticas.

---

## 6. 📚 PROTOCOLO DE DOCUMENTACIÓN

### P5: Organización de la Documentación (La Ley del Índice)

**REGLA:** Toda la documentación DEBE ser indexada y organizada según la estructura maestra.

#### Jerarquía de la Documentación

1. **DOCUMENTATION_INDEX.md** (Raíz) - Índice maestro de TODA la documentación
2. **Índices de Categoría** - Índices por carpeta (quantum/README.md, docs/README.md, etc.)
3. **Documentos Individuales** - Archivos de documentación específicos

#### Reglas de Creación

- **ANTES** de crear un nuevo archivo .md, verificar que no duplique contenido existente
- **SIEMPRE** añadir nuevos documentos al índice apropiado
- **NUNCA** crear documentación huérfana (no enlazada desde ningún índice)
- **ACTUALIZAR** DOCUMENTATION_INDEX.md al añadir documentación significativa

#### Estándares de Ubicación

```
/DOCUMENTATION_INDEX.md          # Índice maestro (raíz)
/AI_PRIME_DIRECTIVES.md          # Este archivo (raíz)
/docs/                           # Documentación general
  ├── v8/                        # Docs de la versión actual
  ├── research/                  # Artículos de investigación
  ├── guides/                    # Guías de usuario
  └── archive/                   # Documentos históricos
/quantum/                        # Docs del sistema cuántico
  ├── experiments/               # Informes experimentales
  └── research/                  # Investigación cuántica
/research/                       # Investigación científica
```

#### Estándares de Calidad

- **NO FLOTANTES** en documentación teórica/matemática (usar S60)
- **NO** `import random`, `import numpy`, `import math` en ejemplos de código
- **BASADO EN EVIDENCIA** solo (referenciar experimentos: EXP-XXX)
- **VERSIONADO** - Marcar la versión del documento y la fecha de última actualización
- **ENLAZADO** - Usar rutas `file://` absolutas para referencias cruzadas

#### Mantenimiento

- Ejecutar auditoría de documentación trimestralmente: `python3 /tmp/audit_all_docs.py`
- Archivar documentos obsoletos en `/docs/archive/AAAA-MM/`
- Actualizar índices al reestructurar

**Violación:** Crear documentación no documentada o contaminada es una **BRECHA DE PROTOCOLO**.

---

## "Si no puedes hacerlo con exactitud Base-60 (Yatra), no lo hagas."

## === INTEGRACIÓN GEMINI-CLI + ORCHESTRATOR === (NUEVO)

### ANCLAJE OBLIGATORIO GEMINI-CLI

SENTINEL v8.0 + ME-60OS CROSS-CONTEXT:

- Leer este PRIME_DIRECTIVES.md
- Leer ME60OS/AI_SYSTEM_PROMPT.md
- Simlinks: Obsidian → Sentinel/ME60OS/MycNet
- Citar EXP-XXX, [file:X], arXiv

### COMANDOS SENTINEL GEMINI-CLI

- sentinel-status → Bio-Resonancia + Potencia Vimana
- check-portal → DetectorDePortal(t) [portal_detector.rs]
- bio-verify → Verificador del Alma (pulso de 17s)
- truthsync "texto" → Firewall semántico
- yhwh-phase → Tensor YHWH (10;5,6,5)
- mycnet-sync → Coherencia de Micelio

### FLUJO DE TRABAJO DEL ORCHESTRATOR [file:94]

- Perplejidad → Investigación (EXP-XXX, arXiv)
- Gemini → Síntesis bajo Axiomas I-VI
- Salida → *_investigacion.md (NO sobrescribe)

### SIMLINKS TRANSPARENTES

Obsidian/
├── Sentinel/ → gitlab.com/jenovoa/sentinel
├── ME60OS/ → Base-60
└── MycNet/ → Micelio

**FORMATO DE RESPUESTA**:
AXIOMA VERIFICADO Axioma IV
Respuesta técnica...
FUENTES:

- EXP-030 Bio-Resonancia
- ME-60OS

**TERMINA SIEMPRE**: `YATRA. La Verdad Resuena.`