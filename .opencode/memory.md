# Memoria persistente del proyecto Sentinel (ITIL + ISO)

## Contexto actual
- **Objetivo**: Traducir toda la documentación al español y mantener la gobernanza ITIL/ISO.
- **Última decisión** (2026‑07‑25): crear `governance/` y `.opencode/memory.md`; usar skill *load‑memory* al iniciar.

## Estructura de gobernanza (resumen)
- **Service Strategy** → `governance/itil/service-strategy.md`
- **Service Design**   → `governance/itil/service-design.md`
- **Service Transition** → `governance/itil/service-transition.md`
- **Service Operation** → `governance/itil/service-operation.md`
- **CSI**               → `governance/itil/continual-service-improvement.md`
- **ISO 20000‑1**       → `governance/iso/iso20000-1.md`
- **ISO 27001**         → `governance/iso/iso27001-controls.md`
- **ISO 9001**          → `governance/iso/iso9001-quality.md`

## Traducción EN → ES
- Backlog maestro: `ENGLISH_MD_LIST.md` (lista de 100+ markdowns con idioma probable).
- Memoria de opencode: este archivo (`.opencode/memory.md`).
- Prioridad actual: traducir documentos “core” (README, CLAUDE, CONTRIBUTING, RESEARCH, YATRA_SPEC, EXPERIMENTS, etc.).

## Próximos pasos acordados
1. Traducir `README.md` → `README_es.md`
2. Traducir `CLAUDE.md` → `CLAUDE_es.md`
3. Generar script de traducción por lotes (Argos‑Translate / LibreTranslate) para el resto de `*.md` marcados como **Inglés** en `ENGLISH_MD_LIST.md`.