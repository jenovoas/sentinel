# CLAUDE.md — Guía de Contribución a Sentinel

> Este archivo proporciona contexto del código base a los asistentes de IA.

## Qué es Sentinel

Sentinel es un framework de sistemas de bajo nivel construido sobre **aritmética sexagesimal (base‑60)** y eBPF.
La idea central: el punto flotante IEEE 754 introduce errores sistemáticos de redondeo en fracciones cuyos
denominadores incluyen primos que no dividen a 2 (1/3, 1/6, 1/60 son no terminales en binario).
La base‑60 es divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — estas fracciones son **exactas**.

Sentinel implementa esto a nivel kernel: hooks eBPF refuerzan la pureza aritmética, Rust proporciona
el sistema de tipos zero‑copy, y PyO3 expone el núcleo a Python sin sobrecarga.

## Arquitectura

    sentinel/
    sentinel-cortex/   Núcleo Rust: tipos S60/U60, IPC, refuerzo en Anillo 0
      src/math/        Aritmética entera pura (suma, resta, mult, div, cmp)
    ebpf/              Hooks LSM: intercepción de syscalls, detección de contaminación float
    quantum/           Capa Python vía PyO3 (me60os_core.so)
      experiments/     Programa experimental numerado (EXP-001 a EXP-029)
    agents/            Agentes modulares: Investigación, Verificador, Publicador, Memoria
    observability/     Dashboards Prometheus + Grafana
    constraints/       YATRA_SPEC.md — el contrato aritmético inmutable

## Stack Tecnológico (SERVIDOR FENIX — Solo CPU)

| Capa | Tecnología |
|------|-----------|
| Tipos base | Rust (struct S60 empaquetado con repr(packed), 16 bytes) |
| Refuerzo kernel | eBPF / hooks LSM |
| Puente Python | PyO3 — zero‑copy, sin serialización |
| IPC | Memoria compartida /dev/shm (6× más rápida que IPC serializado) |
| Observabilidad | Prometheus + Grafana |
| Contenedores | Podman (rootless) |
| Inferencia IA | Ollama solo‑CPU (modelo phi3:mini) |

## El Candado YATRA — Regla No Negociable

**NUNCA usar f32, f64, ni ningún tipo de punto flotante en lógica base‑60.**

Esta regla existe porque una sola operación float puede contaminar una cadena de cómputo entera.
La capa eBPF detecta y bloquea patrones de syscalls float en tiempo de ejecución.

Si necesitas logaritmos o funciones trascendentales: usa las implementaciones S60 por serie de Taylor
en sentinel‑cortex/src/math/. Si aún no existe la que necesitas, abre un issue — no uses floats.

## Compilación

    # Construir núcleo Rust
    cd sentinel-cortex && cargo build --release

    # Construir extensión PyO3 (me-60os)
    cd ../me-60os && cargo build --release --features extension-module
    cp target/release/libme60os_core.so ../sentinel/quantum/

    # Ejecutar experimentos
    cd sentinel/quantum && python3 experiments/EXP_022_ENTROPY_VALIDATION.py

## Restricciones Clave

- Prohibidos floats en lógica S60 (Candado YATRA)
- Prohibidas nuevas VMs o instancias cloud: todos los servicios despliegan como contenedores Podman en un solo nodo
- Los experimentos siguen numeración secuencial. EXP‑023/024/025 son parte del registro
  de investigación. Estaban temporalmente ausentes del repositorio; restaurados 2026‑07‑30.
- internal/ está en .gitignore: la investigación exploratoria vive ahí, no en el árbol principal

## Por Dónde Empezar

- constraints/YATRA_SPEC.md: el contrato aritmético que gobierna todas las decisiones
- sentinel-cortex/src/math/: la implementación base del tipo S60
- quantum/experiments/EXP_015_MEMORY_THROUGHPUT.py: benchmark (reducción de memoria 23.6×)
- docs/RESEARCH_es.md: narrativa científica del programa experimental

## Gobernanza (ITIL 4 / ISO 20000‑1 / ISO 27001)

- `governance/itil/service-strategy.md` – Estrategia de Servicio
- `governance/itil/service-design.md` – Diseño de Servicio
- `governance/iso27001/statement-of-applicability.md` – SoA
- `governance/iso20000/service-management-system.md` – SMS
- `governance/iso27001/risk-treatment-plan.md` – RTP
- `governance/policies/information-security-policy.md` – Política de Seguridad de la Información
- `governance/policies/access-control-policy.md` – Control de Acceso
- `governance/policies/incident-management-policy.md` – Gestión de Incidentes
- `governance/policies/change-management-policy.md` – Gestión de Cambios
- `governance/compliance/matrix.md` – Matriz de cumplimiento
- `governance/compliance/evidence-index.md` – Índice de evidencias
- `governance/compliance/internal-audit-plan.md` – Plan de auditoría interna
- `governance/compliance/management-review-agenda.md` – Agenda de revisión por la dirección
- `governance/kpi/dashboard.md` – Panel de KPI
- `governance/continuous-improvement/kaizen-log.md` – Bitácora Kaizen

## Iniciativa de Traducción (Inglés → Español)

- Lista maestra de archivos Markdown con idioma detectado: `ENGLISH_MD_LIST.md`
- Memoria Opencode (auto‑actualizada): `.opencode/memory.md`
- Prioridad actual: traducir primero los documentos "núcleo" (README, CLAUDE, CONTRIBUTING, RESEARCH,
  YATRA_SPEC, EXPERIMENTS, etc.)

## Restricciones Clave (actualizado)

- Prohibidos floats en lógica S60 (Candado YATRA)
- Prohibidas nuevas VMs / instancias cloud — todo corre como contenedores Podman rootless en el único nodo FENIX
- Experimentos con numeración secuencial; EXP‑023/024/025 restaurados 2026‑07‑30
- `internal/` está en .gitignore — el trabajo exploratorio vive ahí
- Todo documento nuevo o actualizado debe agregarse a la cola de traducción (ver `ENGLISH_MD_LIST.md`)
