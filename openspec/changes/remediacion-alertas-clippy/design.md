# Design

## Context

Ver `proposal.md` y `specs/core-arithmetic/spec.md`. El crate combina aritmética SPA con bindings PyO3; al menos el importador decimal, el scheduler SOMA y el detector de anomalías contienen `f64`. Las reglas estrictas del crate ya existen y no se modificarán.

## Goals / Non-Goals

**Goals:**
- Eliminar las operaciones y firmas `f32`/`f64` de la lógica operativa compilada en `me-60os-core`.
- Mantener escala SPA y unidades explícitas en las fronteras Rust/Python.
- Corregir los casts con comprobación o acotación semántica, sin envoltura accidental.
- Mantener pruebas que verifiquen límites, unidades y equivalencia de las rutas afectadas.

**Non-Goals:**
- Modificar niveles de lint, manifiestos de compilador, eBPF, despliegues o estado remoto.
- Eliminar floats de herramientas de benchmark/visualización cuando solo representen resultados y no participen de lógica de dominio.
- Cambiar la escala SPA o introducir una dependencia numérica.

## Decisions

- Las APIs Rust/PyO3 que hoy reciben tiempo usarán nanosegundos enteros monotónicos (`u64`); las duraciones configurables usarán milisegundos enteros. Se evita convertir `Instant` a punto flotante.
- Las métricas SOMA continuas se expresarán como valores raw SPA (escala `60^4`); contadores, bytes y duraciones conservarán unidades enteras declaradas. Estadística de ventanas y umbrales será entera/S60, con raíz cuadrada de `SPAMath` donde sea necesaria.
- Los consumidores Python convertirán datos de entrada a esas unidades antes del binding. No se mantendrá una sobrecarga `f64` ni alias de compatibilidad en Rust.
- Para casts enteros, usar `TryFrom` donde el rango no esté garantizado; donde el dominio se limite intencionalmente, aplicar `clamp` antes de convertir y probar los extremos. Los operadores SPA sin canal de error usarán fallo explícito al exceder rango, no truncamiento.
- El importador decimal se sustituirá por una entrada entera explícita; los documentos y bridges que lo referencien se actualizarán o retirarán según su uso comprobado.

## Risks / Trade-offs

- [Cambios en firmas PyO3 rompen callers existentes] → actualizar callers rastreados en el mismo cambio y probar la importación/binding.
- [Redondeo entero puede diferir de floats históricos] → definir escalas y reglas de redondeo en pruebas de equivalencia y límites antes de migrar cada métrica.
- [Los operadores SPA no pueden devolver errores] → preservar el contrato actual de resultado directo y fallar explícitamente solo ante un resultado no representable.

## Migration Plan

Actualizar bindings Rust y callers Python en el mismo cambio; no hay despliegue asociado. Revertir conjuntamente las firmas y callers si las pruebas del binding o del backend revelan incompatibilidad. Validar OpenSpec, `cargo clippy` estricto, pruebas del core, targets y pruebas Python relevantes.
