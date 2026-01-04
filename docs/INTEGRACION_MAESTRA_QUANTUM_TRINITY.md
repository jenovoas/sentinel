# Sentinel - Quantum Trinity Integration Plan

**Date**: 2026-01-04  
**Status**: Implementation Roadmap  
**Version**: 2.0 - Technical Specification

---

## Overview

This document outlines the integration plan for Sentinel's quantum simulation components with the monitoring and visualization layers.

**Components to Integrate:**

- Quantum simulation engine (`quantum_lite.py`)
- Trinity 3D visualization (React/Three.js)
- eBPF monitoring (Guardian Alpha/Beta)
- Backend API (FastAPI)

---

## Phase 1: Quantum Data Visualization

### Objective
Connect the quantum rift detector's correlation matrix to the Trinity 3D visualization panel for real-time display.

### Existing Components

#### Quantum Rift Detection
```python
# /quantum/quantum_lite.py
# Generates correlation matrix for membrane network
# Output example:
[[ 1.0        -0.999999  -0.961594]
 [-0.999999   1.0        0.961586]
 [-0.961594   0.961586   1.0     ]]
```

#### Trinity GUI
```typescript
// /frontend/src/app/trinity/components/TrinityScene3D.tsx
// 3D visualization using Three.js
```

### Implementation

#### Backend API Endpoint
```python
# /backend/app/routers/quantum.py
from fastapi import APIRouter
from quantum.quantum_lite import SentinelQuantumLite
import numpy as np

router = APIRouter(prefix="/api/v1/quantum")

@router.get("/rift/correlation")
async def get_rift_correlation():
    """
    Returns quantum correlation matrix from membrane network
    """
    # Initialize quantum simulator
    sim = SentinelQuantumLite(n_membranes=3, n_levels=5)
    
    # Run simulation
    result = sim.detect_rift()
    
    return {
        "correlation_matrix": result["correlation_matrix"].tolist(),
        "max_correlation": float(result["max_correlation"]),
        "rift_detected": bool(result["rift_detected"]),
        "timestamp": datetime.now().isoformat()
    }
```

#### Frontend Integration
```typescript
// /frontend/src/app/trinity/page.tsx
interface QuantumData {
  correlation_matrix: number[][];
  max_correlation: number;
  rift_detected: boolean;
}

export default function TrinityPage() {
  const [data, setData] = useState<QuantumData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api/v1/quantum/rift/correlation');
      const json = await response.json();
      setData(json);
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <TrinityScene3D correlationMatrix={data?.correlation_matrix} />
      <CorrelationDisplay data={data} />
    </div>
  );
}
```

---

## Phase 2: Quantum Watchdog Service

### Objective
Monitor quantum simulation metrics and trigger alerts when values fall below thresholds.

### Concept
Monitor the standard deviation (sigma) of the correlation matrix. Low sigma indicates degraded quantum state.

### Implementation

```python
# /backend/app/services/quantum_watchdog.py
import asyncio
import logging
from quantum.quantum_lite import SentinelQuantumLite
import numpy as np

logger = logging.getLogger(__name__)

class QuantumWatchdog:
    """
    Monitors quantum simulation health metrics
    """
    
    def __init__(self, sigma_threshold: float = 0.5):
        self.sigma_threshold = sigma_threshold
        self.is_running = False
        self.sim = SentinelQuantumLite(n_membranes=3, n_levels=5)
        
    async def monitor(self):
        """
        Monitor quantum sigma every 10 seconds
        """
        self.is_running = True
        
        while self.is_running:
            try:
                # Run rift detection
                result = self.sim.detect_rift()
                
                # Calculate sigma (std dev of correlation matrix)
                correlation_matrix = result["correlation_matrix"]
                sigma = np.std(correlation_matrix)
                
                logger.info(f"Quantum Sigma: {sigma:.4f}")
                
                # Alert if below threshold
                if sigma < self.sigma_threshold:
                    logger.warning(
                        f"Quantum Sigma below threshold: "
                        f"{sigma:.4f} < {self.sigma_threshold}"
                    )
                    await self.send_alert({
                        "type": "quantum_degradation",
                        "sigma": sigma,
                        "threshold": self.sigma_threshold
                    })
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in quantum watchdog: {e}")
                await asyncio.sleep(10)
    
    async def send_alert(self, alert: dict):
        """
        Send alert to monitoring system
        """
        logger.warning(f"ALERT: {alert}")
        # TODO: Integrate with alerting system
    
    def stop(self):
        self.is_running = False
```

---

## Phase 3: Docker Container for External Users

### Objective
Package the quantum simulator in a Docker container for external researchers to run simulations.

### Dockerfile
```dockerfile
# /docker/Dockerfile.quantum-sim
FROM python:3.13-slim

LABEL maintainer="Sentinel Team"
LABEL description="Sentinel Quantum Simulator"
LABEL version="1.0.0"

WORKDIR /app

# Copy quantum simulator
COPY quantum/ /app/quantum/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p /app/output

# Entry point
COPY docker/quantum_sim_entrypoint.py /app/
CMD ["python", "quantum_sim_entrypoint.py"]
```

### Entrypoint Script
```python
# /docker/quantum_sim_entrypoint.py
"""
Sentinel Quantum Simulator - User-facing script
"""

import json
from datetime import datetime
from quantum.quantum_lite import SentinelQuantumLite
import numpy as np

def run_simulation():
    print("=" * 60)
    print("SENTINEL QUANTUM SIMULATOR v1.0")
    print("=" * 60)
    print()
    
    # Initialize simulator
    print("Initializing quantum simulator...")
    sim = SentinelQuantumLite(n_membranes=3, n_levels=5)
    
    print(f"  Membranes: 3")
    print(f"  Hilbert Dimension: 125")
    print()
    
    # Run rift detection
    print("Running rift detection...")
    result = sim.detect_rift()
    
    correlation_matrix = result["correlation_matrix"]
    max_correlation = result["max_correlation"]
    
    print(f"  Max Correlation: {max_correlation:.6f}")
    print()
    
    # Save results
    output = {
        "correlation_matrix": correlation_matrix.tolist(),
        "max_correlation": float(max_correlation),
        "rift_detected": bool(result["rift_detected"]),
        "timestamp": datetime.now().isoformat()
    }
    
    output_file = f"/app/output/simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    print()
    print("=" * 60)
    print("Simulation complete")
    print("=" * 60)

if __name__ == "__main__":
    run_simulation()
```

### Usage
```bash
# Build image
docker build -f docker/Dockerfile.quantum-sim -t sentinel-quantum-sim .

# Run simulation
docker run -v $(pwd)/output:/app/output sentinel-quantum-sim

# View results
cat output/simulation_*.json
```

---

## Phase 4: Resource Management Integration

### Objective
Connect the quantum control system with the resource management layer for dynamic optimization.

### Architecture

```
┌─────────────────────────────────────────┐
│     Quantum Simulation Layer            │
│  • Correlation matrix generation        │
│  • Rift detection                       │
│  • State evolution                      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│     Resource Management Layer           │
│  • Buffer allocation                    │
│  • Thread scheduling                    │
│  • Memory management                    │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│     Monitoring Layer                    │
│  • Metrics collection                   │
│  • Alert generation                     │
│  • Dashboard updates                    │
└─────────────────────────────────────────┘
```

### Implementation

```python
# /backend/app/services/resource_optimizer.py
import asyncio
from quantum.quantum_lite import SentinelQuantumLite
from quantum_control.core import QuantumController
from quantum_control.resources import BufferResource

class ResourceOptimizer:
    """
    Optimizes system resources based on quantum simulation metrics
    """
    
    def __init__(self):
        self.sim = SentinelQuantumLite(n_membranes=3, n_levels=5)
        self.controller = QuantumController(BufferResource())
        
    async def optimize_loop(self):
        """
        Continuous optimization loop
        """
        while True:
            # Run quantum simulation
            result = self.sim.detect_rift()
            correlation = result["max_correlation"]
            
            # Adjust resources based on correlation
            # High correlation = high load predicted
            if correlation > 0.9:
                await self.controller.increase_buffer_size()
            elif correlation < 0.5:
                await self.controller.decrease_buffer_size()
            
            await asyncio.sleep(10)
```

---

## Performance Metrics

### Quantum Simulation
- Hilbert space dimension: 125 (3 membranes × 5 levels)
- Correlation calculation: ~10ms
- Rift detection: ~50ms

### API Endpoints
- `/api/v1/quantum/rift/correlation`: ~60ms response time
- Update frequency: 5 seconds (configurable)

### Resource Usage
- Memory: ~50MB per simulation
- CPU: ~5% during simulation
- Network: ~1KB per API response

---

## Testing Plan

### Unit Tests
```python
# /tests/test_quantum_integration.py
import pytest
from backend.app.routers.quantum import get_rift_correlation

@pytest.mark.asyncio
async def test_rift_correlation_endpoint():
    result = await get_rift_correlation()
    
    assert "correlation_matrix" in result
    assert "max_correlation" in result
    assert isinstance(result["correlation_matrix"], list)
    assert 0.0 <= result["max_correlation"] <= 1.0
```

### Integration Tests
- Test quantum simulator → API → frontend data flow
- Verify watchdog alert generation
- Validate Docker container execution

---

## Deployment

### Prerequisites
- Python 3.13+
- Docker (for containerized deployment)
- PostgreSQL (for data persistence)

### Steps
1. Install dependencies: `pip install -r requirements.txt`
2. Start backend: `uvicorn backend.app.main:app`
3. Start frontend: `npm run dev`
4. Access Trinity dashboard: `http://localhost:3000/trinity`

---

## References

- Quantum Simulator: `/quantum/quantum_lite.py`
- Trinity GUI: `/frontend/src/app/trinity/`
- API Router: `/backend/app/routers/quantum.py`
- Resource Control: `/quantum_control/`

---

*Last updated: 2026-01-04*
*Version: 2.0 - Technical Specification*
