# 🔧 REFERENCIA: Despliegue Sentinel + bpftool (receta verificada 2026-08-06)

> Sesión con Jaime: levantar los 6 daemons + LSM manual, verificar que el cortex se
> puebla con "nervios de verdad" (PAI, fase, fonones). Todos los comandos probados.

## 0. Precondiciones
- Kernel: Fedora 44, `uid=1002`. `cargo 1.97.1`. `bpftool v7.6.0`.
- `export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` (py3.14 > pyo3 0.13 cap) antes de cualquier cargo.
- LSM cargado manual por Jaime (hooks en `/sys/fs/bpf/sentinel/`). Verificar:
  `sudo bpftool prog show | grep guardian_execve` → debe aparecer 1 solo (link vivo).

## 1. Compilar los bins (workspace root)
```bash
cd ~/Proyectos/sentinel
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cargo build -p me60os --bin qhc_agent --bin pai_neural_daemon --bin vid_agent --bin hex_daemon
cargo build -p sentinel-cortex
```

## 2. Levantar cortex CON PAI (background, NO usar &/nohup — Hermes los rechaza)
```bash
# usar background=true del tool terminal, o:
SENTINEL_PAI_CONVERT=1 SENTINEL_PORT=8014 \
  EBPF_MONITOR_PATH=/sys/fs/bpf/sentinel/events \
  ./target/debug/sentinel-cortex
```

## 3. Levantar los otros daemons (cada uno en su propio background)
```bash
./target/debug/qhc_agent          # pulso 10;5,6,5 YHWH (independiente)
./target/debug/vid_agent          # optomechanical cooling
./target/debug/hex_daemon         # control hexagonal 91 nodos
sudo ./target/debug/pai_neural_daemon   # NECESITA sudo: pin events es 0600 root
```
> El `pai_neural_daemon` LEE el mismo ringbuf `/sys/fs/bpf/sentinel/events` que el cortex
> (consumidor paralelo). Sin sudo → `Permission denied (os error 13)`.

## 4. Poblar alpha_ai_agents (para que el guardian emita eventos de un PID)
```bash
# PID en little-endian __u32 -> bytes hex separados por espacio
KEY_HEX=$(python3 -c "import struct; print(' '.join(f'{b:02x}' for b in struct.pack('<I', <PID>)))")
sudo bpftool map update pinned /sys/fs/bpf/sentinel/alpha_ai_agents key hex $KEY_HEX value hex 01
# verificar:
sudo bpftool map dump pinned /sys/fs/bpf/sentinel/alpha_ai_agents
```
> Sintaxis clave: `key hex <bytes espaciados> value hex 01`. NO `key 0x...` ni `key <bytes>` sin `hex`.

## 5. Verificar que el sistema está vivo
```bash
curl -s http://127.0.0.1:8014/health          # {"status":"OK",...}
curl -s http://127.0.0.1:8014/api/v1/lattice  # total_energy sube conforme los daemons inyectan
```
> Si `total_energy` crece (ej. 873M → 25B) los daemons están poblando la lattice.

## 6. Benchmark con/sin Sentinel (workload sentinel_bench)
```bash
./target/debug/sentinel_bench   # crystal tick ~41Hz, drift ppm, lattice I/O ns/op, CPU%
```
> Resultado medido 2026-08-06: I/O lattice IDÉNTICO (~240 ns/op) con/sin framework;
> CPU +4-6% con Sentinel vivo. Ver `sentinel-s60-plan/docs/BENCHMARK_QA_BASELINE_2026-08-06.md`.

## 7. Pitfalls
- No usar `&` / `nohup` / `setsid` en el tool terminal de Hermes → rechaza. Usar `background=true`.
- `-EBUSY` al atachar LSM = hook ya vivo, no reintentar. Vacío tras reboot = hooks soltados.
- Docs viejos (`architecture_technical.md`) dicen `/sys/fs/bpf/ai_guardian/cortex_events` →
  wrong; realidad es `/sys/fs/bpf/sentinel/events`. Actualizar esos docs.
- `pai_neural_daemon.rs` fallback de path corregido para probar `/sys/fs/bpf/sentinel/events` primero.
