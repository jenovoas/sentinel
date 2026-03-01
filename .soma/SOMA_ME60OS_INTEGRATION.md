# SOMA - ME-60OS Agent Orchestrator Integration Plan

## Descubrimiento

El proyecto **ME-60OS** tiene un sistema de orquestación de agentes completo:

### Componentes Python (agents/)

| Agente | Función | Estado |
|---------|-----------|---------|
| **SystemMonitorAgent** | Monitor de recursos (CPU, memoria) | ✅ Implementado |
| **SecurityGuardianAgent** | Guardian de seguridad basado en entropía | ✅ Implementado |
| **NetworkResonanceAgent** | Sincronización MycNet (TQ → S60) | ✅ Implementado |
| **HarmonicDecisionAgent** | NPU - Decisiones armónicas | ✅ Implementado |
| **HolographicStorageAgent** | Almacenamiento holográfico | ✅ Implementado |
| **InertiaControllerAgent** | Control de inercia variable | ✅ Implementado |
| **ResonanceTuningAgent** | Sintonización de resonancia | ✅ Implementado |
| **AnomalyDetectorAgent** | Detección de anomalías | ✅ Implementado |

### Componentes Rust (src/)

| Componente | Función | Estado |
|-------------|-----------|---------|
| **AgentManager** | Gestor de agentes nativos (trait AgentSPA) | ✅ Implementado |
| **EnergyMonitorAgent** | Monitor de energía nativo | ✅ Implementado |
| **qhc-agent** | Driver YHWH 10-5-6-5 (1Hz) | ✅ Deployado |
| **adm-agent** | Métricas mesh TQ→SPA (0.858) | ✅ Deployado |
| **vid-agent** | Quantum cooling (10Hz) | ✅ Deployado |

### Orquestador Principal

**agent_orchestrator.py** - Gestor central de agentes:
- Carga configuración desde `agents_config.json`
- Instancia agentes dinámicamente
- Ejecuta ciclo `tick()` a 41Hz
- Despacha directivas al sistema
- Inyecta percepciones globales

## Arquitectura Integrada SOMA v3.0

```
┌─────────────────────────────────────────────────────────────────┐
│              SOMA Orchestration Layer (Python)                │
│  • Contracts Engine                                          │
│  • Handoffs Manager                                         │
│  • Task Scheduler                                           │
│  • State Tracker (S60 timestamps)                             │
└───────────────┬─────────────────────────────────────────────┘
                │ usa
┌───────────────▼─────────────────────────────────────────────┐
│      ME-60OS Agent Orchestrator (agent_orchestrator.py)    │
│  • SystemMonitorAgent                                       │
│  • SecurityGuardianAgent                                     │
│  • NetworkResonanceAgent (MycNet)                           │
│  • HarmonicDecisionAgent (NPU)                              │
│  • HolographicStorageAgent                                    │
│  • InertiaControllerAgent                                     │
└───────────────┬─────────────────────────────────────────────┘
                │ coordina
┌───────────────▼─────────────────────────────────────────────┐
│        ME-60OS Core Services (Rust)                          │
│  • AgentManager (nativos)                                      │
│  • qhc-agent (1Hz, YHWH 10-5-6-5)                        │
│  • adm-agent (TQ→SPA, coherencia 0.858)                      │
│  • vid-agent (quantum cooling, 10Hz)                            │
└───────────────┬─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│           ME-60OS Kernel & eBPF (Ring 0)                      │
│  • guardian_alpha_lsm (id=92)                                  │
│  • eBPF Ring Buffer (eventos → Cortex)                          │
│  • SPA Arithmetic (Base-60)                                     │
└─────────────────────────────────────────────────────────────┘
```

## Plan de Integración

### Fase 1: Revivir agent_orchestrator.py en sentinel

```bash
# Copiar a sentinel
scp ~/Dev/me-60os/agents/agent_orchestrator.py jnovoas@10.10.10.2:~/Dev/sentinel/.soma/

# Copiar agentes base
scp ~/Dev/me-60os/agents/*.py jnovoas@10.10.10.2:~/Dev/sentinel/.soma/agents/

# Crear directorio de configuración
ssh jnovoas@10.10.10.2 "mkdir -p ~/Dev/sentinel/.soma/agents/quantum"
```

### Fase 2: Integrar SOMA con ME-60OS Orchestrator

```python
# soma_me60os_bridge.py
from agent_orchestrator import AgentOrchestrator
from typing import Dict, Any

class SOMA_ME60OS_Bridge:
    """
    Puente entre SOMA y ME-60OS Agent Orchestrator.
    SOMA gestiona handoffs y contratos,
    ME-60OS gesta agentes del sistema.
    """

    def __init__(self):
        # Inicializar orquestador ME-60OS
        self.me60os_orch = AgentOrchestrator(
            config_path=".soma/agents_config.json",
            verbose=True
        )

        # SOMA state tracker
        self.soma_state = SOMAStateManager()

    def tick(self) -> Dict[str, Any]:
        """
        Ciclo principal SOMA-ME60OS.
        Llamado por SOMA cada tick (1Hz como qhc-agent).
        """
        # 1. Consultar QHC actual (desde qhc-agent)
        qhc_phase = self.get_qhc_phase()
        coherence = self.get_mesh_coherence()

        # 2. Consultar ME-60OS agents
        me60os_state = self.me60os_orch.get_agent_states()

        # 3. SOMA decide acciones de orquestación
        somma_actions = self.soma_state.compute_actions(
            qhc_phase=qhc_phase,
            coherence=coherence,
            me60os_state=me60os_state
        )

        # 4. Ejecutar handoffs pendientes
        self.process_handoffs(qhc_phase, coherence)

        # 5. Tick ME-60OS agents
        self.me60os_orch.tick({
            "qhc_phase": qhc_phase,
            "coherence": coherence,
            "somma_actions": somma_actions
        })

        return {
            "qhc_phase": qhc_phase,
            "coherence": coherence,
            "me60os_agents": me60os_state,
            "somma_actions": somma_actions
        }
```

### Fase 3: Mapeo de Agentes SOMA → ME-60OS

| SOMA Agente | ME-60OS Agente | Relación |
|--------------|-----------------|-----------|
| **claude-opus** | HarmonicDecisionAgent | Orquestador principal |
| **claude-glm** | SystemMonitorAgent | Ejecuta tareas monitoreadas |
| **claude-qwen** | NetworkResonanceAgent | Balancea carga por mesh |
| **gemini** | HolographicStorageAgent | Investigación y almacenamiento |
| **qwen-3.5-plus** | SecurityGuardianAgent | Auditoría y seguridad |

### Fase 4: Integración de Handoffs con ME-60OS

```python
# SOMA handoffs informan a ME-60OS agents
class HandoffManager:
    def execute_handoff(self, handoff: Handoff):
        """
        Ejecuta handoff informando a ME-60OS agents.
        """
        # 1. Notificar a NetworkResonanceAgent
        me60os_orch.notify_agent(
            "NetworkResonanceAgent",
            "HANDOFF_INCOMING"
        )

        # 2. Esperar fase QHC óptima
        if handoff.qhc_optimal_phase:
            wait_for_qhc_phase(handoff.qhc_optimal_phase)

        # 3. Verificar coherencia mesh
        coherence = get_mesh_coherence()
        if coherence < handoff.required_coherence:
            raise Exception(f"Coherencia insuficiente: {coherence}")

        # 4. Ejecutar handoff
        result = self.atomic_handoff(handoff)

        # 5. Notificar a SystemMonitorAgent
        me60os_orch.notify_agent(
            "SystemMonitorAgent",
            f"HANDOFF_COMPLETE:{handoff.id}"
        )

        return result
```

### Fase 5: Configuración de Agents (agents_config.json)

```json
{
  "agents": [
    {
      "name": "SomaMonitor",
      "module": "agents.level2_memory",
      "class": "SystemMonitorAgent",
      "enabled": true,
      "params": {
        "history_size": 100,
        "umrales": {"cpu": 85, "memoria": 90}
      }
    },
    {
      "name": "SomaSecurityGuardian",
      "module": "agents.level1_reactive",
      "class": "SecurityGuardianAgent",
      "enabled": true,
      "params": {
        "umbral_entropia": 65
      }
    },
    {
      "name": "SomaMyceliumSync",
      "module": "agents.network_resonance",
      "class": "NetworkResonanceAgent",
      "enabled": true,
      "params": {
        "target_coherence": "0,51,0"
      }
    },
    {
      "name": "SomaHarmonicOracle",
      "module": "agents.harmonic_decision",
      "class": "HarmonicDecisionAgent",
      "enabled": true,
      "params": {}
    },
    {
      "name": "SomaHoloMemory",
      "module": "agents.holographic_storage",
      "class": "HolographicStorageAgent",
      "enabled": true,
      "params": {}
    }
  ]
}
```

## Beneficios de la Integración

1. **Aprovechar código existente** - ME-60OS orquestator ya está probado
2. **S60 nativo** - Todos los cálculos en Base-60
3. **Resonancia armónica** - Agents siguen ciclo QHC automáticamente
4. **Mesh awareness** - NetworkResonanceAgent maneja MycNet
5. **Orquestación externa** - SOMA coordina handoffs entre agentes IA
6. **Zero duplicación** - Reusar ME-60OS infraestructura

## Archivos a Crear/Deployar

```
/home/jnovoas/Dev/sentinel/.soma/
├── agents/
│   ├── agent_orchestrator.py      # Desde ME-60OS
│   ├── base_agent.py              # Desde ME-60OS
│   ├── level1_reactive.py         # Desde ME-60OS
│   ├── level2_memory.py           # Desde ME-60OS
│   ├── level3_goal_based.py       # Desde ME-60OS
│   ├── harmonic_decision.py        # Desde ME-60OS
│   ├── network_resonance.py        # Desde ME-60OS
│   └── holographic_storage.py     # Desde ME-60OS
├── quantum/                      # Desde ME-60OS
│   └── s60_fixedpoint.py        # Librería S60
├── agents_config.json             # Configuración SOMA-ME60OS
├── soma_me60os_bridge.py         # Puente SOMA ↔ ME-60OS
└── soma_orchestrator.py          # Main entry point
```

## Próximos Pasos

1. **Deploy ME-60OS agents** a `~/Dev/sentinel/.soma/`
2. **Crear soma_me60os_bridge.py** para integración
3. **Configurar agents_config.json** para uso SOMA
4. **Crear soma-orchestrator.service** en sentinel
5. **Probar integración** con qhc-agent, adm-agent, vid-agent
6. **Implementar Fase 7 (DNS)** usando ME-60OS orquestación

## Conclusión

**SOMA v3.0 = SOMA Orchestration + ME-60OS Agent System**

No reescribimos nada de ME-60OS. SOMA se integra como capa superior que:
- Coordina handoffs entre agentes IA externos
- Usa ME-60OS agents para monitoreo del sistema
- Sigue ciclo QHC vía qhc-agent
- Balancea carga vía NetworkResonanceAgent
- Almacena estado vía HolographicStorageAgent

Esta es la arquitectura correcta: **SOMA como cerebro orquestador, ME-60OS como sistema nervioso**.
