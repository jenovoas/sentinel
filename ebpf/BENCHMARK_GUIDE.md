# Guardian-Alpha LSM - Benchmark Guide

## Overview

Two benchmarks available to measure Guardian-Alpha LSM performance overhead:

1. **Bash Simple** - Quick overhead measurement
2. **Python Advanced** - Full statistical analysis

---

## Benchmarks

### 1. Bash Simple (`benchmark_lsm_overhead.sh`)

**What it does**:
- Runs 1,000 executions of `/bin/true`
- Measures total and average execution time
- Estimates overhead vs typical baseline
- Shows recent kernel events

**Usage**:
```bash
cd /home/jnovoas/sentinel/ebpf
./benchmark_lsm_overhead.sh
```

**Output**:
- Total time (ms)
- Average per execution (μs)
- Estimated overhead (μs and %)
- Performance rating (Excellent/Good/Moderate/High)

---

### 2. Python Advanced (`benchmark_lsm_advanced.py`)

**What it does**:
- Runs 1,000 executions with precise timing
- Full statistical analysis
- Percentile calculations (P50, P95, P99)
- Saves results to JSON

**Usage**:
```bash
cd /home/jnovoas/sentinel/ebpf
python3 benchmark_lsm_advanced.py
```

**Output**:
- Mean, Median, Std Dev
- Min, Max
- P50, P95, P99 percentiles
- Estimated overhead
- Results saved to `benchmark_results.json`

---

## How to Run

### Option 1: With LSM Already Loaded

```bash
cd /home/jnovoas/sentinel/ebpf

# Run benchmark
python3 benchmark_lsm_advanced.py

# View results
cat benchmark_results.json
```

### Option 2: Load, Benchmark, Unload

```bash
cd /home/jnovoas/sentinel/ebpf

# Load LSM
sudo ./load.sh

# Run benchmark
python3 benchmark_lsm_advanced.py

# Unload LSM
sudo ./unload.sh
```

### Option 3: Before/After Comparison

```bash
# 1. Baseline (no LSM)
python3 benchmark_lsm_advanced.py
mv benchmark_results.json baseline_results.json

# 2. With LSM
sudo ./load.sh
python3 benchmark_lsm_advanced.py
mv benchmark_results.json with_lsm_results.json

# 3. Compare
python3 -c "
import json
baseline = json.load(open('baseline_results.json'))
with_lsm = json.load(open('with_lsm_results.json'))
print(f'Baseline: {baseline[\"statistics\"][\"mean_us\"]:.2f} μs')
print(f'With LSM: {with_lsm[\"statistics\"][\"mean_us\"]:.2f} μs')
overhead = with_lsm['statistics']['mean_us'] - baseline['statistics']['mean_us']
print(f'Overhead: {overhead:.2f} μs')
"
```

---

## What Gets Measured

### Metrics

- **Mean**: Average execution time
- **Median**: Middle value (less affected by outliers)
- **Std Dev**: Consistency of measurements
- **Min/Max**: Range of execution times
- **P95**: 95% of executions are faster than this
- **P99**: 99% of executions are faster than this

### Overhead Calculation

```
Overhead = Measured Time - Typical Baseline
Typical Baseline ≈ 75 μs (for /bin/true without LSM)
```

### Performance Targets

- ✅ **Excellent**: < 10 μs overhead
- ✅ **Good**: < 100 μs overhead  
- ⚠️ **Moderate**: < 1 ms overhead
- ⚠️ **High**: > 1 ms overhead

---

## Expected Results

Based on eBPF LSM design:

- **Overhead**: < 1 μs (hash map lookup)
- **Consistency**: Low std dev (< 10 μs)
- **P99**: < 200 μs total time

eBPF programs are JIT-compiled to native code and run in kernel context, so overhead should be minimal.

---

## Interpreting Results

### Good Results
```
Mean:       80 μs
Median:     78 μs
Std Dev:    5 μs
P95:        90 μs
P99:        95 μs

Overhead:   5 μs (6.7%)
✅ Excellent: < 10μs overhead
```

### Concerning Results
```
Mean:       500 μs
Median:     450 μs
Std Dev:    100 μs
P95:        700 μs
P99:        900 μs

Overhead:   425 μs (567%)
⚠️  High: > 1ms overhead
```

If you see high overhead, check:
- Kernel logs for errors
- BPF map sizes
- System load

---

## Files Created

```
ebpf/
├── benchmark_lsm_overhead.sh      # Bash benchmark
├── benchmark_lsm_advanced.py      # Python benchmark
└── benchmark_results.json         # Results (created after run)
```

---

## Next Steps

After benchmarking:
1. Document results in `EVIDENCE_LSM_DEPLOYMENT.md`
2. Compare with user-space alternatives (50-150ms)
3. Include in patent evidence (< 1ms overhead claim)

---

**Ready to measure Guardian-Alpha performance!** 📊
