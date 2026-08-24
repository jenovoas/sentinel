# Quick Reference - Sentinel Mejoras P0/P1/P2

## Comandos Rápidos

```bash
# P0: Zero-init check
bpftool prog dump xlated name ai_guardian | grep -A2 memset
bpftool prog dump xlated name guardian_alpha_lsm | grep -A2 memset

# P1: Kani
cd sentinel-cortex && cargo kani --harness verify_parse_event_no_panic

# P2: Decision tree compile check
clang -target bpf -O2 -c ebpf/ai_guardian.c -I ebpf/ 2>&1 | grep -E "(error|warning)"

# P2: FFT detector test
cd sentinel-cortex && cargo test periodic_detector -- --nocapture
```

## Archivos a Tocar

| Mejora | Archivos |
|--------|----------|
| P0 Zero-init | `ebpf/ai_guardian.c:91`, `ebpf/guardian_alpha_lsm.c:66` |
| P1 Kani | `sentinel-cortex/kani/harness_parse_event.rs` (nuevo) |
| P2 Decision Tree | `ebpf/decision_tree.h` (nuevo), `ebpf/ai_guardian.c` |
| P2 FFT Detector | `sentinel-cortex/src/detectors/periodic.rs` (nuevo), `ebpf_cortex_bridge.rs` |

## Métricas Clave

| KPI | Actual | Target |
|-----|--------|--------|
| Leaks KASLR posibles | 2/3 progs | 0/3 |
| Verificación formal bridge | 0% | 100% (Kani) |
| Clasificación en kernel | 0% | 100% (decision tree) |
| Detección beaconing | 0% | >90% recall |

## Papers de Referencia

- **Heimdall** (2605.25411): Verificación formal + leaks uninit
- **TU Wien IDS** (2102.09980): Decision trees en eBPF
- **IoT DDoS** (2508.00851): XDP + panic mode
- **Time-Crystal** (2509.21959, 2606.30890): Resonancia periódica = Q-factor

---

*Ver `MEJORAS_PLANIFICADAS.md` para detalle completo.*