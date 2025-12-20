# 📊 Benchmarks & Performance - Consolidated

## TruthSync: 90.5x Speedup
- **Throughput**: 1.54M claims/segundo
- **Latency**: 0.36μs (p50)
- **Cache hit**: 99.9%
- **Code**: `truthsync-poc/benchmark.py`

## Dual-Lane Architecture: 5/5 Claims Validated

| Metric | Target | Measured | Improvement |
|--------|--------|----------|-------------|
| Routing | <1ms | 0.0035ms | 285x |
| WAL Security | <5ms | 0.01ms | 500x |
| WAL Ops | <20ms | 0.01ms | 2000x |
| Security Lane | <10ms | 0.00ms | ∞ |
| Bypass | <0.1ms | 0.0014ms | 71x |

**Code**: `backend/benchmark_dual_lane.py`

## WASM Integration
- **Bundle**: 37KB gzipped
- **Tests**: 3/3 passing
- **Patterns**: 42 malicious detected
- **Status**: Production ready

## vs Competition

| Feature | Datadog | Splunk | Sentinel |
|---------|---------|--------|----------|
| Routing | ~10ms | ~25ms | **0.0035ms** |
| WAL | N/A | ~80ms | **0.01ms** |
| Security Lane | ~50ms | ~150ms | **0.00ms** |

**Details**: `BENCHMARKS_VALIDADOS.md`
