# 🧪 TruthSync Stress Testing Guide

## Overview

Complete stress testing setup using **synthetic data** - no real data needed!

---

## Quick Start

### 1. Generate Synthetic Data

```bash
python3 generate_synthetic_data.py
```

This creates:
- `synthetic_claims_1k.json` - Quick testing (1K claims)
- `synthetic_claims_10k.json` - Stress testing (10K claims)
- `synthetic_claims_100k.json` - Production simulation (100K claims)

### 2. Run Local Stress Test

```bash
# Install locust
pip install locust

# Run test
locust -f locustfile.py --host http://localhost:8000
```

Open browser: http://localhost:8089

### 3. Run Headless Test

```bash
locust -f locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 1h \
  --headless
```

---

## Test Scenarios

### Scenario 1: Baseline Performance (30 min)

```bash
locust -f locustfile.py \
  --host http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 30m \
  --headless
```

**Objectives**:
- Validate 90.5x speedup
- Measure cache hit rate
- Baseline latency (P50, P95, P99)

**Success Criteria**:
- ✅ P99 latency < 10ms
- ✅ Cache hit rate > 80%
- ✅ Error rate < 0.1%

### Scenario 2: Stress Test (1 hour)

```bash
locust -f locustfile.py \
  --host http://localhost:8000 \
  --users 200 \
  --spawn-rate 20 \
  --run-time 1h \
  --headless
```

**Objectives**:
- Find breaking point
- Monitor resource usage
- Validate auto-scaling

**Success Criteria**:
- ✅ Sustained throughput > 10k RPS
- ✅ Memory stable (no leaks)
- ✅ CPU < 80%

### Scenario 3: Spike Test (15 min)

```bash
# Use custom spike script
python3 spike_test.py
```

**Objectives**:
- Test burst capacity
- Validate queue handling
- Recovery time

**Success Criteria**:
- ✅ Handles 10x spike
- ✅ Recovery < 30s
- ✅ No dropped requests

### Scenario 4: Endurance Test (4 hours)

```bash
locust -f locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 4h \
  --headless
```

**Objectives**:
- Memory leaks
- Performance degradation
- Cache effectiveness over time

**Success Criteria**:
- ✅ Latency stable (no drift)
- ✅ Memory stable
- ✅ Cache hit rate maintained

---

## Cloud Stress Testing (AWS)

### Setup (One-time)

```bash
# 1. Launch EC2 instances
aws ec2 run-instances \
  --image-id ami-xxxxx \
  --instance-type c6i.xlarge \
  --count 3 \
  --key-name your-key

# 2. Install dependencies
ssh ec2-user@instance-1
sudo yum install -y python3 git
pip3 install locust

# 3. Clone repo
git clone https://github.com/your-repo/truthsync.git
cd truthsync/truthsync-poc
```

### Run Distributed Test

```bash
# Master node (instance-1)
locust -f locustfile.py \
  --master \
  --expect-workers 2

# Worker nodes (instance-2, instance-3)
locust -f locustfile.py \
  --worker \
  --master-host <master-ip>
```

**Capacity**:
- 3x c6i.xlarge = ~30k RPS
- Cost: ~$2-3/hour

---

## Monitoring During Tests

### Prometheus Queries

```promql
# Request rate
rate(truthsync_requests_total[1m])

# Latency percentiles
histogram_quantile(0.99, truthsync_processing_seconds)

# Cache hit rate
truthsync_cache_hit_rate

# Error rate
rate(truthsync_errors_total[1m])
```

### Key Metrics to Watch

```
✅ REAL-TIME DASHBOARD

Performance:
  ├─ RPS: ___/sec (target: >10k)
  ├─ P50: ___ ms (target: <1ms)
  ├─ P95: ___ ms (target: <5ms)
  └─ P99: ___ ms (target: <10ms)

Cache:
  ├─ Hit rate: ___% (target: >80%)
  ├─ Size: ___ entries
  └─ Evictions: ___/sec

Resources:
  ├─ CPU: ___% (target: <70%)
  ├─ Memory: ___ MB (watch for leaks)
  └─ Connections: ___

Errors:
  ├─ 4xx: ___ (should be 0)
  ├─ 5xx: ___ (target: <0.1%)
  └─ Timeouts: ___ (should be 0)
```

---

## Expected Results

### With Synthetic Data (10K claims, 80% hit rate)

```
Baseline Performance:
  RPS: 10,000-50,000
  P50 latency: 0.5-1ms
  P99 latency: 2-5ms
  Cache hit rate: 80-85%

Stress Performance (200 users):
  RPS: 50,000-100,000
  P50 latency: 1-2ms
  P99 latency: 5-10ms
  Cache hit rate: 75-80%

Resource Usage:
  CPU: 40-60%
  Memory: 512MB-1GB
  Network: 10-50 Mbps
```

---

## Troubleshooting

### High Latency

```bash
# Check batch size
curl http://localhost:8000/stats

# Increase batch size
export BATCH_SIZE=1000

# Restart
./restart.sh
```

### Low Cache Hit Rate

```bash
# Check cache size
curl http://localhost:8000/stats

# Increase cache
export CACHE_SIZE=50000

# Restart
./restart.sh
```

### Memory Issues

```bash
# Check for leaks
valgrind --leak-check=full ./target/release/truthsync

# Profile memory
heaptrack ./target/release/truthsync
```

---

## Checklist

### Pre-Test
- [ ] Synthetic data generated
- [ ] Locust installed
- [ ] Monitoring configured
- [ ] Baseline metrics recorded

### During Test
- [ ] Monitor dashboard actively
- [ ] Log any anomalies
- [ ] Check resource usage
- [ ] Validate cache behavior

### Post-Test
- [ ] Analyze results
- [ ] Compare to targets
- [ ] Document findings
- [ ] Plan optimizations

---

## Cost Estimate

### Local Testing
- **Cost**: $0 (use your machine)
- **Capacity**: 1k-10k RPS
- **Duration**: Unlimited

### AWS Cloud Testing
- **3x c6i.xlarge**: ~$2-3/hour
- **Capacity**: 30k-50k RPS
- **Recommended**: 2-4 hours testing
- **Total cost**: ~$10-15

### GCP Cloud Testing
- **3x e2-standard-4**: ~$1-2/hour
- **Capacity**: 20k-30k RPS
- **Total cost**: ~$5-10

---

**Status**: Ready for stress testing ✅  
**Data**: 100% synthetic (no real data needed) ✅  
**Cost**: $0-15 depending on scale ✅
