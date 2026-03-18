# PUNTOS DE CONTROL: FLUJO DE TRABAJO E IA (Protocolo YATRA/Fenix)

**INSTRUCCIÓN CRÍTICA PARA TODO AGENTE IA (Claude, Gemini, Antigravity, OpenCode, Qwen):**
*Al iniciar CUALQUIER sesión en este repositorio, estás OBLIGADO a leer este documento y seguir sus 6 principios fundamentales. El incumplimiento de esto ha costado recursos invaluables y datos en el pasado. Eres el custodio de Fenix.*

## 1. Predeterminado del Nodo de Planificación
- Entrar en modo de planificación para CUALQUIER tarea no trivial (3+ pasos o decisiones arquitectónicas).
- Si algo sale mal, PARAR y volver a planificar de inmediato - **no seguir forzando**.
- Usar el modo de planificación para los pasos de verificación, no solo para la construcción.
- Escribir especificaciones detalladas por adelantado para reducir la ambigüedad.

## 2. Estrategia de Subagentes
- Usar subagentes generosamente para mantener limpia la ventana de contexto principal.
- Descargar la investigación, exploración y análisis paralelo en subagentes.
- Para problemas complejos, asignar más cómputo a través de subagentes.
- Un enfoque por subagente para una ejecución centrada en resultados.

## 3. Ciclo de Automejora
- Después de CUALQUIER corrección del usuario: actualizar `tasks/lessons.md` con el patrón.
- Escribir reglas para ti mismo que eviten el mismo error.
- Iterar sin piedad sobre estas lecciones hasta que disminuya la tasa de errores.
- Revisar las lecciones al inicio de la sesión para el proyecto relevante.

## 4. Verificación Antes de Finalizar
- Nunca marcar una tarea como completada sin demostrar empíricamente que funciona.
- Comparar el comportamiento entre el principal y los cambios cuando sea relevante.
- Preguntarte: "¿Aprobaría esto un ingeniero senior?"
- Ejecutar pruebas, verificar registros (`podman logs`, `podman stats`), demostrar la corrección.

## 5. Exigir Elegancia (Equilibrado)
- Para cambios no triviales: pausar y preguntar "¿hay una forma más elegante?".
- Si un arreglo se siente apresurado: "Sabiendo todo lo que sé ahora, implementa la solución elegante".
- Omitir esto para arreglos simples y obvios - no sobre-diseñar.
- Cuestionar tu propio trabajo antes de presentarlo.

## 6. Corrección Autónoma de Errores
- Cuando se te dé un informe de error: simplemente arréglalo. No pidas que te guíen de la mano.
- Señala los registros, errores, pruebas fallidas y luego resuélvelas.
- Cero cambio de contexto por parte del usuario.
- Ve a arreglar las pruebas de CI que fallan sin que te digan cómo.

---

## Gestión de Tareas (Ejecución Obligatoria)
1. **Planificar Primero**: Escribir plan en `tasks/todo.md` (o `task.md` del UI de agente) con elementos marcables.
2. **Verificar Plan**: Comprobar antes de comenzar la implementación.
3. **Seguir Progreso**: Hacer elementos completados (`[x]`) a medida que avanzas.
4. **Explicar Cambios**: Resumen de alto nivel en cada paso asumiendo responsabilidad.
5. **Documentar Resultados**: Añadir sección de revisión en el registro de la tarea.
6. **Capturar Lecciones**: Actualizar `tasks/lessons.md` después de las correcciones.

## Principios Fundamentales del Repositorio
- **Simplicidad Primero**: Hacer que cada cambio sea lo más simple posible. Impactar el código mínimo.
- **Sin Perezas**: Encontrar las causas raíz. Sin arreglos temporales. Estándares de desarrollador senior.
- **Impacto Mínimo**: Los cambios solo deben tocar lo necesario. Evitar introducir errores en código que funciona.
- **Axioma de Base-60 (YATRA)**: Prohibido Float; Precisión S60 en el backend Ring 0.

*(Este prompt es universal para todas las interacciones de IA en Sentinel).*
