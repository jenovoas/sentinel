# SOMA: Sistema de Eventos

Sistema publish-subscribe distribuido para comunicación asíncrona entre agentes.

## Tipos de Eventos

### Fase lifecycle
- `phase_started`: Una fase comienza ejecución
- `phase_completed`: Una fase finaliza exitosamente
- `phase_failed`: Una fase falla
- `phase_blocked`: Una fase está bloqueada esperando dependencias

### Tarea lifecycle
- `task_claimed`: Un agente reclama una tarea
- `task_started`: Una tarea comienza ejecución
- `task_completed`: Una tarea finaliza exitosamente
- `task_failed`: Una tarea falla
- `task_blocked`: Una tarea está bloqueada

### Sistema
- `agent_registered`: Nuevo agente se registra
- `agent_heartbeat`: Latido de agente
- `lock_acquired`: Un bloqueo es adquirido
- `lock_released`: Un bloqueo es liberado
- `handoff_requested`: Handoff solicitado
- `handoff_accepted`: Handoff aceptado
- `handoff_rejected`: Handoff rechazado

### Infraestructura
- `container_started`: Contenedor iniciado
- `container_stopped`: Contenedor detenido
- `service_up`: Servicio operativo
- `service_down`: Servicio caído
- `network_changed`: Cambio en red

## Formato de Evento

```yaml
event:
  id: "evt-{timestamp}-{type}-{agent}"
  timestamp: "2026-02-26T12:34:56Z"
  type: string
  phase: integer|null
  task: string|null
  agent: string
  data: object
  severity: "info"|"warning"|"error"|"critical"
```

## Eventos Actuales (state.yaml)

```yaml
events:
  - id: "evt-001"
    timestamp: "2026-02-26T00:00:00Z"
    type: "phase_completed"
    phase: 4
    message: "Verificación de componentes finalizada"
    agent: "claude-opus"
```

## Publicar Eventos

Para publicar un evento:

1. Agregar al array `events` en `.soma/state.yaml`
2. El evento más reciente debe estar al principio del array
3. Mantener solo los últimos 100 eventos (limpiar los antiguos)

## Suscribirse a Eventos

Los agentes pueden filtrar eventos por:
- `type`: Tipo de evento
- `phase`: Fase específica
- `agent`: Agente específico
- `severity`: Nivel de severidad

## Eventos Pendientes (Fase 5-7)

Esperados en Fase 5:
- `phase_started` (phase=5)
- `task_claimed` (auditd-001, auditd-002)
- `task_completed` (auditd-001)
- `task_completed` (auditd-002)
- `phase_completed` (phase=5)
- `handoff_requested` (5→6)

Esperados en Fase 6:
- `phase_started` (phase=6)
- `task_claimed` (podman-001, podman-002, podman-003)
- `task_completed` (podman-001)
- `task_completed` (podman-002)
- `task_completed` (podman-003)
- `phase_completed` (phase=6)
- `handoff_requested` (6→7)

Esperados en Fase 7:
- `phase_started` (phase=7)
- `task_claimed` (dns-001, dns-002)
- `task_completed` (dns-001)
- `task_completed` (dns-002)
- `phase_completed` (phase=7)
- `deployment_complete`: Evento especial cuando todas las fases completas

## Registro de Eventos

Los archivos de log de eventos se guardan en `.soma/logs/`:
- `events-YYYY-MM-DD.log`: Registro diario
- `events-error.log`: Solo errores críticos
- `events-audit.log`: Handoffs y cambios de ownership
