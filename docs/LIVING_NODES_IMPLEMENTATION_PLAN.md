# Implementation Plan: Sentinel Living Nodes - Phase 1

## Goal

Implement the first functional components of Sentinel Living Nodes to validate the biological architecture concepts:

1. **Swarm Simulation** (n8n): 100 autonomous nodes negotiating traffic
2. **Unikernel Specification**: Minimal OS for node (eBPF + IA only)
3. **Bio-Watchdog Prototype**: Self-healing circuit design

---

## Proposed Changes

### Component 1: Swarm Simulation (n8n Workflows)

#### New Files

##### [NEW] `orchestrator/workflows/living_nodes_swarm_simulation.json`
n8n workflow that simulates 100 autonomous nodes with:
- **Node Agent**: Each node as a sub-workflow
- **Mesh Communication**: Nodes discover and communicate with neighbors
- **Load Balancing**: Nodes negotiate traffic distribution
- **Failover**: Automatic redistribution when a node "dies"
- **Metrics Collection**: Track swarm behavior (latency, throughput, failures)

**Key Features**:
- Gossip protocol simulation (each node broadcasts state to neighbors)
- Dynamic topology (nodes can join/leave)
- Zero-trust handshake (cryptographic verification between nodes)
- Emergent behavior tracking (load balancing without central coordinator)

---

##### [NEW] `tests/swarm_simulation/node_agent.py`
Python script representing a single autonomous node:
```python
class LivingNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors
        self.buffer = []
        self.ai_model = load_guardian_alpha()
        self.energy_level = 100  # %
        
    async def process_traffic(self, packet):
        # AI decides: keep, compress, or discard
        decision = self.ai_model.analyze(packet)
        if decision == "keep":
            self.buffer.append(packet)
        elif decision == "compress":
            compressed = compress(packet)
            self.buffer.append(compressed)
        # else: discard
        
    async def negotiate_load(self):
        # Gossip with neighbors about current load
        my_load = len(self.buffer)
        neighbor_loads = await self.query_neighbors()
        
        # If overloaded, ask neighbor to take some traffic
        if my_load > THRESHOLD:
            lightest_neighbor = min(neighbor_loads)
            await self.transfer_buffer(lightest_neighbor)
    
    async def heartbeat(self):
        # Broadcast "I'm alive" to neighbors
        await self.broadcast({"type": "heartbeat", "id": self.id})
```

---

##### [NEW] `tests/swarm_simulation/swarm_orchestrator.py`
Orchestrator that spawns 100 nodes and monitors swarm behavior:
```python
class SwarmOrchestrator:
    def __init__(self, num_nodes=100):
        self.nodes = []
        self.topology = self.generate_mesh_topology(num_nodes)
        
    def generate_mesh_topology(self, n):
        # Each node connected to 4-6 neighbors (random mesh)
        topology = {}
        for i in range(n):
            neighbors = random.sample(range(n), k=random.randint(4, 6))
            topology[i] = [n for n in neighbors if n != i]
        return topology
    
    async def spawn_nodes(self):
        for node_id, neighbors in self.topology.items():
            node = LivingNode(node_id, neighbors)
            self.nodes.append(node)
            asyncio.create_task(node.run())
    
    async def inject_traffic(self, rate_pps):
        # Inject packets into random nodes
        while True:
            packet = generate_packet()
            target_node = random.choice(self.nodes)
            await target_node.process_traffic(packet)
            await asyncio.sleep(1.0 / rate_pps)
    
    async def kill_random_node(self):
        # Simulate node failure
        victim = random.choice(self.nodes)
        print(f"Killing node {victim.id}")
        victim.stop()
        self.nodes.remove(victim)
        # Observe how swarm heals
```

---

### Component 2: Unikernel Specification

#### [NEW] `docs/UNIKERNEL_SPECIFICATION.md`
Detailed specification for minimal OS:
- **Base**: MirageOS (OCaml) or IncludeOS (C++)
- **Components**: 
  - eBPF runtime (for packet processing)
  - TensorFlow Lite Micro (for AI inference)
  - Minimal TCP/IP stack
  - Cryptographic library (libsodium)
- **Size**: < 10 MB
- **Boot time**: < 100ms
- **Memory footprint**: < 256 MB

---

#### [NEW] `unikernel/config.ml` (MirageOS example)
```ocaml
open Mirage

let main =
  foreign
    ~packages:[
      package "mirage-net-xen";
      package "tcpip";
      package "tls";
    ]
    "Unikernel.Main" (stackv4 @-> job)

let stack = generic_stackv4 default_network

let () =
  register "sentinel_node" [main $ stack]
```

---

### Component 3: Bio-Watchdog Circuit Design

#### [NEW] `hardware/bio_watchdog/schematic.pdf`
Circuit schematic for hardware watchdog:
- **MCU**: STM32F4 (ARM Cortex-M4)
- **Watchdog Timer**: Internal WDT + External TPL5010
- **Power Control**: MOSFET for hard reset
- **Tamper Detection**: Capacitive touch + Hall effect sensor

---

#### [NEW] `hardware/bio_watchdog/firmware.c`
Bare-metal C firmware for watchdog:
```c
#include "stm32f4xx.h"

#define HEARTBEAT_TIMEOUT_MS 1000
#define TAMPER_PIN GPIO_PIN_0

volatile uint32_t last_heartbeat = 0;

void watchdog_init() {
    // Configure independent watchdog
    IWDG->KR = 0xCCCC;  // Start watchdog
    IWDG->KR = 0x5555;  // Enable register access
    IWDG->PR = 6;       // Prescaler 256
    IWDG->RLR = 4095;   // Reload value (max)
    IWDG->KR = 0xAAAA;  // Reload counter
}

void check_heartbeat() {
    uint32_t now = HAL_GetTick();
    if ((now - last_heartbeat) > HEARTBEAT_TIMEOUT_MS) {
        // No heartbeat from main CPU → trigger reset
        trigger_hard_reset();
    }
}

void check_tamper() {
    if (HAL_GPIO_ReadPin(GPIOA, TAMPER_PIN) == GPIO_PIN_SET) {
        // Physical tamper detected → self-destruct
        crypto_selfdestruct();
        trigger_permanent_shutdown();
    }
}

int main() {
    watchdog_init();
    
    while(1) {
        check_heartbeat();
        check_tamper();
        IWDG->KR = 0xAAAA;  // Feed watchdog
        HAL_Delay(100);
    }
}
```

---

## Verification Plan

### 1. Swarm Simulation Tests

**Test 1: Node Discovery**
```bash
cd tests/swarm_simulation
python3 swarm_orchestrator.py --nodes 10 --test discovery
```
**Expected**: All 10 nodes discover their neighbors within 5 seconds

**Test 2: Load Balancing**
```bash
python3 swarm_orchestrator.py --nodes 100 --traffic 10000pps --duration 60s
```
**Expected**: Traffic distributed evenly across nodes (std dev < 10%)

**Test 3: Failover**
```bash
python3 swarm_orchestrator.py --nodes 100 --kill-rate 1/min --duration 300s
```
**Expected**: Swarm maintains 99% throughput despite 5 node failures

---

### 2. Unikernel Build Test

**Test 1: Build Unikernel**
```bash
cd unikernel
mirage configure -t xen
make
```
**Expected**: Unikernel binary < 10 MB

**Test 2: Boot Time**
```bash
xl create -c sentinel_node.xl
```
**Expected**: Boot to network ready in < 100ms

---

### 3. Bio-Watchdog Hardware Test

**Manual Test** (requires hardware):
1. Flash firmware to STM32F4 board
2. Connect main CPU heartbeat signal to GPIO
3. Stop heartbeat signal
4. **Expected**: Watchdog triggers reset within 1 second
5. Touch tamper sensor
6. **Expected**: Watchdog triggers self-destruct sequence

---

## User Review Required

> [!IMPORTANT]
> **Swarm Simulation Scope**
> 
> The swarm simulation will use Python + asyncio to model 100 nodes. This is a **logical simulation**, not physical hardware. Is this acceptable for Phase 1, or do you want to deploy actual hardware nodes?

> [!WARNING]
> **Unikernel Choice**
> 
> Proposed unikernel base: **MirageOS** (OCaml-based, proven in production)
> 
> Alternative: **IncludeOS** (C++-based, easier for eBPF integration)
> 
> Which do you prefer, or should we prototype both?

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Swarm Simulation** | 1 week | 100-node Python simulation + metrics |
| **Unikernel Spec** | 1 week | Complete specification + build system |
| **Bio-Watchdog** | 1 week | Circuit schematic + firmware prototype |
| **Integration** | 1 week | Unikernel running on simulated swarm |
| **Total** | **4 weeks** | Functional Living Node prototype |

---

## Next Steps After Approval

1. Implement swarm simulation in Python
2. Create n8n workflow for visualization
3. Write unikernel specification
4. Design bio-watchdog circuit
5. Integrate all components
6. Document results

---

**Ready to proceed?** 🚀🧬
