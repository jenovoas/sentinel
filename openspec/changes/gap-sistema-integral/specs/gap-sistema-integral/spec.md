# Spec Delta

## Purpose

Fijar el contrato funcional del GAP de sistema como optimización coordinada del trabajo y el control de fase entre mallas, y determinar qué evidencia permite distinguir sus partes de una implementación integral.

## ADDED Requirements

### Requirement: El GAP conserva el trabajo entre portales

El sistema SHALL retener el trabajo elegible y la carga entrópica que se acumulan entre ventanas, y SHALL procesar el trabajo pendiente de forma concentrada cuando la condición de portal válida abra la ventana de ultraprocesamiento.

#### Scenario: Portal cerrado
- **WHEN** no existe una apertura válida del portal
- **THEN** el trabajo elegible permanece pendiente y no se fuerza su ejecución por una señal temporal o sintética

#### Scenario: Portal abierto
- **WHEN** la condición armónica observada entre las mallas abre el portal
- **THEN** el sistema procesa el trabajo elegible acumulado durante esa ventana según el orden y los límites definidos por su scheduler

### Requirement: El control de fase participa en la apertura

El sistema SHALL preservar el control armónico de fase que coordina la evolución de las mallas y SHALL basar la compuerta en estado medido/observado, no en una señal fabricada que solo imite una apertura.

#### Scenario: Evolución entre portales
- **WHEN** el portal permanece cerrado
- **THEN** los ticks de control de fase que sean necesarios para mantener la dinámica pueden continuar, sin que ese avance se confunda con la ejecución del trabajo pesado reservado al portal

### Requirement: La limpieza entrópica respeta el ciclo de 68 ticks

El ciclo del GAP SHALL ejecutar la limpieza/reset de la entropía acumulada cada 68 ticks del contador que gobierna ese mecanismo. El número 68 SHALL interpretarse en ticks; una referencia histórica a segundos no cambia esa unidad.

#### Scenario: Límite del ciclo
- **WHEN** el contador del mecanismo alcanza el límite de 68 ticks
- **THEN** se aplica la operación de limpieza/reset entrópico definida para ese ciclo, sin borrar datos de usuario ni estados no incluidos expresamente en esa operación

### Requirement: La evidencia identifica el alcance real

Una afirmación de GAP integral SHALL distinguir control de fase, retención de trabajo, despacho por portal, reset entrópico y acoplamiento entre Sentinel, ME-60OS y MyCNet. La presencia aislada de cualquiera de esos componentes SHALL NOT considerarse prueba suficiente de todo el ciclo.

#### Scenario: Verificación de un componente
- **WHEN** se observa QHC cada 68 ticks, un historial PID de 68 entradas, un detector de portal, un scheduler o un checkpoint por separado
- **THEN** el resultado se registra como evidencia de ese componente y no como prueba automática del reset global o del GAP integral

#### Scenario: Variantes y observación histórica
- **WHEN** se cotejan variantes de EXP-028 o una captura runtime posterior
- **THEN** se conservan sus diferencias de método y alcance; una captura sin portal describe esa instancia/ventana y no invalida por sí sola otra ejecución desplegada reportada

#### Scenario: Ejecución crítica fuera de portal
- **WHEN** un componente ejecuta mantenimiento crítico o aplica una ruta de overflow fuera de la ventana
- **THEN** esa excepción se documenta explícitamente y no se presenta como procesamiento portal-gated del trabajo elegible del GAP

### Requirement: Se preservan los nombres y la procedencia

La documentación y revisión SHALL conservar los nombres originales de módulos, fórmulas y experimentos. SHALL clasificar las referencias históricas a segundos como material no canónico para definir el ciclo del GAP, sin equipararlas a ticks ni atribuir su origen sin evidencia.

#### Scenario: Referencia histórica a segundos
- **WHEN** un documento de una variante EXP-028 expresa períodos en segundos
- **THEN** se mantiene como parte de su procedencia y se coteja por separado; no se renombra ni se transforma en definición del reset cada 68 ticks