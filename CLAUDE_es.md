# CLAUDE.md — Guía del Contribuyente de Sentinel

> Este archivo brinda a los asistentes de codificación con IA contexto sobre la base de código de Sentinel.

## ¿Qué es Sentinel?

Sentinel es un marco de sistemas de bajo nivel construido sobre **aritmética sexagesimal (base‑60)** y eBPF.
La idea central: IEEE 754 de punto flotante introduce errores sistemáticos de redondeo para fracciones con denominadores que incluyen primos que no dividen a 2 (1/3, 1/6, 1/60 no terminan en binario).
La base‑60 es divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — esas fracciones son **exactas**.

Sentinel implementa esto a nivel de kernel: *hooks* eBPF fuerzan la pureza aritmética, Rust provee el sistema de tipos *zero‑copy*, y PyO3 expone el núcleo a Python sin sobrecarga.

## Arquitectura

    sentinel/
    sentinel-cortex/   Núcleo Rust: tipos S60/U60, IPC, imposición Ring 0
      src/math/        Aritmética de enteros puros (add, sub, mul, div, cmp)
    ebpf/              Hooks LSM: intercepción de syscalls, detección de contaminación float
    quantum/           Capa Python vía PyO3 (me60os_core.so)
      experiments/     Programa experimental numerado (EXP‑001 a EXP‑029)
    agents/            Agentes modulares: Research, Verifier, Publisher, Memory
    observability/     Prometheus + Grafana dashboards
    constraints/       YATRA_SPEC.md — el contrato inmutable de la aritmética

## Pila Tecnológica (SERVIDOR FENIX — Solo CPU)

| Capa | Tecnología |
|------|-----------|
| Tipos base | Rust (`repr(packed)` struct S60, 16 bytes) |
| Imposición kernel | eBPF / LSM hooks |
| Puente Python | PyO3 — zero‑copy, sin serialización |
| IPC | /dev/shm memoria compartida (6× más rápido que IPC serializado) |
| Observabilidad | Prometheus + Grafana |
| Runtime contenedores | Podman (rootless) |
| Inferencia IA | Ollama solo CPU (modelo phi3:mini) |

## El Bloqueo YATRA — Regla Innegociable

**NUNCA usar `f32`, `f64` ni ningún tipo de punto flotante en lógica base‑60.**

Esta regla existe porque una sola operación *float* puede contaminar una cadena de cómputo completa.
La capa eBPF detecta y bloquea patrones de syscall con punto flotante en tiempo de ejecución.

Si necesitas logaritmos o funciones trascendentes: usa las implementaciones de series de Taylor S60 en `sentinel-cortex/src/math/`. Si no existe aún, abre un *issue* — no uses floats.

## Compilación

    # Compilar núcleo Rust
    cd sentinel-cortex && cargo build --release

    # Compilar extensión PyO3 (me‑60os)
    cd ../me-60os && cargo build --release --features extension-module
    cp target/release/libme60os_core.so ../sentinel/quantum/

    # Ejecutar experimentos
    cd sentinel/quantum && python3 experiments/EXP_022_ENTROPY_VALIDATION.py

## Restricciones Clave

- Sin floats en lógica S60 (Bloqueo YATRA arriba).
- No nuevas VMs ni instancias cloud: todos los servicios se despliegan como contenedores Podman en un solo nodo.
- Experimentos numerados secuencialmente: EXP‑023/024/025 omitidos intencionalmente (sustituidos durante la migración *zero‑float*, commit 2bfde153).
- `internal/` está en `.gitignore`: trabajo exploratorio vive ahí, no en el árbol principal.

## Dónde Empezar

- `constraints/YATRA_SPEC.md`: el contrato aritmético que rige todas las decisiones.
- `sentinel-cortex/src/math/`: implementación base del tipo S60.
- `quantum/experiments/EXP_015_MEMORY_THROUGHPUT.py`: benchmark (reducción 23.6× de memoria).
- `RESEARCH.md`: narrativa científica del programa experimental.

## Gobernanza (ITIL 4 / ISO 20000‑1 / ISO 27001)

- `governance/itil/service-strategy.md` – Estrategia del Servicio
- `governance/itil/service-design.md` – Diseño del Servicio
- `governance/iso27001/statement-of-applicability.md` – SoA
- `governance/iso20000/service-management-system.md` – SMS
- `governance/iso27001/risk-treatment-plan.md` – Plan de Tratamiento de Riesgos
- `governance/policies/information-security-policy.md` – Política de Seguridad de la Información
- `governance/policies/access-control-policy.md` – Control de Acceso
- `governance/policies/incident-management-policy.md` – Gestión de Incidentes
- `governance/policies/change-management-policy.md` – Gestión de Cambios
- `governance/compliance/matrix.md` – Matriz de Cumplimiento
- `governance/compliance/evidence-index.md` – Índice de Evidencias
- `governance/compliance/internal-audit-plan.md` – Plan de Auditoría Interna
- `governance/compliance/management-review-agenda.md` – Agenda de Revisión de Dirección
- `governance/kpi/dashboard.md` – Panel de KPIs
- `governance/continuous-improvement/kaizen-log.md` – Registro Kaizen

## Iniciativa de Traducción (Inglés → Español)

- Listado maestro de todos los Markdown con su idioma: `ENGLISH_MD_LIST.md`
- Memoria de Opencode (auto‑actualizada): `.opencode/memory.md`
- Prioridad actual: traducir primero los documentos “core” (README, CLAUDE, CONTRIBUTING, RESEARCH, YATRA_SPEC, EXPERIMENTS, etc.)

## Restricciones Clave (actualizadas)

- Sin floats en lógica S60 (Bloqueo YATRA).
- Sin nuevas VMs / instancias cloud — todo corre como contenedores Podman rootless en el único nodo FENIX.
- Experimentos numerados secuencialmente; EXP‑023/024/025 omitidos a propósito.
- `internal/` está en `.gitignore` — trabajo exploratorio vive ahí.
- Toda documentación nueva/actualizada debe agregarse al backlog de traducción (ver `ENGLISH_MD_LIST.md`).