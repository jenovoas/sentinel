# Fan Daemon Reactivation (2026-08-18)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


## Objetivo

Reactivar los daemons `sentinel-*.service` en la Fan (10.88.0.1 → 157.254.174.40:4222)
y verificar su arranque según la línea de trabajo Item 3 del plan de remediación.

## Estado MEDIDO antes de la acción

| Comprobación | Resultado |
| --- | --- |
| Fan ICMP desde fedora (10.88.0.1) | ✅ responde (213 ms avg) |
| SSH `fan:4222` desde fedora | ✅ autentica con `~/.ssh/id_ed25519_server` |
| sudo NOPASSWD en Fan | ✅ root |
| `systemd` en Fan | ✅ systemd 257 (Rocky Linux 10.2) |
| Binarios en Fan `~/.local/bin/` | ✅ los 9 esperados ya presentes (ver tabla) |
| Unit files en Fan `/etc/systemd/system/` | ✅ los 9 `.service` registrados |
| Estado previo de los 9 | todos `disabled`, ninguno `active` |

### Bloqueador previo en fedora

ssh desde fedora fallaba con:

```
Bad owner or permissions on /etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf
```

El filesystem del host fedora tiene `/etc/ssh/ssh_config.d/` en read-only. La salida
era una caída temprana antes de la auth. Se resolvió pasando `-F tools/ssh-fan.conf`
(workspace path escribible) que apunta explícitamente a `id_ed25519_server`,
única clave con autorización en Fan.

```bash
ssh -F tools/ssh-fan.conf fan 'whoami'  # → jnovoas
```

Fichero: `tools/ssh-fan.conf`. `tools/.fan-known-hosts` se generó solo.

## Acción ejecutada (Round 2/40)

```bash
sudo systemctl daemon-reload
for s in sentinel-cortex sentinel-verifier sentinel-qhc-agent \
         sentinel-vid-agent sentinel-adm-agent sentinel-pai-neural \
         sentinel-hex-daemon sentinel-gamma-watchdog sentinel-ebpf-forwarder; do
    sudo systemctl enable "$s.service"
    sudo systemctl start "$s.service"
done
```

## Estado MEDIDO después de la acción

| Servicio | Binario | enabled | active |
| --- | --- | --- | --- |
| sentinel-cortex.service | `~/.local/bin/sentinel-cortex` | ✅ | ⚠️ activating (restart-loop) |
| sentinel-verifier.service | `~/.local/bin/sentinel-verifier --watch 60` | ✅ | ⚠️ activating (depends on cortex) |
| sentinel-qhc-agent.service | `~/.local/bin/qhc_agent` | ✅ | ✅ active (PID 2164493) |
| sentinel-vid-agent.service | `~/.local/bin/vid_agent` | ✅ | ✅ active (PID 2164497) |
| sentinel-adm-agent.service | `~/.local/bin/sentinel-adm-agent` | ✅ | ⚠️ activating |
| sentinel-pai-neural.service | `~/.local/bin/pai_neural_daemon` | ✅ | ⚠️ activating |
| sentinel-hex-daemon.service | `~/.local/bin/hex_daemon` | ✅ | ⚠️ activating |
| sentinel-gamma-watchdog.service | `ebpf/gamma_watchdog` | ✅ | ⚠️ activating |
| sentinel-ebpf-forwarder.service | `/usr/sbin/bpftool prog tracelog` | ✅ | ✅ active (PID 2164524) |

3/9 arrancados limpios; 6/9 en restart-loop con `RestartSec=3-10s`.

## Diagnóstico de los 6 fallos

### `sentinel-cortex` — `AddrInUse` + Redis PubSub denied

```
thread 'main' panicked at sentinel-cortex/src/main.rs:390:62
called `Result::unwrap()` on an Err value: AddrInUse (os error 98)
ERROR sentinel_cortex: Failed to open Redis PubSub: Permission denied (os error 13)
```

- Puerto objetivo `127.0.0.1:8891` ya está en uso por un binario anónimo
  (`ss -tlnp` LISTEN en 127.0.0.1:8891 sin process associado al namespace actual).
- `redis://localhost:6379` no responde con permisos de root.
- `systemctl status redis` → unit no existe en Fan.

### `sentinel-pai-neural` — `/sys/fs/bpf/cortex_events` ausente

```
Error: Failed to open pinned map at /sys/fs/bpf/cortex_events:
       No such file or directory (os error 2)
```

- `bpffs` está montado en `/sys/fs/bpf` (`mount | grep bpf`).
- La ruta específica `cortex_events` no existe — es un pin del loader eBPF que
  solo se crea al cargar el BPF object. Ningún servicio `cortex_events_loader`
  está instalado en Fan.

### `sentinel-hex-daemon` — `status=203/EXEC`

- `file hex_daemon` → ELF 64-bit LSB pie executable, x86-64.
- `ldd hex_daemon` resuelve bien (`libelf.so.1`, `libc.so.6`, etc.).
- Con permisos `0755 jnovoas:jnovoas`, la salida `203/EXEC` típicamente indica
  arquitectura incompatible o glibc ≥ requerida por el binario no presente.
  Fan corre Rocky 10.2 glibc 2.x; sospecho binario compilado para otra distro.
  Necesita re-compilación desde el repo actual.

### `sentinel-adm-agent`, `sentinel-gamma-watchdog`

- Probablemente mismo bloqueo que `pai-neural`: necesitan `cortex_events` en
  bpffs. Sin diagnosticar uno por uno aún.

### `sentinel-verifier`

- `After=network.target sentinel-cortex.service` — depende de `cortex` activo.
- Mientras cortex esté en restart-loop, verifier queda `activating` solo en su
  fase pre-cortex. Cuando cortex reviva, verifier debe arrancar. No es un bug
  separado.

## Lo que NO se puede hacer sin Fan operativa

Cumpliendo la regla del plan ("Prohibido tocar SSH/firewall sin verificación
desde afuera"), **NO se ha hecho**:

1. **No se ha matado el proceso que ocupa 127.0.0.1:8891.** Podría ser un
   cortex manual con datos en vuelo (memoria compartida `/dev/shm/sentinel_*`).
   Cualquier kill puede dejar estado inconsistente.
2. **No se ha instalado Redis en Fan.** Los servicios root dependen de él.
3. **No se ha cargado el BPF object `cortex_events` desde ebpf/.** Cambia
   el entorno del kernel; requiere sincronizar con la regla YATRA de no
   contaminar floats.
4. **No se ha re-compilado `hex_daemon` desde el repo actual** (puede que
   el binario del 2026-07-29 requiera glibc más nuevo que la Fan tiene, o
   viceversa).
5. **No se ha tocado el firewall ni la wireguard.** Aunque ya está el túnel
   `20129→20128` corriendo, eso es pre-existente al plan.

## Próximos pasos propuestos (a coordinar contigo antes de ejecutar)

Orden de prioridad, cada uno es una acción destructiva que requiere tu OK:

### 1. Apaciguar los restart-loop (bajo riesgo)

```bash
# Ver de matar lo que ocupa :8891 sin perder datos
lsof -i :8891 || sudo ss -tlnp sport = :8891
sudo systemctl stop sentinel-cortex sentinel-verifier
sudo systemctl reset-failed sentinel-cortex sentinel-verifier
```

### 2. Cargar `cortex_events` desde ebpf/

```bash
cd /home/jnovoas/Proyectos/sentinel/ebpf
sudo bash load_ebpf_array_fan.py  # si existe
# o bien:
sudo /usr/local/bin/loader-ebpf-cortex
```

### 3. Re-compilar `hex_daemon`

```bash
cd /home/jnovoas/Proyectos/sentinel/me-60os-core
cargo build --release --bin hex_daemon
rsync target/release/hex_daemon fan:.local/bin/
sudo systemctl restart sentinel-hex-daemon
```

### 4. Instalar Redis + habilitar socket

```bash
# Requiere tu confirmación para instalar
sudo dnf install -y redis
sudo systemctl enable --now redis
sudo usermod -aG redis jnovoas
```

### 5. Verificación final

```bash
for s in sentinel-cortex sentinel-verifier sentinel-qhc-agent \
         sentinel-vid-agent sentinel-adm-agent sentinel-pai-neural \
         sentinel-hex-daemon sentinel-gamma-watchdog sentinel-ebpf-forwarder; do
    printf "%-40s %s\n" "$s" "$(ssh fan systemctl is-active $s.service)"
done
# esperado: 9/9 active
```

## Criterios de cierre Item 3

- [x] 9 unit files localizados en Fan
- [x] 9 binarios verificados en `~/.local/bin/`
- [x] SSH resuelto (config alternativa en `tools/ssh-fan.conf`)
- [x] `enable` aplicado a los 9
- [x] `start` ejecutado en los 9
- [ ] 9/9 `active` (3/9 hoy)
- [ ] Sin procesos zombies / restart-loops
- [ ] health-checks externos pasan (`curl localhost:8891`, `redis-cli ping`)

## Referencias

- `tools/ssh-fan.conf` — config SSH operativa desde fedora hacia Fan
- `tools/.fan-known-hosts` — host key persistido (ED25519 157.254.174.40:4222)
- Unit files: `/etc/systemd/system/sentinel-*.service` (Fan)
- Logs relevantes: `journalctl -u sentinel-*` en Fan