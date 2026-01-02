# Sentinel - Examples for Researchers

## Overview

This document provides practical examples of how researchers can use Sentinel for scientific computing, data analysis, and distributed systems research.

## Table of Contents

1. [Quick Start for Researchers](#quick-start-for-researchers)
2. [Python SDK Examples](#python-sdk-examples)
3. [API Usage Examples](#api-usage-examples)
4. [Data Analysis Workflows](#data-analysis-workflows)
5. [Performance Benchmarking](#performance-benchmarking)
6. [Distributed Computing](#distributed-computing)
7. [AI/ML Integration](#aiml-integration)

---

## Quick Start for Researchers

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sentinel.git
cd sentinel

# Start the system
sudo sctl start

# Verify system health
sctl status --json
```

### Expected Output

```json
{
  "cpu_load": 0.9,
  "ebpf_lsm": false,
  "memory_used": 2248704,
  "pulse": true,
  "semantic_vectors": {
    "coherence": 0.96,
    "entropy": 0.073,
    "tte_us": 3.23
  }
}
```

---

## Python SDK Examples

### Example 1: System Coherence Monitoring

```python
#!/usr/bin/env python3
"""
Monitor system coherence in real-time for research analysis
"""

import requests
import time
import pandas as pd
from datetime import datetime

class SentinelMonitor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.data = []
    
    def get_status(self):
        """Fetch current system status"""
        response = requests.get(f"{self.base_url}/api/v1/health")
        return response.json()
    
    def get_semantic_vectors(self):
        """Get semantic vector measurements"""
        response = requests.get(f"{self.base_url}/api/v1/dashboard/status")
        data = response.json()
        return {
            'coherence': data.get('coherence', 0),
            'entropy': data.get('entropy', 0),
            'tte_us': data.get('tte_us', 0),
            'timestamp': datetime.now()
        }
    
    def collect_data(self, duration_seconds=60, interval=1):
        """Collect data for analysis"""
        print(f"Collecting data for {duration_seconds} seconds...")
        
        end_time = time.time() + duration_seconds
        while time.time() < end_time:
            vectors = self.get_semantic_vectors()
            self.data.append(vectors)
            time.sleep(interval)
        
        return pd.DataFrame(self.data)
    
    def analyze_coherence(self):
        """Analyze coherence patterns"""
        df = pd.DataFrame(self.data)
        
        stats = {
            'mean_coherence': df['coherence'].mean(),
            'std_coherence': df['coherence'].std(),
            'min_coherence': df['coherence'].min(),
            'max_coherence': df['coherence'].max(),
            'mean_entropy': df['entropy'].mean(),
            'mean_tte': df['tte_us'].mean()
        }
        
        return stats

# Usage
if __name__ == "__main__":
    monitor = SentinelMonitor()
    
    # Collect 5 minutes of data
    df = monitor.collect_data(duration_seconds=300, interval=1)
    
    # Analyze
    stats = monitor.analyze_coherence()
    print("\nCoherence Analysis:")
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}")
    
    # Save for further analysis
    df.to_csv('sentinel_coherence_data.csv', index=False)
    print("\nData saved to sentinel_coherence_data.csv")
```

### Example 2: AI Query Analysis

```python
#!/usr/bin/env python3
"""
Analyze AI response patterns and latency
"""

import requests
import time
import statistics

class AIAnalyzer:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def query_ai(self, prompt, max_tokens=100, temperature=0.3):
        """Query the AI and measure latency"""
        start_time = time.time()
        
        response = requests.post(
            f"{self.base_url}/api/v1/ai/query",
            json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            data = response.json()
            return {
                'response': data.get('response'),
                'model': data.get('model'),
                'latency_ms': latency,
                'success': True
            }
        else:
            return {
                'error': response.text,
                'latency_ms': latency,
                'success': False
            }
    
    def benchmark_ai(self, prompts, iterations=10):
        """Benchmark AI performance"""
        print(f"Benchmarking AI with {len(prompts)} prompts, {iterations} iterations each...")
        
        for prompt in prompts:
            latencies = []
            for i in range(iterations):
                result = self.query_ai(prompt)
                if result['success']:
                    latencies.append(result['latency_ms'])
                print(f"  Iteration {i+1}/{iterations}: {result['latency_ms']:.2f}ms")
            
            self.results.append({
                'prompt': prompt[:50] + '...',
                'mean_latency': statistics.mean(latencies),
                'std_latency': statistics.stdev(latencies) if len(latencies) > 1 else 0,
                'min_latency': min(latencies),
                'max_latency': max(latencies),
                'p95_latency': sorted(latencies)[int(len(latencies) * 0.95)]
            })
        
        return self.results
    
    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("AI PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        for result in self.results:
            print(f"\nPrompt: {result['prompt']}")
            print(f"  Mean Latency: {result['mean_latency']:.2f}ms")
            print(f"  Std Dev:      {result['std_latency']:.2f}ms")
            print(f"  Min:          {result['min_latency']:.2f}ms")
            print(f"  Max:          {result['max_latency']:.2f}ms")
            print(f"  P95:          {result['p95_latency']:.2f}ms")

# Usage
if __name__ == "__main__":
    analyzer = AIAnalyzer()
    
    # Test prompts
    prompts = [
        "Explain quantum computing in 50 words",
        "What is the difference between supervised and unsupervised learning?",
        "Describe the TCP/IP protocol stack"
    ]
    
    # Run benchmark
    results = analyzer.benchmark_ai(prompts, iterations=5)
    analyzer.print_results()
```

### Example 3: TruthSync Verification

```python
#!/usr/bin/env python3
"""
Verify claims using TruthSync protocol
"""

import requests
import json

class TruthSyncClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def verify_claim(self, text, metadata=None):
        """Verify a single claim"""
        response = requests.post(
            f"{self.base_url}/api/v1/truthsync/verify",
            json={
                "text": text,
                "metadata": metadata or {}
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Verification failed: {response.text}")
    
    def batch_verify(self, claims):
        """Verify multiple claims"""
        results = []
        for claim in claims:
            result = self.verify_claim(claim)
            results.append({
                'claim': claim,
                'confidence': result.get('confidence'),
                'status': result.get('status'),
                'processing_time_us': result.get('processing_time_us')
            })
        return results

# Usage
if __name__ == "__main__":
    client = TruthSyncClient()
    
    # Scientific claims to verify
    claims = [
        "Water boils at 100°C at sea level",
        "The speed of light is approximately 299,792,458 m/s",
        "DNA is composed of four nucleotide bases"
    ]
    
    print("Verifying scientific claims...\n")
    results = client.batch_verify(claims)
    
    for result in results:
        print(f"Claim: {result['claim']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Status: {result['status']}")
        print(f"  Processing Time: {result['processing_time_us']}μs\n")
```

---

## Data Analysis Workflows

### Example 4: Time-Series Analysis

```python
#!/usr/bin/env python3
"""
Analyze system metrics over time
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class MetricsAnalyzer:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_analytics(self, hours=24):
        """Fetch analytics data"""
        response = requests.get(
            f"{self.base_url}/api/v1/analytics/statistics",
            params={"hours": hours}
        )
        return response.json()
    
    def plot_coherence_trend(self, data):
        """Plot coherence over time"""
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['coherence'], label='Coherence', linewidth=2)
        plt.axhline(y=0.90, color='r', linestyle='--', label='Threshold (0.90)')
        plt.xlabel('Time')
        plt.ylabel('Coherence')
        plt.title('System Coherence Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('coherence_trend.png', dpi=300)
        print("Plot saved to coherence_trend.png")

# Usage
if __name__ == "__main__":
    analyzer = MetricsAnalyzer()
    data = analyzer.get_analytics(hours=24)
    analyzer.plot_coherence_trend(data)
```

---

## Performance Benchmarking

### Example 5: System Load Testing

```python
#!/usr/bin/env python3
"""
Load test Sentinel API endpoints
"""

import requests
import concurrent.futures
import time
import statistics

class LoadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def single_request(self, endpoint):
        """Make a single request and measure latency"""
        start = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            latency = (time.time() - start) * 1000
            return {
                'success': response.status_code == 200,
                'latency_ms': latency,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'latency_ms': (time.time() - start) * 1000,
                'error': str(e)
            }
    
    def load_test(self, endpoint, num_requests=100, concurrency=10):
        """Run load test"""
        print(f"Load testing {endpoint} with {num_requests} requests, concurrency={concurrency}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.single_request, endpoint) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r['success']]
        latencies = [r['latency_ms'] for r in successful]
        
        if latencies:
            return {
                'endpoint': endpoint,
                'total_requests': num_requests,
                'successful': len(successful),
                'failed': num_requests - len(successful),
                'success_rate': len(successful) / num_requests * 100,
                'mean_latency': statistics.mean(latencies),
                'median_latency': statistics.median(latencies),
                'p95_latency': sorted(latencies)[int(len(latencies) * 0.95)],
                'p99_latency': sorted(latencies)[int(len(latencies) * 0.99)],
                'min_latency': min(latencies),
                'max_latency': max(latencies)
            }
        else:
            return {'error': 'All requests failed'}

# Usage
if __name__ == "__main__":
    tester = LoadTester()
    
    endpoints = [
        "/api/v1/health",
        "/api/v1/dashboard/status",
        "/api/v1/analytics/statistics?hours=1"
    ]
    
    print("="*80)
    print("LOAD TEST RESULTS")
    print("="*80)
    
    for endpoint in endpoints:
        result = tester.load_test(endpoint, num_requests=100, concurrency=10)
        
        if 'error' not in result:
            print(f"\nEndpoint: {result['endpoint']}")
            print(f"  Success Rate: {result['success_rate']:.2f}%")
            print(f"  Mean Latency: {result['mean_latency']:.2f}ms")
            print(f"  Median Latency: {result['median_latency']:.2f}ms")
            print(f"  P95 Latency: {result['p95_latency']:.2f}ms")
            print(f"  P99 Latency: {result['p99_latency']:.2f}ms")
```

---

## Distributed Computing

### Example 6: Multi-Node Coordination

```python
#!/usr/bin/env python3
"""
Coordinate multiple Sentinel nodes for distributed research
"""

import requests
import json
from typing import List, Dict

class DistributedSentinel:
    def __init__(self, nodes: List[str]):
        """
        Initialize with list of node URLs
        Example: ["http://node1:8000", "http://node2:8000"]
        """
        self.nodes = nodes
    
    def get_cluster_status(self) -> Dict:
        """Get status from all nodes"""
        statuses = {}
        for node in self.nodes:
            try:
                response = requests.get(f"{node}/api/v1/health", timeout=5)
                statuses[node] = response.json()
            except Exception as e:
                statuses[node] = {'error': str(e)}
        return statuses
    
    def calculate_cluster_coherence(self) -> float:
        """Calculate average coherence across cluster"""
        coherences = []
        for node in self.nodes:
            try:
                response = requests.get(f"{node}/api/v1/dashboard/status", timeout=5)
                data = response.json()
                coherences.append(data.get('coherence', 0))
            except:
                continue
        
        return sum(coherences) / len(coherences) if coherences else 0
    
    def distributed_query(self, prompt: str) -> List[Dict]:
        """Query all nodes and compare responses"""
        results = []
        for node in self.nodes:
            try:
                response = requests.post(
                    f"{node}/api/v1/ai/query",
                    json={"prompt": prompt, "max_tokens": 100},
                    timeout=30
                )
                results.append({
                    'node': node,
                    'response': response.json(),
                    'success': True
                })
            except Exception as e:
                results.append({
                    'node': node,
                    'error': str(e),
                    'success': False
                })
        return results

# Usage
if __name__ == "__main__":
    # Configure your cluster nodes
    cluster = DistributedSentinel([
        "http://localhost:8000",
        # Add more nodes as needed
    ])
    
    # Check cluster health
    print("Cluster Status:")
    statuses = cluster.get_cluster_status()
    for node, status in statuses.items():
        print(f"  {node}: {status.get('status', 'error')}")
    
    # Calculate cluster coherence
    coherence = cluster.calculate_cluster_coherence()
    print(f"\nCluster Coherence: {coherence:.4f}")
```

---

## AI/ML Integration

### Example 7: Model Performance Comparison

```python
#!/usr/bin/env python3
"""
Compare different AI models available in Sentinel
"""

import requests
import time

class ModelComparator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_available_models(self):
        """Get list of available models"""
        response = requests.get(f"{self.base_url}/api/v1/ai/health")
        data = response.json()
        return data.get('models_available', [])
    
    def test_model(self, model_name, test_prompts):
        """Test a specific model"""
        results = []
        for prompt in test_prompts:
            start = time.time()
            # Note: You'd need to modify the API to support model selection
            response = requests.post(
                f"{self.base_url}/api/v1/ai/query",
                json={"prompt": prompt, "max_tokens": 100}
            )
            latency = (time.time() - start) * 1000
            
            results.append({
                'prompt': prompt,
                'latency_ms': latency,
                'response_length': len(response.json().get('response', ''))
            })
        
        return results

# Usage
if __name__ == "__main__":
    comparator = ModelComparator()
    
    # Get available models
    models = comparator.get_available_models()
    print(f"Available models: {models}")
    
    # Test prompts
    test_prompts = [
        "Explain machine learning",
        "What is quantum computing?",
        "Describe neural networks"
    ]
    
    # Compare models (if multiple available)
    for model in models:
        print(f"\nTesting model: {model}")
        results = comparator.test_model(model, test_prompts)
        avg_latency = sum(r['latency_ms'] for r in results) / len(results)
        print(f"  Average latency: {avg_latency:.2f}ms")
```

---

## Best Practices for Researchers

### 1. Data Collection
- Always timestamp your measurements
- Use consistent sampling intervals
- Store raw data for reproducibility

### 2. Performance Testing
- Warm up the system before benchmarking
- Run multiple iterations for statistical significance
- Document system configuration

### 3. Error Handling
- Implement timeouts for all API calls
- Log errors for debugging
- Use try-except blocks appropriately

### 4. Reproducibility
- Document all parameters
- Use version control for scripts
- Save configuration files

### 5. Collaboration
- Share scripts with colleagues
- Document your methodology
- Publish results with code

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **RESEARCH.md**: Scientific documentation
- **STYLE_GUIDE.md**: Coding conventions
- **GitHub Issues**: Report bugs or request features

---

## Citation

If you use these examples in your research, please cite:

```bibtex
@software{sentinel_examples2026,
  title = {Sentinel Research Examples},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/yourusername/sentinel}
}
```

---

**Happy researching! 🔬**
