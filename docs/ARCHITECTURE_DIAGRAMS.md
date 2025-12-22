# Architecture Diagrams - UML

Comprehensive UML diagrams for all systems.

---

## 1. Quantum Control Framework - Class Diagram

```mermaid
classDiagram
    class Resource {
        <<interface>>
        +measure_state() ResourceState
        +apply_control(size: int) bool
        +get_metrics() Dict
        +get_limits() Tuple
    }
    
    class ResourceState {
        +position: float
        +velocity: float
        +acceleration: float
        +timestamp: float
        +metadata: Dict
    }
    
    class PhysicsModel {
        <<interface>>
        +calculate_force(state, history) float
        +calculate_ground_state(history) float
        +get_damping_factor(state) float
    }
    
    class QuantumController {
        -resource: Resource
        -physics: PhysicsModel
        -history: List~ResourceState~
        -running: bool
        +start()
        +stop()
        +get_stats() Dict
        -_control_cycle()
    }
    
    class OptomechanicalCooling {
        -velocity_threshold: float
        -acceleration_threshold: float
        -cooling_factor: float
        +calculate_force(state, history) float
        +calculate_ground_state(history) float
        +get_damping_factor(state) float
    }
    
    class BufferResource {
        -current_size: int
        -min_size: int
        -max_size: int
        +measure_state() ResourceState
        +apply_control(size) bool
    }
    
    class ThreadPoolResource {
        -current_threads: int
        -min_threads: int
        -max_threads: int
        +measure_state() ResourceState
        +apply_control(threads) bool
    }
    
    class MemoryResource {
        -current_heap: int
        -min_heap: int
        -max_heap: int
        +measure_state() ResourceState
        +apply_control(heap) bool
    }
    
    Resource <|.. BufferResource
    Resource <|.. ThreadPoolResource
    Resource <|.. MemoryResource
    PhysicsModel <|.. OptomechanicalCooling
    QuantumController --> Resource
    QuantumController --> PhysicsModel
    QuantumController --> ResourceState
```

---

## 2. Neural Interface - Class Diagram

```mermaid
classDiagram
    class NeuralState {
        +spike_rate: float
        +spike_velocity: float
        +spike_acceleration: float
        +entropy: float
        +timestamp: float
    }
    
    class NeuralEntropyController {
        -target_rate: float
        -min_rate: float
        -max_rate: float
        -cooling_factor: float
        -base_damping: float
        -history: List~NeuralState~
        -ground_state: float
        +measure_state(spike_rate, timestamp) NeuralState
        +calculate_force(state) float
        +calculate_ground_state() float
        +get_damping_factor(state) float
        +compute_control(state) Tuple
        +update(spike_rate, timestamp) Tuple
    }
    
    class BoneTransducer {
        <<hardware>>
        +vibration_frequency: float
        +intensity: float
        +apply_stimulation(intensity, action)
    }
    
    class OPMSensor {
        <<hardware>>
        +read_magnetic_field() float
        +get_spike_rate() float
    }
    
    NeuralEntropyController --> NeuralState
    NeuralEntropyController --> BoneTransducer
    NeuralEntropyController --> OPMSensor
```

---

## 3. System Architecture - Component Diagram

```mermaid
graph TB
    subgraph Production["Production (quantum_control/)"]
        QC[QuantumController]
        PM[PhysicsModel]
        BR[BufferResource]
        TR[ThreadPoolResource]
        MR[MemoryResource]
    end
    
    subgraph Research["Research (research/)"]
        NC[NeuralEntropyController]
        BT[BoneTransducer]
        OPM[OPMSensor]
    end
    
    subgraph Infrastructure["Infrastructure"]
        NET[Network Buffers]
        CPU[Thread Pools]
        RAM[Memory Heaps]
    end
    
    subgraph Biology["Biological"]
        BRAIN[Neural Signals]
        BONE[Bone Conduction]
    end
    
    QC --> PM
    QC --> BR
    QC --> TR
    QC --> MR
    
    BR --> NET
    TR --> CPU
    MR --> RAM
    
    NC --> BT
    NC --> OPM
    
    OPM --> BRAIN
    BT --> BONE
    BONE --> BRAIN
    
    PM -.Same Physics.-> NC
```

---

## 4. Control Flow - Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Controller
    participant R as Resource
    participant P as Physics
    
    loop Every Poll Interval
        C->>R: measure_state()
        R-->>C: ResourceState
        
        C->>P: calculate_force(state, history)
        P-->>C: force
        
        C->>P: calculate_ground_state(history)
        P-->>C: ground_state
        
        C->>P: get_damping_factor(state)
        P-->>C: damping
        
        C->>C: compute_new_size()
        
        alt Size Changed
            C->>R: apply_control(new_size)
            R-->>C: success
        end
        
        C->>C: update_history(state)
    end
```

---

## 5. Neural Control Flow - Sequence Diagram

```mermaid
sequenceDiagram
    participant NC as NeuralController
    participant OPM as OPM Sensor
    participant BT as Bone Transducer
    participant BRAIN as Brain
    
    loop Continuous
        OPM->>BRAIN: Read magnetic field
        BRAIN-->>OPM: Spike rate
        
        OPM->>NC: spike_rate
        
        NC->>NC: measure_state()
        NC->>NC: calculate_force()
        NC->>NC: compute_control()
        
        alt Entropy > Ground State
            NC->>BT: cool(intensity)
            BT->>BRAIN: Calming vibration
        else Entropy < Ground State
            NC->>BT: heat(intensity)
            BT->>BRAIN: Excitatory vibration
        else Near Ground State
            NC->>BT: hold()
        end
    end
```

---

## 6. Data Flow - Architecture Diagram

```mermaid
graph LR
    subgraph Input
        M[Metrics]
        S[State]
    end
    
    subgraph Processing
        F[Force Calculation]
        G[Ground State]
        D[Damping]
    end
    
    subgraph Output
        C[Control Action]
        A[Apply]
    end
    
    M --> S
    S --> F
    S --> G
    S --> D
    
    F --> C
    G --> C
    D --> C
    
    C --> A
    A --> M
```

---

## 7. The Trinity - Conceptual Diagram

```mermaid
graph TD
    subgraph Trinity["E = mc²"]
        E[Energy<br/>MemoryResource]
        M[Mass<br/>BufferResource]
        C[Speed²<br/>ThreadResource²]
    end
    
    subgraph Physics["Same Physics"]
        OM[OptomechanicalCooling<br/>F = v² × (1 + a)]
    end
    
    subgraph Result["Throughput"]
        T[Throughput = Space × Time²]
    end
    
    M --> OM
    C --> OM
    E --> OM
    
    OM --> T
```

---

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph Production["Production Environment"]
        LB[Load Balancer]
        S1[Server 1<br/>Quantum Control]
        S2[Server 2<br/>Quantum Control]
        S3[Server 3<br/>Quantum Control]
    end
    
    subgraph Monitoring
        P[Prometheus]
        G[Grafana]
    end
    
    subgraph Research["Research Lab"]
        SIM[Neural Simulator]
        VITRO[In Vitro Testing]
    end
    
    LB --> S1
    LB --> S2
    LB --> S3
    
    S1 --> P
    S2 --> P
    S3 --> P
    
    P --> G
    
    SIM -.Future.-> VITRO
```

---

## 9. Evolution Timeline

```mermaid
gantt
    title Quantum Control Evolution
    dateFormat YYYY-MM
    section Production
    Buffer/Thread/Memory    :done, 2025-12, 2026-01
    DB/LoadBalancer        :active, 2026-01, 2026-03
    Production Deploy      :2026-03, 2026-06
    
    section Research
    Neural Simulation      :active, 2025-12, 2026-06
    In Vitro Testing       :2026-06, 2027-06
    Animal Studies         :2027-06, 2030-01
    Human Trials           :2030-01, 2035-01
    
    section Applications
    Deep Space             :2026-01, 2028-01
    Power Grids            :2026-06, 2028-06
    Medical Devices        :2030-01, 2035-01
```

---

All diagrams use Mermaid syntax for easy rendering in Markdown.
