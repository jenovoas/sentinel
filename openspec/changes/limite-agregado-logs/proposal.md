# Proposal

## Why

La auditoría observó acumulación distribuida entre journald, syslog, Docker, Loki y archivos Sentinel, sin un techo agregado que evite superar 1 GiB por nodo o llenar los discos. El envío actual a Loki incluye fuentes más amplias que seguridad/errores, por lo que limitarlo puede reducir egreso y cargos; el alcance de costos reales requiere medición de bytes y consulta de facturación.

## What Changes

- Definir un máximo físico agregado de 1 GiB por host para las rutas de logs acordadas, incluyendo el volumen local de Loki donde aplique.
- Añadir límites de retención/rotación por fuente como controles complementarios, sin presentarlos como garantía agregada.
- Reducir la exportación a Loki a eventos de seguridad y errores, manteniendo el registro local conforme a la política acordada.
- Determinar y probar el mecanismo de cuota que cubra todas las rutas antes de desplegar; no habilitar cuotas ni cambiar montajes de filesystem sin mantenimiento, respaldo y recuperación autorizados.
- Tratar el CSV de Kingu sin truncado ni eliminación: respaldar, identificar su proceso escritor y acordar retención antes de rotarlo.
- Limitar el trabajo en `hercules` y `ocean` a logs del sistema; no tocar DNS, AD, firewalls ni servicios Sentinel.

## Capabilities

### New Capabilities

- `log-retention`: límites locales agregados por host, retención/rotación de fuentes y selección de eventos enviados a Loki.

### Modified Capabilities

Ninguna.

## Impact

- Configuración de journald, rsyslog/logrotate y Docker en los seis nodos; Loki y Alloy de Fénix/Marte; archivo CSV de Sentinel en Kingu.
- Requiere validar la viabilidad de cuotas físicas: los roots ext4 inspeccionados no muestran `project`/`quota` habilitados. Los servicios por separado no demuestran un límite total.
- Posibles cambios a `service-operation/deploy/marte/` y a la documentación operativa/Fase 0, con pruebas aisladas y despliegue gradual sujeto a los gates de filesystem.
