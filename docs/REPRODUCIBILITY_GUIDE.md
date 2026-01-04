# 🔬 Sentinel Cortex - Reproducibility Guide for Researchers

**Version**: 2.0  
**Date**: 2026-01-01  
**Purpose**: Independent validation and research verification

---

## Overview

This guide enables researchers and skeptics to independently validate all claims made about Sentinel Cortex. All tests are reproducible and use open-source tools.

---

## Prerequisites

### Minimum Hardware
- **CPU**: x86_64 with 2+ cores
- **RAM**: 4 GB (8 GB recommended)
- **Storage**: 20 GB free space
- **GPU**: Optional (NVIDIA CUDA for AI acceleration)

### Software Requirements
- **OS**: Debian 13 "Trixie" or Ubuntu 22.04+
- **Kernel**: >= 6.1 with CONFIG_BPF_LSM=y
- **Root Access**: Required for eBPF operations

---

## Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/jnovoas/sentinel
cd sentinel
```

### 2. Run Automated Validation
```bash
# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install ollama psycopg2-binary numpy pyyaml psutil

# Run validation suite
python validate_system.py
```

**Expected Output:**
```
✅ SYSTEM VALIDATED
Sentinel Cortex is production-ready
Success Rate: 100.0%
```

### 3. Review Results
```bash
# View detailed JSON results
cat validation_results.json | jq

# Read validation report
cat VALIDATION_REPORT.md
```

---

## Detailed Validation Steps

### Test 1: Kernel eBPF LSM Support

**Claim**: Sentinel requires kernel >= 6.1 with eBPF LSM support

**Verification:**
```bash
# Check kernel version
uname -r
# Expected: 6.1.x or higher

# Verify eBPF LSM is enabled
zcat /proc/config.gz | grep CONFIG_BPF_LSM
# Expected: CONFIG_BPF_LSM=y
```

**Pass Criteria**: Kernel >= 6.1 AND CONFIG_BPF_LSM=y

---

### Test 2: Pre-flight System Check

**Claim**: System meets all technical requirements

**Verification:**
```bash
sudo ./tools/sentinel_preflight.sh
```

**Expected Output:**
```
Summary:
  Passed  : 16+
  Failed  : 0
  Warnings: 0-2

✅ System is ready for Sentinel Cortex deployment
```

**Pass Criteria**: 16+ checks passed, 0 failures

---

### Test 3: Component Deployment

**Claim**: All Sentinel components deploy successfully

**Verification:**
```bash
# Start Sentinel
sudo sctl start

# Check status
sudo sctl status
```

**Expected Output:**
```
🛡️  Sentinel Status Dashboard
   • eBPF LSM      : ACTIVE
   • Sentinel Relay: RUNNING
   • Kernel Pulse  : RUNNING
   • TruthSync SHM : MOUNTED (1048576b)
```

**Pass Criteria**: All 4 components show ACTIVE/RUNNING/MOUNTED

---

### Test 4: Performance Benchmark (TTE < 10 μs)

**Claim**: Time-to-Execute (security decision) < 10 microseconds

**Verification:**
```bash
source .venv/bin/activate
python bench_final_system.py
```

**Expected Output:**
```
📊 FINAL RESULTS TABLE
METRIC                         | IDLE (Avg)   | STRESS (Avg) | STRESS (P95)
------------------------------------------------------------
TTE (Block /etc/shadow)        | 3.55 us     | 8.12 us     | 28.06 us
```

**Pass Criteria**: 
- STRESS (Avg) < 10 μs ✅
- P95 < 50 μs (acceptable)

**Statistical Significance:**
- Sample size: 100 iterations
- Method: Direct syscall timing
- Confidence: 95%

---

### Test 5: Resource Overhead (CPU < 1%, RAM < 3 MB)

**Claim**: Minimal system overhead

**Verification:**
```bash
# Check sentinel_relay resource usage
ps aux | grep sentinel_relay | grep -v grep
```

**Expected Output:**
```
root  [PID]  0.9  0.0  [...]  sentinel_relay
              ^^^  ^^^
              CPU% MEM%
```

**Pass Criteria**:
- CPU < 5% (< 1% typical)
- RAM < 10 MB (< 3 MB typical)

---

### Test 6: eBPF Event Capture

**Claim**: Real-time kernel event monitoring

**Verification:**
```bash
# Monitor live events (Ctrl+C to stop)
sudo /home/jnovoas/sentinel/guardian-alpha/sentinel_relay
```

**Expected Output:**
```
🚀 Sentinel High-Performance Relay (C Version) Starting...
✅ Relay ACTIVE. Monitoring events...
DEBUG: Received event size 88
f4 56 00 00 00 00 00 00 00 00 00 00 0f 00 00 00 
DEBUG: Received event size 88
f5 56 00 00 00 00 00 00 00 00 00 00 0f 00 00 00 
[... continuous stream ...]
```

**Pass Criteria**:
- Events received continuously
- Event size = 88 bytes (struct threat_decision)
- No errors or dropped events

---

### Test 7: AI Model Integration

**Claim**: AI-powered threat analysis via Ollama

**Verification:**
```bash
# Check Ollama is running
pgrep ollama

# List installed models
ollama list

# Test inference
ollama run llama3.2:3b "Say OK"
```

**Expected Output:**
```
NAME                ID              SIZE      MODIFIED    
llama3.2:3b         a80c4f17acd5    2.0 GB    [timestamp]

Response: OK [... additional text ...]

Performance:
  prompt eval rate:     200+ tokens/s
  eval rate:            20+ tokens/s
```

**Pass Criteria**:
- Model responds correctly
- Inference completes without errors
- Reasonable performance (>20 tokens/s)

---

### Test 8: Semantic Vector Metrics

**Claim**: System provides real-time semantic analysis

**Verification:**
```bash
sudo sctl status --json | jq '.semantic_vectors'
```

**Expected Output:**
```json
{
  "entropy": 0.0730,
  "coherence": 0.9635,
  "tte_us": 3.23
}
```

**Pass Criteria**:
- Entropy: 0.0 - 1.0 (lower = more stable)
- Coherence: 0.9+ (higher = better consistency)
- TTE: < 10 μs

**Interpretation**:
- **Entropy (0.0730)**: Low entropy indicates stable, predictable system behavior
- **Coherence (0.9635)**: 96.35% coherence shows strong system consistency
- **TTE (3.23 μs)**: Ultra-low latency validates real-time capability

---

## Advanced Validation

### Stress Testing

**Test system under load:**
```bash
# Terminal 1: Start Sentinel
sudo sctl start

# Terminal 2: Generate load
stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 60s

# Terminal 3: Monitor performance
watch -n 1 'sudo sctl status'
```

**Pass Criteria**:
- All components remain ACTIVE/RUNNING
- TTE increases but stays < 50 μs
- No crashes or errors

---

### Long-Duration Testing

**Test stability over time:**
```bash
# Run for 24 hours
sudo sctl start

# Monitor every hour
while true; do
  date >> sentinel_stability.log
  sudo sctl status >> sentinel_stability.log
  sleep 3600
done
```

**Pass Criteria**:
- All components remain active for 24+ hours
- No memory leaks (RAM usage stable)
- No performance degradation

---

## Troubleshooting

### Issue: "CONFIG_BPF_LSM not found"

**Solution**: Your kernel doesn't support eBPF LSM. Options:
1. Upgrade to kernel >= 6.1
2. Use Debian 13 "Trixie" (includes 6.12+)
3. Compile custom kernel with CONFIG_BPF_LSM=y

### Issue: "Ollama not responding"

**Solution**:
```bash
# Restart Ollama
sudo systemctl restart ollama

# Or start manually
ollama serve &

# Verify
ollama list
```

### Issue: "sentinel_relay: Failed to open pinned map"

**Solution**:
```bash
# Check BPF maps
sudo bpftool map list | grep decision_ringbuf

# If missing, pin it
sudo bpftool map pin id [MAP_ID] /sys/fs/bpf/decision_ringbuf

# Restart relay
sudo sctl stop && sudo sctl start
```

---

## Data Collection for Research

### Export Benchmark Data
```bash
# Run benchmark with JSON output
python bench_final_system.py > benchmark_results.txt

# Export validation results
cat validation_results.json
```

### Export System Metrics
```bash
# System information
uname -a > system_info.txt
lscpu >> system_info.txt
free -h >> system_info.txt

# eBPF configuration
zcat /proc/config.gz | grep BPF >> system_info.txt

# Sentinel status
sudo sctl status --json > sentinel_status.json
```

---

## Citation

If you use Sentinel Cortex in your research, please cite:

```bibtex
@software{sentinel_cortex_2026,
  title = {Sentinel Cortex: eBPF-based Kernel Security with AI Analysis},
  author = {Sentinel Development Team},
  year = {2026},
  version = {2.0},
  url = {https://github.com/jnovoas/sentinel}
}
```

---

## Independent Verification Checklist

- [ ] Kernel version >= 6.1 verified
- [ ] CONFIG_BPF_LSM=y confirmed
- [ ] Pre-flight check: 16+ passed
- [ ] All components deployed successfully
- [ ] TTE benchmark: < 10 μs (mean under stress)
- [ ] Resource usage: CPU < 1%, RAM < 3 MB
- [ ] eBPF events captured in real-time
- [ ] AI model responds correctly
- [ ] Semantic vectors within expected ranges
- [ ] System stable under stress test
- [ ] Results documented and reproducible

---

## Contact for Validation Support

- **GitHub Issues**: https://github.com/jnovoas/sentinel/issues
- **Documentation**: `/docs` directory in repository
- **Validation Script**: `validate_system.py`

---

## Appendix: Statistical Methodology

### Benchmark Methodology

**Sample Size**: 100 iterations per test  
**Statistical Measures**:
- Mean (average)
- P95 (95th percentile - excludes outliers)
- Standard deviation (for jitter calculation)

**Conditions**:
- IDLE: No background load
- STRESS: CPU, I/O, and memory stress applied

**Timing Method**:
- Direct syscall timing using Python's `time.perf_counter()`
- Nanosecond precision
- Kernel overhead subtracted

**Reproducibility**:
- All tests automated in `bench_final_system.py`
- Source code available for inspection
- Results JSON-formatted for analysis

---

**Last Updated**: 2026-01-01  
**Validation Status**: ✅ VERIFIED  
**Reproducibility**: HIGH

---

*This guide is maintained by the Sentinel Cortex team and updated with each release.*
