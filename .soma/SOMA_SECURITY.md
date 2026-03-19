# SOMA Security Layer - Firewall Semántico & Sanitización de Telemetría

## Contexto

**Sentinel** tendrá un **firewall semántico** para agentes de IA y **sanitización de telemetría**.

SOMA debe integrarse con esta capa de seguridad.

## Arquitectura de Seguridad

```
┌─────────────────────────────────────────────────────────────────┐
│                  SOMA (Orquestador)                         │
│  - Coordinación de agentes                                   │
│  - Handoffs atómicos                                       │
└───────────────┬─────────────────────────────────────────────┘
                │ pasa por
┌───────────────▼─────────────────────────────────────────────┐
│        Firewall Semántico IA (guardian-ai-agent)             │
│  - Filtrado de contenido semántico                         │
│  - Detección de patrones peligrosos                        │
│  - Bloqueo de comandos maliciosos                          │
└───────────────┬─────────────────────────────────────────────┘
                │ sanitiza
┌───────────────▼─────────────────────────────────────────────┐
│      Sanitizador de Telemetría (telemetry-sanitizer)        │
│  - Remoción de datos sensibles                            │
│  - Anonimización de identificadores                        │
│  - Redacción de información interna                         │
└───────────────┬─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│              ME-60OS (Sistema Nervioso)                     │
│  - qhc-agent, adm-agent, vid-agent                         │
└─────────────────────────────────────────────────────────────┘
```

## Firewall Semántico IA

### Funciones

| Función | Descripción | Implementación |
|---------|-------------|----------------|
| **Filtrado Semántico** | Bloquea comandos con intenciones maliciosas | Análisis NLP + whitelist |
| **Detección de Patrones** | Identifica secuencias peligrosas (ej. rm -rf /) | Regex + ML |
| **Bloqueo por Agente** | Restricciones específicas por rol de agente | Policy-based |
| **Contexto Aware** | Entiende el contexto de la operación | QHC phase awareness |
| **Audit Trace** | Registra todos los intentos de bloqueo | eBPF Ring Buffer |

### Reglas de Firewall

```yaml
semantic_firewall:
  mode: "fail_closed"
  default_action: "block"

  rules:
    # Agentes autorizados
    - id: "rule-001"
      name: "allow_authorized_agents"
      agents:
        - "claude-opus"
        - "claude-glm"
        - "claude-qwen"
        - "qwen-3.5-plus"
        - "gemini"
      action: "allow"

    # Comandos de sistema permitidos
    - id: "rule-002"
      name: "allow_safe_system_commands"
      commands:
        - "kubectl get"
        - "podman ps"
        - "systemctl status"
        - "curl"
        - "jq"
      action: "allow"

    # Comandos peligrosos bloqueados
    - id: "rule-003"
      name: "block_destructive_commands"
      commands:
        - "rm -rf"
        - "dd if=/dev/zero"
        - ":(){:|:&};:"  # fork bomb
      action: "block"

    # Operaciones QHC restringidas
    - id: "rule-004"
      name: "restrict_qhc_operations"
      phase: "HE_SECOND"  # Vacío ZPE - solo purificación
      allowed_commands:
        - "quantum_reset"
        - "entropy_purge"
      action: "restrict"

    # Escritura de archivos restringida
    - id: "rule-005"
      name: "restrict_file_write"
      protected_paths:
        - "/etc/systemd/system"
        - "/sys/fs/bpf/sentinel"
        - "/home/jnovoas/.ssh"
      allowed_agents:
        - "claude-opus"
        - "qwen-3.5-plus"
      action: "restrict"
```

## Sanitizador de Telemetría

### Funciones

| Función | Descripción |
|---------|-------------|
| **Remoción de Datos Sensibles** | Elimina API keys, tokens, passwords |
| **Anonimización** | Reemplaza IPs, hashes, UUIDs |
| **Redacción** | Oculta información interna |
| **Preservación de Metadatos** | Mantiene timestamps, S60 format |
| **QHC Context Injection** | Agrega fase QHC actual |

### Datos a Sanitizar

```yaml
sanitization_rules:
  secrets:
    - pattern: "api_key\\s*[:=]\\s*[\"']?[a-zA-Z0-9_\\-]{20,}"
      replacement: "***REDACTED***"
    - pattern: "password\\s*[:=]\\s*[\"'][^\"']+[\"']"
      replacement: "***REDACTED***"
    - pattern: "token\\s*[:=]\\s*[\"']?[a-zA-Z0-9\\.\\-_]{20,}"
      replacement: "***REDACTED***"

  identifiers:
    - pattern: "\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b"  # IP addresses
      replacement: "***.***.***.***"
    - pattern: "\\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\b"  # UUIDs
      replacement: "********-****-****-****-************"
    - pattern: "\\bsha256:[a-f0-9]{64}\\b"  # SHA256 hashes
      replacement: "sha256:************************************************"

  internal_info:
    - pattern: "10\\.10\\.10\\.\\d{1,3}"  # VPN IPs
      replacement: "10.10.10.***"
    - pattern: "/home/jnovoas/[^\\s]+"  # Home paths
      replacement: "~/***"
    - pattern: "\\bnova\\.ssh\\b"  # Container names
      replacement: "***container***"

  qhc_context:
    injection: "QHC_PHASE:{phase}|COHERENCE:{coherence}|S60:{timestamp}"
```

## SOMA - Security Integration

### Workflow con Firewall Semántico

```python
# SOMA Agent Execution Flow
def execute_agent_command(agent, command, context):
    # 1. Verificar autorización del agente
    if not firewall.is_agent_authorized(agent):
        log_blocked(agent, command, "UNAUTHORIZED_AGENT")
        return False

    # 2. Validar comando semánticamente
    if not firewall.validate_command(command, agent):
        log_blocked(agent, command, "SEMANTIC_VIOLATION")
        return False

    # 3. Verificar restricciones de fase QHC
    qhc_phase = get_current_qhc_phase()
    if not firewall.is_allowed_in_phase(command, qhc_phase):
        log_blocked(agent, command, f"QHC_RESTRICTION_{qhc_phase}")
        return False

    # 4. Verificar permisos de paths
    if not firewall.validate_paths(command, agent):
        log_blocked(agent, command, "PATH_RESTRICTION")
        return False

    # 5. Ejecutar comando
    output = execute(command)

    # 6. Sanitizar telemetría
    sanitized_output = sanitizer.sanitize(output)

    # 7. Agregar contexto QHC
    context_injected = f"{sanitized_output} | QHC:{qhc_phase.name}|S60:{qhc_phase.timestamp_s60}"

    return context_injected
```

### Agentes SOMA con Roles y Permisos

| Agente | Rol | Permisos | Restricciones |
|---------|------|-----------|--------------|
| **claude-opus** | Orchestrator | Completo | Ninguna |
| **claude-glm** | Worker | Lectura, ejecución segura | No puede escribir paths protegidos |
| **claude-qwen** | Worker | Lectura, ejecución segura | No puede escribir paths protegidos |
| **gemini** | Researcher | Solo lectura | No puede ejecutar comandos |
| **qwen-3.5-plus** | Architect | Alto | Debe consultar para cambios críticos |

### Eventos de Seguridad SOMA

```yaml
security_events:
  - id: "sec-001"
    timestamp: "2026-02-26T07:00:00Z"
    type: "agent_blocked"
    agent: "gemini"
    command: "rm -rf /etc/systemd/system"
    reason: "DESTRUCTIVE_COMMAND_NOT_ALLOWED"
    qhc_phase: "YOD"

  - id: "sec-002"
    timestamp: "2026-02-26T07:00:00Z"
    type: "telemetry_sanitized"
    agent: "claude-glm"
    original: "Connected to 10.10.10.2 with api_key=abc123xyz"
    sanitized: "Connected to 10.10.10.*** with api_key=***REDACTED***"
    qhc_context: "QHC:VAV|COHERENCE:0.85|S60:S60[2026;02,26,07,00]"
```

## Implementación en sentinel

### Componentes a Deployar

```
/home/jnovoas/Dev/sentinel/
├── .soma/
│   ├── security/
│   │   ├── semantic_firewall.py      # Firewall IA
│   │   ├── telemetry_sanitizer.py    # Sanitizador
│   │   ├── rules/
│   │   │   ├── agents.yaml          # Permisos por agente
│   │   │   ├── commands.yaml        # Reglas de comandos
│   │   │   └── sanitization.yaml    # Reglas de sanitización
│   │   └── audit/
│   │       └── blocked.log          # Log de bloqueos
│   └── ...
```

### Systemd Services

```bash
# Firewall semántico
[Unit]
Description=SOMA Semantic Firewall for AI Agents
After=me60os-qhc-agent.service

[Service]
Type=simple
User=jnovoas
ExecStart=/usr/bin/python3 /home/jnovoas/Dev/sentinel/.soma/security/semantic_firewall.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Sanitizador de telemetría
[Unit]
Description=SOMA Telemetry Sanitizer
After=soma-semantic-firewall.service

[Service]
Type=simple
User=jnovoas
ExecStart=/usr/bin/python3 /home/jnovoas/Dev/sentinel/.soma/security/telemetry_sanitizer.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Conclusión

**SOMA incluye una capa de seguridad robusta:**

1. **Firewall Semántico** - Protege contra comandos maliciosos de IA
2. **Sanitización de Telemetría** - Protege datos sensibles
3. **Integración QHC** - Restricciones contextuales según fase respiratoria
4. **Audit Completo** - Todo se registra con contexto S60

Esta capa asegura que los agentes SOMA operen de forma segura mientras coordinan las capacidades de ME-60OS en sentinel.
