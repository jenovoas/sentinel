# Sentinel — Marco de Sistemas Sexagesimales

**Marco de sistemas de bajo nivel que implementa aritmética base‑60 a nivel de kernel, eliminando los errores de redondeo de IEEE 754 desde la base matemática.**

[![Licencia: Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](./LICENSE)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?logo=rust)](./services/neural-guard/)
[![eBPF](https://img.shields.io/badge/eBPF-nivel--kernel-orange)](./ebpf/)
[![Estado Fenix](https://img.shields.io/badge/Nodo_Fenix-ACTIVO-brightgreen?style=for-the-badge&logo=linux)](https://pinguinoseguro.cl)

> [!NOTE]
> **Nodo Fenix Operativo**: Sentinel ha transitado a una arquitectura de **Nodo Único (Fenix)** bajo Podman Rootless, consolidando la orquestación Ring 0 y el monitoreo resiliente.

---

---

## Fases del Proyecto

Este repositorio contiene la infraestructura y el código para el proyecto Sentinel en sus diferentes etapas. Es crucial entender cada contexto:

1. **Entorno de Desarrollo Local (PoC Inicial):**
   * **Ubicación:** Principalmente en `docker-compose.yml` (desarrollo) y el directorio `backend/`.
   * **Stack:** Python (FastAPI), Celery, Nginx.
   * **Propósito:** Fue la prueba de concepto original para validar las ideas del proyecto. Contiene la integración inicial con la IA de Google. **No se usa en producción.**

2. **Producción Fase 1 (Nodo Único Fenix):**
   * **Ubicación:** `docker-compose.fenix.yml` y los directorios `sentinel-cortex/` y `services/neural-guard/`.
   * **Stack:** **Rust (Axum)**, Podman, Traefik. El backend de Python fue reemplazado por un binario nativo (`sentinel-cortex`).
   * **Propósito:** Es el **entorno de producción actual**. Un único servidor robusto que ejecuta el núcleo del sistema.

3. **Arquitectura Objetivo Fase 2 (Clúster Multi‑Nodo):**
   * **Ubicación:** Documentado en `docs/00_vision_y_arquitectura_global/`.
   * **Stack:** Se expandirá a un clúster de múltiples nodos (ej. Kingu, Centurion), posiblemente usando tecnologías de mesh‑networking como MycNet.
   * **Propósito:** Es la **visión a futuro del proyecto**, buscando una computación distribuida y de alta disponibilidad.

---

## El Problema: La Deriva del Punto Flotante

IEEE 754 (el estándar para números de punto flotante) tiene problemas de precisión con fracciones comunes en sistemas binarios, como `1/3`, `1/6`, `1/12` y `1/60`. Estas se convierten en números periódicos que acumulan errores de redondeo en cadenas de cálculo largas.

La Base‑60 (sexagesimal), usada por los astrónomos babilonios durante 2 000 años, es divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20 y 30. Esto permite que esas fracciones sean **exactas**. Sentinel explora cómo implementar esta robustez matemática en el software de sistemas moderno.

---

## Resultados de Benchmarks

### Eficiencia de Memoria (EXP‑015)

| Implementación | Memoria por nodo | Throughput | Capacidad en 11 GB RAM |
|---|---|---|---|
| Python sparse lattice | ~377 bytes | ~0.04 M nodos/s | ~0.4 GB payload |
| **Rust S60 nativo** | **16.00 bytes** | **~120 M nodos/s** | **~10 GB payload** |
| **Factor** | **23.6× más pequeño** | **~3 000× más rápido** | **25× más** |

### Equivalencia Numérica (EXP‑021/022)

Comparación de S60 vs. f64 con 1 000 señales y 300 muestras:

| Métrica | Divergencia Media (Lyapunov) | Divergencia Media (Shannon) |
|---|---|---|
| S60 vs f64 | **< 0.0001** | **< 0.0001** |

S60 demuestra ser numéricamente equivalente a f64 para procesamiento de señales, pero eliminando la representación de punto flotante.

---

## Arquitectura Actual (Fenix)

```
sentinel/
├── sentinel-cortex/   Rust Cortex — 🛡️ Servidor Axum, API y motor de decisiones.
├── services/
│   └── neural-guard/  (Legacy) Lógica de defensa ahora integrada en Cortex.
├── ebpf/              Hooks de Kernel — Interceptación de syscalls, bloqueo de floats.
├── quantum/           Capa de Python vía PyO3 (me60os_core.so, zero-copy).
├── observability/     Prometheus + Grafana (métricas con conciencia térmica).
└── constraints/       YATRA_SPEC.md — El contrato inmutable de la aritmética.
```

### 🧠 Neural Guard y Acoplamiento Octomecánico

Sentinel integra el **Acoplamiento Octomecánico**:

- **Conciencia Térmica**: El sistema consulta la temperatura de la CPU en tiempo real.
- **Umbrales Dinámicos**: Las alertas de seguridad se ajustan basadas en la **Masa Computacional** del sistema (carga efectiva). Entornos más "calientes" (con más carga/entropía) se vuelven menos sensibles para evitar falsos positivos.

---

## Inicio Rápido (Desarrollo)

```bash
# Construir el núcleo de Rust
cd sentinel-cortex && cargo build --release

# Construir la extensión PyO3 (requiere el repo me-60os)
cd ../me-60os && cargo build --release --features extension-module
cp target/release/libme60os_core.so ../sentinel/quantum/

# Ejecutar benchmarks (desde el directorio sentinel/quantum)
python3 experiments/EXP_015_MEMORY_THROUGHPUT.py
python3 experiments/EXP_022_ENTROPY_VALIDATION.py
```

---

## El Contrato YATRA

**No usar `f32` ni `f64` en la lógica de base‑60.** Esta regla es reforzada a nivel de kernel por ganchos de eBPF que pueden detectar y bloquear syscalls "contaminados" con punto flotante.

---

## Hoja de Ruta

- [x] **Soberanía Fenix**: Transición a orquestador de nodo único con Podman.
- [x] **Neural Guard (Rust)**: Despliegue del nuevo motor de decisiones seguro.
- [x] **Acoplamiento Octomecánico**: Sensibilidad dinámica basada en la temperatura de la CPU.
- [x] **Ring 0**: Hooks de eBPF para detectar contaminación de punto flotante.
- [x] **Puente PyO3**: Acceso desde Python al núcleo Rust sin sobrecarga de serialización.
- [x] Stack de observabilidad con Prometheus + Grafana.
- [ ] **MycNet**: Computación S60 distribuida entre nodos de una malla.
- [ ] **Prueba de Equivalencia Formal**: Demostración matemática de S60 como una clase de equivalencia a IEEE 754.

---

## Licencia

Apache 2.0 — ver [LICENSE](./LICENSE)