# Proposal

## Why

La definición sistémica del GAP está repartida entre memoria persistente, experimentos, historial Git, el QHC, CrystalRuntime y el scheduler. Esa fragmentación ha hecho que el mecanismo se reduzca a piezas aisladas o se confunda el ciclo de 68 ticks con referencias históricas a segundos. Hace falta fijar el contrato integral y separar diseño, variantes experimentales, código local vigente y evidencia operativa.

## What Changes

- Documentar el GAP como acumulación del trabajo pendiente y de la entropía entre portales, control armónico de fase y procesamiento concentrado en ventanas observadas, con limpieza/reset cada 68 ticks.
- Registrar por separado los acoplamientos Sentinel, ME-60OS y MyCNet, las variantes EXP-028 y las excepciones/rutas que el código actual ejecuta fuera del portal.
- Mantener las referencias históricas a segundos como material por auditar; no tratarlas como definición de 68 ticks ni reemplazar/renombrar experimentos.
- Crear una nota de auditoría correspondiente en personalvault y enlazarla desde la arquitectura funcional existente.

## Capabilities

### New Capabilities
- `gap-sistema-integral`: Define el contrato observable del GAP y la evidencia necesaria para afirmar que el ciclo integral está implementado o desplegado.

### Modified Capabilities

## Impact

Solo documentación y especificación OpenSpec. No cambia código, configuración, servicio, datos ni despliegue. La inspección del checkout y la documentación no se presenta como prueba de que el estado local esté desplegado.