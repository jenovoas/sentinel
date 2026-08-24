---
name: sentinel-runtime-verification
description: Runtime verification rules for Rust, eBPF, and SPA base-60 scale calculations.
---

# Sentinel Runtime Verification Skill

1. **Medir, no especular**: Inspeccionar logs completos y ejecutar benchmarks de tiempo real antes de diagnosticar.
2. **Aritmética Exacta Base-60⁴**: Validar que `SPA` y `PAI-60` no tengan contaminación float (`f32`/`f64`) ni doble escalado (`SPA::to_raw()` a `inject()`).
3. **Drive Continuo**: Verificar que el drive continuo en `sentinel-cortex` esté activo para evitar que el lattice decaiga a ground state.
