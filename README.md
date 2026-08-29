# 🛡️ Sentinel — Sexagesimal Systems Framework & Cognitive Security Kernel

**Framework de sistemas de bajo nivel y kernel de seguridad determinista que implementa aritmética base-60 exacta ($S_{60}$) en Ring 0 eBPF y espacio de usuario, eliminando los errores de redondeo IEEE 754 de la cadena de cálculo crítico.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Rust 2021+](https://img.shields.io/badge/rust-2021%2B-black.svg?logo=rust)](./sentinel-cortex/)
[![eBPF LSM](https://img.shields.io/badge/eBPF-Ring%200%20LSM-orange)](./ebpf/)
[![Core S60](https://img.shields.io/badge/Core-S60%20Fixed%20Point-purple)](./me-60os-core/)
[![WireGuard Mesh](https://img.shields.io/badge/Network-WireGuard%2010.88.0.0%2F24-emerald)](./)

---

## 🏛️ Topología de Ejecución (Fenix + Kingu)

> **Nota de red física:** Fenix y Kingu operan en cuentas de Azure separadas (sin VPC compartida). Toda la interconexión, sincronización del cristal fonónico y telemetría transita exclusivamente por el túnel cifrado **WireGuard (`10.88.0.0/24`)**. Fan está completamente decomisionado.

```
                  ┌────────────────────────────────────────┐
                  │            INTERNET PÚBLICA            │
                  └───────────┬────────────────┬───────────┘
                              │                │
                      (:53 DNS1 UDP/TCP)   (:80 / :443 HTTPS)
                      (:51820 WG UDP)      (:4222 SSH / :53 DNS2)
                              ▼                ▼
     ┌──────────────────────────────────┐    ┌──────────────────────────────────┐
     │      FENIX (Cuenta Azure A)      │    │      KINGU (Cuenta Azure B)      │
     │      IP Pública: 20.226.112.222  │    │      IP Pública: 68.211.176.190  │
     │      Túnel VPN: 10.88.0.1/24     │    │      Túnel VPN: 10.88.0.2/24     │
     │      Rol: Dev + Sentinel Core    │    │      Rol: Prod + Sentinel Nodes  │
     ├──────────────────────────────────┤    ├──────────────────────────────────┤
     │ • Sentinel Cortex API (:8000)    │    │ • Traefik v3 Reverse Proxy       │
     │ • Retículo SHM (67.951 Nodos)    │    │ • PowerDNS secundario (dns2)     │
     │ • eBPF LSM (guardian_alpha_lsm)  │    │ • Sentinel Verifier (Invariantes)│
     │ • float_detector (Anti-Drift)    │    │ • MycNet Daemon Mesh (:7474)     │
     │ • BIND9 primario (dns1)          │    │ • Podman rootless (Contenedores) │
     │ • Sentinel Verifier (Systemd)    │    │ • Backup diario cron → Fenix     │
     └─────────────────┬────────────────┘    └────────────────┬─────────────────┘
                       │                                      │
                       └───────────► Túnel Cifrado ◄──────────┘
                                  WireGuard (wg0)
                                   10.88.0.0/24
```

---

## 🧱 Arquitectura de 6 Capas y Orden de Arranque

```
1. eBPF Ring-0 (LSM / XDP / TC Hooks)
      │ (Crea maps y hooks de seguridad en /sys/fs/bpf)
      ▼
2. sentinel-cortex (Rust :8000)
      │ (Inicializa /dev/shm/me60os_lattice con 67.951 nodos y arranca el bombeo PAI)
      ▼
3. mycnetd (Rust :7474)
      │ (Lee /me60os_lattice en Zero-Copy y proyecta a la malla mesh UDP)
      ▼
4. Daemons me-60os (qhc_agent, pai_neural_daemon, adm_agent, vid_agent, hex_daemon)
      │ (Modulación armónica, marcapasos 17s/68s e inyección neural)
      ▼
5. Observabilidad & Invariantes (sentinel-verifier, Prometheus, Loki, Grafana)
      ▼
6. Aplicaciones & Servicios Soberanos (pinguinoseguro-web, portal, bases de datos)
```

---

## 💎 Retículo del Cristal Fonónico y Osciladores Isocrónicos

* **Dimensionamiento Dinámico:** $N = 3r^2 + 3r + 1$ ($r=150 \implies \mathbf{67.951\,\text{nodos}}$ para servidores de 16 GB RAM).
* **Estructura por Oscilador (`IsochronousOscillator`):** `192 bytes` exactos con layout `#[repr(C)]`.
  * `name[32]` + `natural_frequency[40]` + `amplitude[40]` + `phase[40]` + `damping_factor[40]`.
* **Frecuencia Armónica:** $SPA(1, 32, 2, 24, 0)$ (Plimpton 322 Fila 12).
* **Memoria Compartida Zero-Copy:** `/dev/shm/me60os_lattice` en memoria RAM del kernel, sin overhead de serialización ni copia de datos.

---

## 📦 Workspace Cargo (5 Crates Principales)

```
sentinel/
├── sentinel-cortex/       Servidor Axum (:8000), drive continuo, ingesta eBPF,
│                          holograma fonónico (/api/v1/lattice/hologram), métricas Prometheus
├── me-60os-core/          Núcleo numérico S60, PAI-60, ResonantMatrix, IsochronousOscillator,
│                          QHC, daemons nativos (qhc_agent, pai_neural_daemon, adm_agent, vid_agent)
├── truthsync-core/        Motor de verificación de afirmaciones y mitigación de drift
├── sentinel-verifier/     Verificador continuo de invariantes runtime (--watch 15 --json)
├── services/neural-guard/ Correlación de eventos eBPF + orquestación de respuesta
└── ebpf/                  Módulos kernel: guardian_alpha_lsm.c, float_detector.c,
                           guardian_cognitive.c, tc_firewall.c, burst_sensor.c
```

---

## 🔢 Reglas de Oro de la Aritmética Core S60

1. **Escala Base:** `SCALE_0 = 60⁴ = 12,960,000`.
2. **Prohibición de Floats:** Ni `f32` ni `f64` en lógica de cálculo de estado o facturación; vigilado en compilación por Clippy (`forbid(float_arithmetic)`) y en runtime por `float_detector` eBPF.
3. **No Doble-Escalar:** Distinguir entre `SPA::from_int(n)` y `SPA::from_raw(n)`. Para valores raw usar `inject_spa(x, SPA::from_raw(v))`.
4. **Drive Continuo:** El retículo es intrínsecamente disipativo; `sentinel-cortex` inyecta pulsos armónicos cada 500ms para sostener la resonancia.

---

## ⚡ Comandos Rápidos

```bash
# Compilar todo el workspace en modo release
cargo build --release

# Ejecutar suite de pruebas unitarias numéricas
cargo test -p me60os --lib

# Iniciar Sentinel Cortex
cargo run --release -p sentinel-cortex

# Iniciar Verificador de Invariantes
cargo run --release -p sentinel-verifier -- --watch 15 --json

# Cargar módulos de seguridad eBPF en el kernel (Root)
cd ebpf && sudo bash load.sh
```

---

## 📄 Licencia

Apache 2.0 — Ver [LICENSE](./LICENSE).
Desarrollado por **Jaime Novoa Sepúlveda** para **Sentinel / SecurePenguin**.
