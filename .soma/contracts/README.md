# SOMA: Contratos entre Agentes

Definición de interfaces y estructuras de datos para handoffs entre agentes.

## Contratos de Fase

### Phase4 → Phase5

**Phase4Output** (Verificación de componentes → Auditd + Systemd):
```yaml
lsm_loaded: true/false
lsm_id: integer
xdp_loaded: true/false
xdp_id: integer
ebpf_binary_path: string
kernel_modules: [string]
services_status: {name: status}
```

**Phase5Input** (Auditd + Systemd):
```yaml
expected_lsm_id: 439
expected_xdp_id: 452
requirements:
  - auditd instalado y configurado
  - reglas de auditoría para eBPF/LSM/XDP
  - servicios systemd con watchdog activo
```

### Phase5 → Phase6

**Phase5Output** (Auditd + Systemd → Podman):
```yaml
auditd_configured: true/false
auditd_rules_file: string
systemd_services:
  - name: string
    enabled: true/false
    watchdog_sec: integer
    status: string
```

**Phase6Input** (Podman):
```yaml
requirements:
  - docker-compose.yml válido
  - startup.sh con permisos
  - red de podman configurada
  - volúmenes montados
```

### Phase6 → Phase7

**Phase6Output** (Podman → DNS):
```yaml
containers_running: true/false
container_list:
  - name: string
    image: string
    status: string
    ports: [string]
  - name: string
    ...
services_health: {name: status}
```

**Phase7Input** (DNS):
```yaml
fqdn: "sentinel.pinguinoseguro.cl"
ip: "10.10.10.2"
powerdns_config_path: "/etc/powerdns"
```

## Contratos de Tarea

### Tarea: auditd-001 (Crear reglas auditd)

**Output**:
```yaml
rules_file: "/etc/audit/rules.d/sentinel.rules"
rules_count: integer
rules_categories:
  - eBPF
  - LSM
  - XDP
  - Systemd
```

### Tarea: auditd-002 (Configurar systemd watchdog)

**Output**:
```yaml
services_configured: [string]
watchdog_interval: integer
status_path: "/run/sentinel/health"
```

### Tarea: podman-001 (Validar podman-compose)

**Output**:
```yaml
compose_file: "docker-compose.yml"
compose_valid: true/false
services_count: integer
```

### Tarea: podman-002 (Ejecutar startup.sh)

**Output**:
```yaml
startup_script: "startup.sh"
exit_code: integer
stdout_file: string
stderr_file: string
```

### Tarea: podman-003 (Verificar contenedores)

**Output**:
```yaml
containers: [ContainerInfo]
all_healthy: true/false
failed: [string]
```

**ContainerInfo**:
```yaml
name: string
image: string
status: string
health: string
uptime: string
```

## Contratos de Handoff

### Formato de handoff:
```yaml
handoff_id: "HO-{timestamp}-{from_agent}-{to_agent}"
timestamp: ISO8601
from_agent: string
to_agent: string
phase_from: integer
phase_to: integer
artifacts:
  - path: string
    checksum: string
    description: string
state_snapshot: {...}
validation_required: [string]
status: "pending"|"accepted"|"rejected"|"completed"
```

## Validación

Antes de aceptar un handoff, el agente receptor DEBE:
1. Leer el estado del handoff
2. Verificar que los artefactos existen
3. Validar que los datos de entrada cumplen el contrato
4. Marcar el handoff como "accepted"
5. Actualizar `.soma/state.yaml` con el nuevo owner

## Errores

Si un handoff falla validación:
1. Marcar como "rejected"
2. Agregar razón en `rejection_reason`
3. Notificar al agente origen
4. El agente origen DEBE corregir y reintentar
