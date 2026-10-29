# CLAUDE.md — Guía de Contribución a Sentinel

> Este archivo proporciona contexto del código base a los asistentes de IA.

> **⚠ LECTURA OBLIGATORIA — Fundamento científico:**
> [`sentinel-scientific-foundation.md`](file:///home/jnovoas/.config/Code/User/workspaceStorage/7c63ffead990815376933d02c94d88c9/GitHub.copilot-chat/memory-tool/memories/repo/sentinel-scientific-foundation.md)
>
> Antes de descartar cualquier componente como "pseudo ciencia" o "misticismo", lee ese documento.
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
    sentinel-verifier  Verificador de invariantes runtime (OpenRC `--watch 15 --json`)
    services/neural-guard  Correlación de eventos + playbooks n8n; motor parcial
    ebpf/               Hooks LSM/kernel: guardian_alpha_lsm.c (ACTIVO), guardian_cognitive,
                        float_detector, gamma_watchdog; ai_guardian.c DESACTIVADO
    quantum/            LEGADO: .py con headers LEGACY BRIDGE / MIGRADO — estudio,
                        incluye experiments/ EXP-001..EXP-035 preservados
    observability/      Dashboards Prometheus + Grafana
    constraints/        YATRA_SPEC.md — el contrato aritmético inmutable

## Stack Tecnológico (entorno actual Debian, despliegue Kingu/Fenix)

| Capa | Tecnología |
|------|-----------|
| Sistema operativo host | Debian 13 |
| Rama | `main` para el entorno Debian/systemd; `alpine_fenix` corresponde a otro entorno. No mezclar configuraciones entre ambos. |
| Daemons nativos | systemd |
| Contenedores | Docker Compose; solo los contenedores que lo requieran deben usar imágenes Alpine. |
| Proxy TLS | Nginx + Let's Encrypt |
| Tipos base | Rust: SPA `[i64;5]` escala 60⁴=12,960,000; S60 `i64` |
| Refuerzo kernel | eBPF / hooks LSM + XDP/TC, solo con aprobación y preflight de recuperación |
| IPC | Memoria compartida POSIX en `/dev/shm` |
| Observabilidad | Prometheus + Grafana + Loki + Promtail |

Para la operación actual, el alcance autorizado es Kingu; no modificar Fenix salvo solicitud explícita.

El workspace incluye `soma_orchestrator` y `soma_worker` como WIP; no forman
parte del arranque operativo. `neural-guard` se ejecuta en Compose con el motor
de correlación todavía parcial.
## El Candado YATRA — Regla No Negociable

**NUNCA usar f32, f64, ni ningún tipo de punto flotante en lógica base‑60.**

Esta regla existe porque una sola operación float puede contaminar una cadena de cómputo entera.
La capa eBPF detecta y bloquea patrones de syscalls float en tiempo de ejecución.

Si necesitas logaritmos o funciones trascendentales: usa las implementaciones S60 por serie de Taylor
en sentinel‑cortex/src/math/. Si aún no existe la que necesitas, abre un issue — no uses floats.

Antes de adjuntar Guardian/eBPF en Kingu, poblar y verificar la whitelist de ejecutables y rutas críticas de recuperación. El bootstrap actual valida la whitelist antes de adjuntar en modo auditoría y no ofrece modo solo-poblar. Confirmar consola de proveedor/recuperación fuera de banda antes de ejecutarlo; enforcement requiere autorización explícita separada.

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
- Producción actual: un solo nodo `fenix` (Alpine/OpenRC/Docker Compose) hasta terminar este servidor e instalar el otro. No contratar datacenter ni añadir nodos mientras tanto. No asumir la topología histórica Fenix/Kingu.
- Experimentos con numeración secuencial; EXP‑023/024/025 restaurados 2026‑07‑30
- `internal/` está en .gitignore — el trabajo exploratorio vive ahí
- Todo documento nuevo o actualizado debe agregarse a la cola de traducción (ver `ENGLISH_MD_LIST.md`)

## Conocimiento del Código y Navegación (graphify)

Este proyecto cuenta con soporte de grafo de conocimiento local mediante **graphify**.

### Reglas de consulta e interacción:
- Si existe `graphify-out/graph.json`, ejecuta `graphify query "<pregunta>"` antes de realizar búsquedas textuales masivas (`grep`/`find`).
- Utiliza `graphify path "<A>" "<B>"` para rastrear dependencias o relaciones entre dos módulos o componentes.
- Utiliza `graphify explain "<concepto>"` para explicaciones enfocadas de nodos y su vecindario arquitectónico.
- Si existe `graphify-out/wiki/index.md` o `graphify-out/GRAPH_REPORT.md`, consúltalos para navegación arquitectónica global.
- Tras realizar cambios importantes en el código, ejecuta `graphify update .` para mantener el grafo sincronizado (análisis AST local sin consumo de tokens de API).
- Para construir o reconstruir el grafo completo, utiliza el comando `/graphify .`.
