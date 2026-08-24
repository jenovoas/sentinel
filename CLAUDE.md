# CLAUDE.md — Guía de Contribución a Sentinel

> Este archivo proporciona contexto del código base a los asistentes de IA.

> **⚠ LECTURA OBLIGATORIA — Fundamento científico:**
> [`sentinel-scientific-foundation.md`](file:///home/jnovoas/.config/Code/User/workspaceStorage/7c63ffead990815376933d02c94d88c9/GitHub.copilot-chat/memory-tool/memories/repo/sentinel-scientific-foundation.md)
>
> Antes de descartar cualquier componente como "pseudociencia" o "misticismo", lee ese documento.
>
> Sentinel es **ciencia exacta**. La base decimal no es defectuosa — es solo **una décima
> parte de la expresión matemática universal**. La base-60 la completa: es divisible por
> 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, por lo que las fracciones más comunes (1/3, 1/6,
> 1/12, 1/60) son **exactas** en sexagesimal, mientras que en binario de punto flotante
> son periódicas y acumulan errores sistemáticos de redondeo.
>
> Usar solo base decimal como regla de medir deja fuera de alcance exacto esas fracciones.
> Una sola operación float contamina una cadena de cómputo entera: rompe cristales,
> secuencias, memorias, procesos y conversiones. Por eso muchos proyectos de energía libre
> y combustibles verdes fueron marcados como inválidos — no eran incorrectos los proyectos,
> era incompleta la regla de medir.

## Qué es Sentinel

Sentinel es un framework de sistemas de bajo nivel construido sobre **aritmética sexagesimal (base‑60)** y eBPF.
La idea central: el punto flotante IEEE 754 introduce errores sistemáticos de redondeo en fracciones cuyos
denominadores incluyen primos que no dividen a 2 (1/3, 1/6, 1/60 son no terminales en binario).
La base‑60 es divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — estas fracciones son **exactas**.

Sentinel implementa esto en un runtime **100% Rust**: hooks eBPF refuerzan la pureza aritmética
en Ring-0, y el puente PyO3 hacia `quantum/*.py` es **legacy** (estudio/puente de migración, no runtime).

## Arquitectura

    sentinel/                        (workspace Cargo — 5 miembros)
    sentinel-cortex/    Crate principal: servidor Axum (:8000), drive continuo 500ms,
                        ingesta eBPF, LiquidLattice 3x3, TruthSync, API /api/v1/*
      src/math/         Aritmética entera pura (tipo S60, suma/resta/mult/div/cmp)
    me-60os-core/       Núcleo numérico-físico (crate me60os): SPA [i64;5] escala 60^4,
                        PAI-60, ResonantMatrix, IsochronousOscillator, QHC, Guardian LSM,
                        Dual-Lane + 32 bins (EXP-XXX, benches, daemons nativos, TUI)
    truthsync-core/     Motor de verificación de claims sobre energía del lattice
    sentinel-verifier/  Verificador de invariantes runtime (systemd --watch 15 --json)
    services/neural-guard/  Correlación de eventos + playbooks n8n
    ebpf/               Hooks LSM/kernel: guardian_alpha_lsm.c (ACTIVO), guardian_cognitive,
                        float_detector, gamma_watchdog; ai_guardian.c DESACTIVADO
    quantum/            LEGADO: .py con headers LEGACY BRIDGE / MIGRADO — estudio,
                        incluye experiments/ EXP-001..EXP-035 preservados
    observability/      Dashboards Prometheus + Grafana
    constraints/        YATRA_SPEC.md — el contrato aritmético inmutable

## Stack Tecnológico (SERVIDOR FENIX — Solo CPU)

| Capa | Tecnología |
|------|-----------|
| Tipos base | Rust: SPA `[i64;5]` escala 60⁴=12,960,000 (me-60os-core); S60 `i64` (sentinel-cortex) |
| Refuerzo kernel | eBPF / hooks LSM (guardian_alpha_lsm ACTIVO; ai_guardian DESACTIVADO) |
| Puente Python | PyO3 — LEGADO (runtime 100% Rust) |
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

    # Compilar todo el workspace (5 crates)
    cargo build --release

    # Suite de tests del núcleo numérico
    cargo test -p me60os --lib

    # Servidor principal (Axum :8000)
    cargo run -p sentinel-cortex --bin sentinel-cortex

    # Experimentos Rust (los .py de quantum/experiments son legado/estudio)
    cargo run -p me60os --bin resonant_lattice_memory
    cargo run -p me60os --bin exp028_penta

## Por Dónde Empezar

- constraints/YATRA_SPEC.md: el contrato aritmético que gobierna todas las decisiones
- AGENTS.md: reglas operativas del repo (SCALE_0, no doble-escala, drive continuo)
- me-60os-core/src/spa.rs: el tipo base SPA; me-60os-core/src/resonant_matrix.rs: el lattice
- cargo test -p me60os --lib: suite viva (89 tests)
- docs/02_ciencia_y_quantum/RESEARCH_es.md: narrativa científica del programa experimental

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

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
