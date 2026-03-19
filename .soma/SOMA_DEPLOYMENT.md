# SOMA Deployment - Arquitectura Final

## Premisa Crítica

**SOMA corre en sentinel y usa sentinel (ME-60OS) como infraestructura.**

## Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────────────┐
│                  Nodo: sentinel (10.10.10.2)               │
│                    Debian 13 trixie                          │
└─────────────────────────────────────────────────────────────────┘

    │
    ├── Ring 0 (Kernel)
    │   ├── guardian_alpha_lsm.c (id=92) ✅
    │   └── xdp_firewall.o (pendiente)
    │
    ├── ME-60OS (Sistema Nervioso) ✅
    │   ├── qhc-agent.service (1Hz, YHWH 10-5-6-5)
    │   ├── adm-agent.service (TQ→SPA, coherencia 0.858)
    │   ├── vid-agent.service (quantum cooling, 10Hz)
    │   └── audit-cortex-bridge.service
    │
    ├── SOMA (Orquestador Multi-Agente) ⏳
    │   ├── state.yaml (estado compartido)
    │   ├── contracts/ (definiciones)
    │   ├── handoffs/ (transferencias)
    │   └── agents/ (coordinación)
    │
    ├── Contenedores Podman ✅
    │   ├── sentinel-postgres, sentinel-redis
    │   ├── sentinel-backend (:8000)
    │   ├── sentinel-frontend (:3000)
    │   ├── sentinel-grafana (:3001)
    │   ├── sentinel-n8n (:5678)
    │   └── ... (15 servicios totales)
    │
    └── Host Services ✅
        ├── auditd (con YHWH-17 throttling)
        ├── PowerDNS Slave (ns3)
        └── Samba AD BDC
```

## SOMA Deployment Plan

### Paso 1: Deploy SOMA en sentinel

```bash
# Desde fenix
rsync -avz ~/Dev/sentinel/.soma/ sentinel:~/Dev/sentinel/.soma/

# Crear directorio de logs
ssh -p 4222 jnovoas@10.10.10.2 "mkdir -p ~/logs/soma"
```

### Paso 2: Crear Systemd Service

```bash
# archivo: /etc/systemd/system/soma-orchestrator.service
[Unit]
Description=SOMA Multi-Agent Orchestrator
After=me60os-qhc-agent.service me60os-adm-agent.service me60os-vid-agent.service
Requires=me60os-qhc-agent.service me60os-adm-agent.service

[Service]
Type=simple
User=jnovoas
WorkingDirectory=/home/jnovoas/Dev/sentinel/.soma
ExecStart=/usr/bin/python3 soma_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Paso 3: SOMA Consume ME-60OS APIs

#### qhc-agent APIs (Unix Socket)

```bash
# Obtener fase actual
socat - UNIX-CONNECT:/run/soma/qhc.sock <<< "GET_PHASE"
# Respuesta: VAV|6|0.35|S60[2026;02,26,07,00]

# Esperar fase específica
socat - UNIX-CONNECT:/run/soma/qhc.sock <<< "WAIT_PHASE YOD"
```

#### adm-agent APIs (Unix Socket)

```bash
# Obtener coherencia mesh
socat - UNIX-CONNECT:/run/soma/adm.sock <<< "GET_COHERENCE"
# Respuesta: 0.858|S60[000;51,00,00,00]|255
```

### Paso 4: SOMA Workflow

```python
# SOMA Orchestration Loop
while True:
    # 1. Consultar QHC actual
    phase = qhc_client.get_phase()
    coherence = adm_client.get_coherence()

    # 2. Verificar condiciones
    if coherence > 0.8 and phase.name == "VAV":
        # Fase óptima para procesar
        process_pending_tasks()

    # 3. Procesar handoffs
    if needs_handoff():
        validate_and_transfer()

    # 4. Actualizar estado
    update_state_with_s60_timestamp()

    # 5. Dormir ciclo QHC
    sleep(1)  # 1Hz como qhc-agent
```

## SOMA - ME-60OS Integration

| SOMA Componente | ME-60OS Servicio | Mecanismo |
|-----------------|-----------------|-----------|
| QHC Phase | qhc-agent | Unix Socket `/run/soma/qhc.sock` |
| Mesh Coherence | adm-agent | Unix Socket `/run/soma/adm.sock` |
| Quantum Cooling | vid-agent | Unix Socket `/run/soma/vid.sock` |
| Events | audit-cortex-bridge | eBPF Ring Buffer |
| Timestamps | qhc-agent | Formato S60 string |

## Fases Sentinel (Estado Actual)

| Fase | Estado | Agente |
|-------|--------|---------|
| 0-6 | ✅ COMPLETAS | claude-opus |
| 7 | ⏳ PENDIENTE | TBA |

## Próximos Pasos

### Inmediato

1. Deploy SOMA scripts en sentinel
2. Crear soma-orchestrator.service
3. Implementar APIs Unix Socket en ME-60OS

### Fase 7 (DNS)

1. SOMA asigna agente a tarea dns-001
2. Espera fase QHC = VAV (óptimo para flujo DNS)
3. Verifica coherencia mesh > 0.8
4. Ejecuta handoff atómico
5. Agente crea registro PowerDNS
6. SOMA valida y completa Fase 7

### Post-Deployment

1. SOMA monitorea todos los servicios
2. Auto-balanceo de carga según coherencia
3. Handoffs entre agentes según ciclo QHC
4. Quantum reset cada T=68s

## Archivos en sentinel

```
/home/jnovoas/Dev/sentinel/
├── .soma/
│   ├── state.yaml                  # Estado orquestación
│   ├── contracts/                 # Definiciones
│   ├── handoffs/                 # Handoffs activos
│   ├── tasks/                    # Tareas pendientes
│   ├── soma_orchestrator.py      # Loop principal
│   └── scripts/
│       ├── deploy.sh              # Deploy script
│       └── start.sh              # Iniciar SOMA
├── me-60os/                     # ME-60OS (instalado)
├── mycnet/                      # MycNet scripts
└── quantum/                     # Experimentos
```

## Conclusión

**SOMA es el cerebro orquestador que corre sobre el sistema nervioso ME-60OS en sentinel.**

No hay separación entre "Sentinel" y "ME-60OS" — son lo mismo. SOMA es la capa de inteligencia que coordina las capacidades del sistema.
