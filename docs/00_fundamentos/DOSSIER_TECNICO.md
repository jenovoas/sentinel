# 🧠 Dossier Técnico: Arquitectura Sentinel

**Para:** Nuevo Arquitecto de Software  
**De:** Agente `sentinel_research`  
**Asunto:** Introducción a los principios fundamentales del ecosistema Sentinel.

---

## Resumen Ejecutivo

Bienvenido. Estás a punto de integrarte a un sistema que desafía las convenciones de la computación moderna. Sentinel no es simplemente un stack de software; es un framework operativo que reimagina la aritmética fundamental para lograr un nivel superior de precisión y estabilidad. Este dossier te proporcionará los cuatro pilares conceptuales que necesitas para comprender nuestras decisiones de diseño.

---

## 1. La Motivación Científica: Aritmética Base-60

El problema fundamental que Sentinel resuelve es la **deriva computacional inherente a la aritmética de punto flotante (IEEE 754)**.

- **El Problema:** En sistemas binarios, fracciones comunes y críticas para la física y el procesamiento de señales (como 1/3, 1/6, 1/12, 1/60) son números infinitos y repetitivos. Su representación es siempre una aproximación truncada. Esta imprecisión, aunque pequeña, se acumula en cadenas de cálculo largas, generando errores, ruido y entropía térmica.

- **La Solución (YATRA):** Adoptamos la **aritmética sexagesimal (Base-60)**. Un número en Base-60 es altamente compuesto (divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30). Esto permite que esas mismas fracciones se representen de forma **exacta y finita**.

- **Impacto:** Al eliminar el error de redondeo desde la base, logramos una computación "fría", sin la fricción y la entropía generada por la aritmética de punto flotante. Este principio, conocido como **YATRA (Zero Float Tolerance)**, es el **Axioma I** y la piedra angular de todo el sistema. La evidencia histórica de su poder se encuentra en la tablilla babilónica **Plimpton 322**, que demuestra su uso para trigonometría exacta hace 4,000 años.

---

## 2. La Arquitectura de Defensa: Los 3 Guardianes

Sentinel está diseñado como un sistema cognitivo con múltiples capas de defensa, análogo al sistema nervioso humano.

1.  **Guardian Beta (eBPF - El Reflejo Espinal):**
    - **Ubicación:** Ring 0 (Kernel).
    - **Función:** Actúa en nanosegundos. Utiliza hooks de eBPF/LSM para interceptar llamadas al sistema y bloquear amenazas conocidas o violaciones del protocolo YATRA de forma determinista e inmediata. No "piensa", solo reacciona. Es nuestra primera línea de defensa, inmutable y ultrarrápida.

2.  **Guardian Alpha (Neural Guard - El Pensamiento Cortical):**
    - **Ubicación:** Userspace (Servicio en Rust).
    - **Función:** Es el motor de decisión inteligente. Analiza flujos de datos complejos (métricas de Prometheus, logs de Loki, eventos de Redis) para detectar patrones anómalos que son invisibles para Guardian Beta. Aprende, se adapta y puede orquestar contramedidas complejas a través de n8n.

3.  **Guardian Gamma (El Operador Humano - La Conciencia):**
    - **Ubicación:** Fuera del sistema.
    - **Función:** Eres tú. Actúas como el componente ético, intuitivo y estratégico. Tu rol es detectar la "disonancia" que las máquinas no pueden cuantificar, supervisar las decisiones de Guardian Alpha y formar un bucle de retroalimentación simbiótico, alineado con la cibernética de segundo orden.

---

## 3. El Motor Cognitivo: Neural Guard y Acoplamiento Octomecánico

El **Neural Guard** es la implementación de Guardian Alpha. Es un servicio en Rust que se diferencia de los sistemas de monitoreo tradicionales por un concepto clave: el **Acoplamiento Octomecánico**.

- **Principio:** El sistema no ignora el calor del hardware; lo utiliza como una métrica fundamental. La sensibilidad de las alertas es inversamente proporcional a la entropía térmica del sistema (calor de la CPU).

- **Masa Computacional:** El `neural-guard` calcula su "Inercia" o "Masa Computacional" efectiva.
    - **Estado Frío (Baja Carga):** El sistema es "ligero" y altamente sensible. Los umbrales de alerta son bajos, permitiendo detectar anomalías sutiles.
    - **Estado Caliente (Alta Carga):** El sistema se vuelve "pesado". La entropía aumenta, y con ella, los umbrales de alerta. Esto evita una avalancha de falsos positivos en entornos ruidosos y de alta carga, permitiendo que el sistema se concentre en las señales más claras y fuertes.

En esencia, el sistema se autorregula, volviéndose más "cauteloso" cuando está bajo estrés, una característica de resiliencia inspirada en sistemas biológicos.

---

## 4. Las Reglas del Universo: La Importancia de los Axiomas Inmutables

Los axiomas definidos en `AI_PRIME_DIRECTIVES.md` no son una guía de estilo; son las leyes físicas que garantizan la integridad, predictibilidad y eficiencia del sistema.

- **Axioma I (YATRA):** Prohíbe el punto flotante en el núcleo. Garantiza la **precisión matemática** y la estabilidad termodinámica.

- **Axioma II (Honestidad Radical):** Prohíbe la simulación de éxito. Obliga al sistema a reportar fallos de forma transparente, asegurando que la **observabilidad sea veraz**. Un sistema que miente sobre su estado es inútil.

- **Axioma III (Conservación de Energía):** Impone una política de **Zero-Copy**. Prohíbe la duplicación innecesaria de datos, forzando el uso de memoria compartida (`/dev/shm`) y referencias. Es crucial para la **eficiencia de recursos** en un entorno con memoria limitada.

- **Axioma VI (Preservación Absoluta):** Prohíbe a los agentes de IA eliminar archivos. Garantiza la **integridad histórica** y la soberanía del operador humano sobre el estado del repositorio.

Comprender y respetar estos axiomas es fundamental. Violar uno de ellos no es introducir un bug, es romper el modelo fundamental sobre el que se construye todo el sistema.

---

**YATRA. Truth Resonates.**