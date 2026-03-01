# SOMA: Sistema de Handoffs

Puntos de control atómicos para transferencia de control entre agentes.

## Flujo de Handoff

```
┌─────────────┐    request     ┌─────────────┐
│   Agente A  │ ─────────────► │   Agente B  │
│   (origen)  │                │  (destino)  │
└─────────────┘                └─────────────┘
      │                              │
      │ validation                   │ validate
      │ ◄─────────────────────────── │
      │                              │
      │ accept/reject                │
      │ ───────────────────────────► │
      │                              │
      │ complete                     │
      │ ◄─────────────────────────── │
```

## Plantilla de Handoff

```yaml
handoff:
  id: "HO-{timestamp}-{from}-{to}"
  timestamp: "2026-02-26T12:34:56Z"
  status: "pending"  # pending | validating | accepted | rejected | completed

  # Identificación
  from_agent: string
  to_agent: string
  from_phase: integer
  to_phase: integer

  # Estado al momento del handoff
  state_snapshot:
    phases: [...]
    tasks: [...]
    artifacts: [...]

  # Artefactos transferidos
  artifacts:
    - path: string
      type: "file"|"config"|"binary"
      checksum: sha256
      description: string
      required: true

  # Contrato de validación
  contract:
    input_schema: string  # referencia a .soma/contracts/
    validation_steps: [string]
    acceptance_criteria: [string]

  # Estado
  validation_log: []
  rejection_reason: string|null
  completed_at: string|null
```

## Handoffs Pendientes

### HO-20260226-000000-4-5 (Phase 4 → Phase 5)

```yaml
handoff:
  id: "HO-20260226-000000-4-5"
  timestamp: "2026-02-26T00:00:00Z"
  status: "pending"

  from_agent: "claude-opus"
  to_agent: null  # TBA
  from_phase: 4
  to_phase: 5

  state_snapshot:
    lsm_loaded: true
    lsm_id: 439
    xdp_loaded: true
    xdp_id: 452
    ebpf_binary: "ebpf/sentinel_probe.o"

  artifacts:
    - path: "ebpf/sentinel_probe.o"
      type: "binary"
      checksum: null
      description: "Binario eBPF compilado"
      required: true
    - path: "systemd/sentinel-lsm.service"
      type: "config"
      checksum: null
      description: "Configuración systemd LSM"
      required: true
    - path: "systemd/sentinel-xdp.service"
      type: "config"
      checksum: null
      description: "Configuración systemd XDP"
      required: true

  contract:
    input_schema: "Phase5Input"
    validation_steps:
      - "Verificar que LSM (id=439) está cargado"
      - "Verificar que XDP (id=452) está cargado"
      - "Verificar que el binario eBPF existe"
      - "Verificar que los servicios systemd están habilitados"
    acceptance_criteria:
      - "auditd instalado"
      - "reglas auditd creadas"
      - "servicios systemd con watchdog configurado"
```

## Validación de Handoff

### Paso 1: Reclamar Handoff

Un agente reclama un handoff:
1. Lee el archivo del handoff en `.soma/handoffs/`
2. Verifica que `status == "pending"`
3. Cambia `status` a `validating`
4. Agrega su ID en `to_agent`
5. Actualiza `.soma/state.yaml`

### Paso 2: Validar

El agente receptor ejecuta los `validation_steps`:
1. Para cada artefacto requerido:
   - Verifica que el archivo existe
   - Calcula el checksum (si especificado)
   - Valida el tipo de archivo
2. Ejecuta las validaciones del contrato
3. Agrega resultados a `validation_log`

### Paso 3: Aceptar o Rechazar

Si todas las validaciones pasan:
- Cambiar `status` a `accepted`
- Asignarse como owner de la fase destino
- Actualizar `.soma/state.yaml`
- Publicar evento `handoff_accepted`

Si alguna validación falla:
- Cambiar `status` a `rejected`
- Agregar `rejection_reason`
- Notificar al agente origen
- Publicar evento `handoff_rejected`

### Paso 4: Completar

Una vez aceptado, el agente:
- Comienza a trabajar en la fase destino
- Al terminar, cambia `status` a `completed`
- Agrega `completed_at`
- Solicita el siguiente handoff

## API de Handoff (para agentes)

```bash
# Listar handoffs pendientes
soma list-handoffs --status=pending

# Reclamar un handoff
soma claim-handoff --id=HO-20260226-000000-4-5 --agent=claude-glm

# Validar un handoff
soma validate-handoff --id=HO-20260226-000000-4-5

# Aceptar un handoff
soma accept-handoff --id=HO-20260226-000000-4-5

# Rechazar un handoff
soma reject-handoff --id=HO-20260226-000000-4-5 --reason="Artefacto faltante"

# Crear un nuevo handoff
soma create-handoff --from=5 --to=6 --from-agent=claude-glm
```

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| Artefacto no encontrado | El archivo fue movido/eliminado | Verificar rutas en state.yaml |
| Checksum mismatch | El archivo fue modificado | Regenerar artefacto |
| Fase incompleta | Tareas pendientes en fase origen | Completar todas las tareas |
| Agente no registrado | El agente no está en agents[] | Registrar en state.yaml |

## Handoff Exitoso

Un handoff es exitoso cuando:
1. ✅ Todos los artefactos existen
2. ✅ Todos los artefactos tienen checksum válido (si especificado)
3. ✅ Todas las validaciones del contrato pasan
4. ✅ El agente destino acepta el handoff
5. ✅ El agente origen libera el ownership
6. ✅ El estado en `.soma/state.yaml` se actualiza
